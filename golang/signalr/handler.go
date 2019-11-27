package signalr

import (
	"context"
	"encoding/json"
	"fmt"
	"reflect"
)

// Handler for receiving SignalR invocations.
type Handler interface {
	Handle(ctx context.Context, target string, args []json.RawMessage) error
	OnStart()
}

type HandlerFunc func(context.Context, string, ...interface{}) error

func dispatch(ctx context.Context, handler Handler, msg *InvocationMessage) error {
	t := reflect.TypeOf(handler)
	if method, ok := t.MethodByName(msg.Target); ok {
		mt := method.Type
		numIn := mt.NumIn()
		if numIn == len(msg.Arguments)+2 && method.Name != "Default" {
			args := make([]reflect.Value, mt.NumIn()-1)
			args[0] = reflect.ValueOf(ctx)
			for i := 0; i < len(msg.Arguments); i++ {
				argType := mt.In(i + 2)
				newArg := reflect.New(argType)
				newArgPtr := newArg.Interface()
				err := json.Unmarshal(msg.Arguments[i], &newArgPtr)
				if err != nil {
					return handler.Handle(ctx, msg.Target, msg.Arguments)
				}

				args[i+1] = newArg.Elem()
			}

			actualTarget := reflect.ValueOf(handler).MethodByName(msg.Target)
			returns := actualTarget.Call(args)
			if len(returns) == 0 {
				return nil
			}

			if returns[0].IsNil() {
				return nil
			}

			if val, ok := returns[0].Elem().Interface().(error); ok {
				return val
			}

			fmt.Printf("didn't know how to deal with: %+v", returns)
			return nil
		}
	}

	return handler.Handle(ctx, msg.Target, msg.Arguments)
}
