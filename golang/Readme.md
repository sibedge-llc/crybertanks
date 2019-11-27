# Cybertank

## SignalR GO Client

Invocations:
* void Debug (string name)
* void Fight (string name)
* void ReceiveArrangement (string field), where (field) [][]int matrix 10x10 of 0 and 1, serialized as JSON
* void ReceiveStep(int x, int y), where (x и y) &gt;= 0 и &lt;= 9