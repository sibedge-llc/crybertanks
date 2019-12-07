namespace CyberTankClient
{
    using System;
    using System.Threading.Tasks;
    using Microsoft.AspNetCore.SignalR.Client;
    using Newtonsoft.Json;

    /// <summary>
    /// Базовый класс бота для игры.
    /// </summary>
    public abstract class CyberTankBotBase : IAsyncDisposable
    {
        private const short MaxStep = 9;
        private const short MinStep = 0;

        private readonly HubConnection _connection;
        private readonly GameMode _gameMode;
        private readonly string _playerName;
        private readonly string _serverUrl;

        /// <summary>
        /// ctor.
        /// </summary>
        /// <param name="serverUrl">URL сервера игры.</param>
        /// <param name="gameMode">Режим игры.</param>
        /// <param name="playerName">Имя игрока.</param>
        protected CyberTankBotBase(string serverUrl, GameMode gameMode, string playerName)
        {
            _serverUrl = serverUrl ?? throw new ArgumentNullException(nameof(serverUrl));
            _gameMode = gameMode;
            _playerName = playerName ?? throw new ArgumentNullException(nameof(playerName));

            _connection = new HubConnectionBuilder().WithUrl(_serverUrl).Build();
        }

        /// <summary>
        /// Событие получения сообщения от сервера игры.
        /// </summary>
        public event Action<string> OnReceiveMessage;

        /// <inheritdoc/>
        public async ValueTask DisposeAsync()
        {
            await _connection.StopAsync();
            await _connection.DisposeAsync();
        }

        /// <summary>
        /// Запускает бота.
        /// </summary>
        /// <returns>Задание.</returns>
        public async Task Start()
        {
            _connection.On("requestArrangement",
                () =>
                {
                    var arrangement = OnArrangementRequested();
                    SendArrangement(arrangement);
                });

            _connection.On("requestStep",
                () =>
                {
                    var (x, y) = OnStepRequested();
                    SendStep(x, y);
                }
            );

            _connection.On<string>("receiveMessage", MessageReceived);

            try
            {
                await _connection.StartAsync();

                MessageReceived($"Подключено {_serverUrl}");
                StartGame();
            }
            catch (Exception e)
            {
                MessageReceived(e.GetBaseException().Message);
            }
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
            _connection.InvokeAsync("ReceiveArrangement", JsonConvert.SerializeObject(board));
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

            _connection.InvokeAsync("ReceiveStep", x, y);
        }

        /// <summary>
        /// Запускает игру.
        /// </summary>
        private void StartGame()
        {
            _connection.InvokeAsync(_gameMode.ToString(), _playerName);
        }
    }
}
