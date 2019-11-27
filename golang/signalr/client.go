package signalr

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	"nhooyr.io/websocket"
)

type (
	// Client represents a bidirectional connection to SignalR (.Net Core 3.0 Compatible).
	Client struct {
		name    string
		hubName string
		connID  string
		connURL *url.URL
		conn    *websocket.Conn

		sync.RWMutex
	}

	ClientOption func(*Client) error

	negotiateResponse struct {
		ConnectionID        string      `json:"connectionId,omitempty"`
		AvailableTransports []transport `json:"availableTransports"`
	}

	transport struct {
		Name    string   `json:"transport,omitempty"`
		Formats []string `json:"transportFormats,omitempty"`
	}

	transportTypes string

	handshakeRequest struct {
		Protocol string `json:"protocol"`
		Version  int    `json:"version"`
	}

	handshakeResponse struct {
		Error string `json:"error,omitempty"`
	}

	messageType int

	// InvocationMessage is the structure expected for sending and receiving in the SignalR protocol.
	InvocationMessage struct {
		Type         messageType       `json:"type,omitempty"`
		Headers      map[string]string `json:"headers,omitempty"`
		InvocationID string            `json:"invocationId,omitempty"`
		Target       string            `json:"target"`
		Arguments    []json.RawMessage `json:"arguments"`
		Error        string            `json:"error,omitempty"`
	}
)

const (
	messageTerminator byte = 0x1E

	invocationMessageType messageType = iota
	streamItemMessageType
	completionMessageType
	streamInvocationMessageType
	cancelInvocationMessageType
	pingMessageType
	closeMessageType
)

var (
	websocketTransportType transportTypes = "WebSockets"
)

func WithName(name string) ClientOption {
	return func(client *Client) error {
		client.name = name
		return nil
	}
}

func NewClient(connStr string, hubName string, opts ...ClientOption) (*Client, error) {
	connURL, err := url.Parse(connStr)
	if err != nil {
		return nil, err
	}

	client := &Client{
		hubName: hubName,
		connURL: connURL,
	}

	for _, opt := range opts {
		if err := opt(client); err != nil {
			return client, err
		}
	}

	return client, nil
}

func (c *Client) Listen(ctx context.Context, handler Handler) error {
	err := c.negotiateOnce(ctx)
	if err != nil {
		return err
	}

	conn, resp, err := websocket.Dial(ctx, c.getWssURI(), nil)
	if resp != nil {
		defer resp.Body.Close()
	}

	if err != nil {
		return err
	}

	err = c.handshake(ctx, conn)
	if err != nil {
		return err
	}

	select {
	case <-ctx.Done():
	default:
		c.conn = conn

		if h, ok := handler.(Handler); ok {
			h.OnStart()
		}

		for {
			bits, err := readConn(ctx, conn)
			if err != nil {
				if err.Error() == "failed to get reader: context canceled" {
					return nil
				}
				return err
			}

			var msg InvocationMessage
			err = json.Unmarshal(bits, &msg)
			if err != nil {
				return err
			}

			switch msg.Type {
			case pingMessageType:
			case invocationMessageType:
				return dispatch(ctx, handler, &msg)
			case streamInvocationMessageType, streamItemMessageType, cancelInvocationMessageType, completionMessageType:
				return errors.New("unhandled InvocationMessage type: " + string(msg.Type))
			case closeMessageType:
				return conn.Close(websocket.StatusNormalClosure, "received close message from SignalR service")
			}
		}
	}

	return nil
}

func (c *Client) SendInvocation(ctx context.Context, target string, args ...interface{}) error {
	jsonArgs := make([]json.RawMessage, len(args))
	for i := 0; i < len(args); i++ {
		bits, err := json.Marshal(args[i])
		if err != nil {
			return err
		}
		jsonArgs[i] = bits
	}

	bits, err := json.Marshal(&InvocationMessage{
		Type:      invocationMessageType,
		Target:    target,
		Arguments: jsonArgs,
	})
	if err != nil {
		return err
	}

	wrCloser, err := c.conn.Writer(ctx, websocket.MessageText)
	if err != nil {
		return err
	}

	_, err = wrCloser.Write(append(bits, messageTerminator))
	if err != nil {
		return err
	}

	if err := wrCloser.Close(); err != nil {
		return err
	}

	return nil
}

func (c *Client) Name() string {
	return c.name
}

func readConn(ctx context.Context, conn *websocket.Conn) ([]byte, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	_, reader, err := conn.Reader(ctx)
	if err != nil {
		return nil, err
	}

	bits, err := ioutil.ReadAll(reader)
	if err != nil {
		return nil, err
	}

	if bits[len(bits)-1] == messageTerminator {
		bits = bits[0 : len(bits)-1]
	}

	return bits, nil
}

func (c *Client) handshake(ctx context.Context, conn *websocket.Conn) error {
	hsReq := handshakeRequest{
		Protocol: "json",
		Version:  1,
	}

	bits, err := json.Marshal(hsReq)
	if err != nil {
		return err
	}

	wrCloser, err := conn.Writer(ctx, websocket.MessageText)
	if err != nil {
		return err
	}

	_, err = wrCloser.Write(append(bits, messageTerminator))
	if err != nil {
		return err
	}

	if err := wrCloser.Close(); err != nil {
		return err
	}

	_, resp, err := conn.Reader(ctx)
	if err != nil {
		return err
	}

	bits, err = ioutil.ReadAll(resp)
	if err != nil {
		return err
	}

	if bits[len(bits)-1] == messageTerminator {
		bits = bits[0 : len(bits)-1]
	}

	var hsRes handshakeResponse
	if err := json.Unmarshal(bits, &hsRes); err != nil {
		return err
	}

	if hsRes.Error != "" {
		return errors.New(hsRes.Error)
	}
	return nil
}

func (c *Client) getWssURI() string {
	wssURI := strings.Replace(c.getURI(), "https://", "wss://", 1) + "?id=" + c.connID
	return wssURI
}

func (c *Client) getURI() string {
	URI := c.connURL.String() + "/" + c.hubName
	return URI
}

func (c *Client) negotiateOnce(ctx context.Context) error {
	c.Lock()
	defer c.Unlock()

	if c.connID == "" {
		res, err := c.negotiate(ctx)
		if err != nil {
			return err
		}

		found := false
		for _, tr := range res.AvailableTransports {
			if tr.Name == string(websocketTransportType) {
				found = true
				break
			}
		}

		if !found {
			return errors.New("WebSockets transport is not supported by the service")
		}

		c.connID = res.ConnectionID
	}

	return nil
}

func (c *Client) negotiate(ctx context.Context) (*negotiateResponse, error) {
	negotiateURI := c.getURI() + "/negotiate"
	req, err := http.NewRequest(http.MethodPost, negotiateURI, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.WithContext(ctx)
	client := newHTTPClient()
	res, err := client.Do(req)
	if res != nil {
		defer res.Body.Close()
	}

	if err != nil {
		return nil, err
	}

	bodyBits, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	if res.StatusCode >= http.StatusBadRequest {
		return nil, errors.New(res.Status)
	}

	var negRes negotiateResponse
	err = json.Unmarshal(bodyBits, &negRes)
	if err != nil {
		return nil, err
	}

	return &negRes, nil
}

func newHTTPClient() *http.Client {
	tr := &http.Transport{
		MaxIdleConnsPerHost: 10,
		TLSClientConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
	}

	return &http.Client{
		Transport: tr,
	}
}
