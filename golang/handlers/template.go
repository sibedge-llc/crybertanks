package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"signalr/signalr"
)

type templateHandler struct {
	onStart func()
	invoke  signalr.HandlerFunc
}

func NewTemplateHandler(onStart func(), invoke signalr.HandlerFunc) *templateHandler {
	return &templateHandler{
		onStart: onStart,
		invoke:  invoke,
	}
}

func (th *templateHandler) Handle(ctx context.Context, target string, args []json.RawMessage) error {
	fmt.Println(target, args)
	switch target {
	case "requestArrangement":
		return th.invoke(ctx, "ReceiveArrangement", defaultField())
	case "requestStep":
		return th.invoke(ctx, "ReceiveStep", 1, 0)
	}
	return nil
}

func (th *templateHandler) OnStart() {
	th.onStart()
}

func defaultField() [][]int {
	var field [][]int
	field = append(field, []int{1, 0, 0, 1, 0, 0, 0, 0, 1, 1})
	field = append(field, []int{1, 0, 0, 1, 0, 0, 0, 0, 0, 0})
	field = append(field, []int{0, 0, 0, 0, 0, 0, 0, 0, 0, 0})
	field = append(field, []int{0, 1, 0, 0, 0, 0, 1, 1, 0, 0})
	field = append(field, []int{0, 1, 0, 0, 0, 0, 0, 0, 0, 0})
	field = append(field, []int{0, 0, 0, 0, 0, 0, 0, 1, 1, 0})
	field = append(field, []int{0, 0, 0, 1, 1, 0, 0, 0, 0, 0})
	field = append(field, []int{0, 1, 0, 0, 0, 0, 0, 0, 0, 0})
	field = append(field, []int{0, 1, 0, 1, 0, 1, 0, 0, 0, 0})
	field = append(field, []int{0, 0, 0, 1, 0, 1, 0, 0, 0, 0})
	return field
}
