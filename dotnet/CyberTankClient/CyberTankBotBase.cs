namespace CyberTankClient
{
    using System;
    using System.Threading.Tasks;
    using Microsoft.AspNetCore.SignalR.Client;
    using Newtonsoft.Json;

    /// <summary>
    /// Базовый класс бота для игры.
    /// </summary>
    public abstract class CyberTankBotBase : IDisposable
    {
        private const short MaxStep = 9;
        private const short MinStep = 0;
        private readonly HubConnection connection;
        private readonly GameMode gameMode;
        private readonly string playerName;
        private readonly string serverUrl;

        /// <summary>
        /// ctor.
        /// </summary>
        /// <param name="serverUrl">URL сервера игры.</param>
        /// <param name="gameMode">Режим игры.</param>
        /// <param name="playerName">Имя игрока.</param>
        protected CyberTankBotBase(string serverUrl, GameMode gameMode, string playerName)
        {
            this.serverUrl = serverUrl;
            this.gameMode = gameMode;
            this.playerName = playerName;
            this.connection = new HubConnectionBuilder().WithUrl(this.serverUrl).Build();
        }

        /// <summary>
        /// Событие получения сообщения от сервера игры.
        /// </summary>
        public event Action<string> OnReceiveMessage;

        /// <inheritdoc/>
        public void Dispose()
        {
            this.connection.StopAsync();
            this.connection.DisposeAsync();
        }

        /// <summary>
        /// Запускает бота.
        /// </summary>
        /// <returns>Задание.</returns>
        public Task Start()
        {
            this.connection.On("requestArrangement",
                () =>
                {
                    short[,] arrangement = OnArrangementRequested();
                    SendArrangement(arrangement);
                });
            this.connection.On("requestStep",
                () =>
                {
                    (short x, short y) step = OnStepRequested();
                    SendStep(step.x, step.y);
                }
            );
            this.connection.On<string>("receiveMessage", MessageReceived);

            return this.connection.StartAsync().ContinueWith(
                task =>
                {
                    if (task.IsFaulted)
                    {
                        MessageReceived(task.Exception.GetBaseException().Message);
                    }
                    else
                    {
                        MessageReceived($"Подключено {this.serverUrl}");
                        StartGame();
                    }
                });
        }

        /// <summary>
        /// Обработчик запроса расстановки.
        /// </summary>
        protected abstract short[,] OnArrangementRequested();

        /// <summary>
        /// Обработчик запроса хода.
        /// </summary>
        protected abstract ( short x, short y ) OnStepRequested();

        /// <summary>
        /// Отправляет расстановку.
        /// </summary>
        /// <param name="board">Расстановка.</param>
        protected void SendArrangement(short[,] board)
        {
            this.connection.InvokeAsync("ReceiveArrangement", JsonConvert.SerializeObject(board));
        }

        /// <summary>
        /// Генерация события получения сообщения от сервера.
        /// </summary>
        /// <param name="message">Сообщение.</param>
        private void MessageReceived(string message)
        {
            OnReceiveMessage?.Invoke(message);
        }

        /// <summary>
        /// Отправляет ход.
        /// </summary>
        /// <param name="x">X.</param>
        /// <param name="y">Y.</param>
        private void SendStep(short x, short y)
        {
            if (x < MinStep || y < MinStep || x > MaxStep || y > MaxStep)
            {
                throw new ArgumentOutOfRangeException($"Индексы должны находится в диапозане [{MinStep};{MaxStep}]");
            }

            this.connection.InvokeAsync("ReceiveStep", x, y);
        }

        /// <summary>
        /// Запускает игру.
        /// </summary>
        private void StartGame()
        {
            this.connection.InvokeAsync(this.gameMode.ToString(), this.playerName);
        }
    }
}
