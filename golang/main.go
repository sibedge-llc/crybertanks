// Author: tishine@sibedge.com

package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"signalr/handlers"
	"signalr/signalr"
)

var (
	connStr = flag.String("conn-str", "https://cybertank.sibedge.com:5001", "connection string")
	hubName = flag.String("hub-name", "gameHub", "SignalR hub name")
	name    = flag.String("name", "gobot", "bot name")
	debug   = flag.Bool("debug", true, "debug mode")
)

func main() {
	flag.Parse()

	client, err := signalr.NewClient(*connStr, *hubName, signalr.WithName(*name))
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	ctx, cancel := context.WithCancel(context.Background())

	start := make(chan struct{}, 1)
	defer close(start)

	handler := handlers.NewTemplateHandler(func() {
		start <- struct{}{}
	}, client.SendInvocation)

	go func() {
		err := client.Listen(ctx, handler)
		if err != nil {
			fmt.Println(err)
			start <- struct{}{}
			cancel()
		}
	}()
	<-start

	target := "Fight"
	if *debug {
		target = "Debug"
	}

	err = client.SendInvocation(ctx, target, client.Name())
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	<-ctx.Done()
	os.Exit(0)
}
