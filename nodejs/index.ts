import { HubConnectionBuilder } from '@aspnet/signalr';

const url = 'https://cybertank.sibedge.com:5001/gameHub';

const connection = new HubConnectionBuilder()
  .withUrl(url)
  .build()
;

connection.start()
  .then(() => {
    console.log('started');
    return connection.invoke("Debug", "Hello")
  });

connection.on("requestArrangement", ()=> {
  console.log("requestArrangement requested");
  const board = [
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
  ];
  return connection.invoke("ReceiveArrangement", JSON.stringify(board)).then(() => console.log('Arrangement is sent'));
});

connection.on("requestStep", () =>
{
  console.log("step requested");
  return connection.invoke("ReceiveStep", 1, 0).then(() => console.log('Step is sent'));
});

connection.on("receiveMessage", (message) => console.log("received: " + message));
