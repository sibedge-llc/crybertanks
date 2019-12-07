namespace CyberTankClient
{
    using System;

    /// <summary>
    /// Бот для игры
    /// </summary>
    public class CyberTankBot : CyberTankBotBase
    {
        private readonly Random _random;

        /// <summary>
        /// ctor.
        /// </summary>
        /// <param name="serverUrl">URL сервера игры.</param>
        /// <param name="gameMode">Режим игры.</param>
        /// <param name="playerName">Имя игрока.</param>
        public CyberTankBot(string serverUrl, GameMode gameMode, string playerName)
            : base(serverUrl, gameMode, playerName)
        {
            _random = new Random(Environment.TickCount);
        }

        /// <inheritdoc/>
        /// <remarks>
        /// Здесь должен быть размещён код для генерации расстановки танков.
        /// </remarks>
        protected override short[,] OnArrangementRequested()
        {
            return new short[,]
            {
                { 1, 0, 0, 1, 0, 0, 0, 0, 1, 1 },
                { 1, 0, 0, 1, 0, 0, 0, 0, 0, 0 },
                { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
                { 0, 1, 0, 0, 0, 0, 1, 1, 0, 0 },
                { 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
                { 0, 0, 0, 0, 0, 0, 0, 1, 1, 0 },
                { 0, 0, 0, 1, 1, 0, 0, 0, 0, 0 },
                { 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
                { 0, 1, 0, 1, 0, 1, 0, 0, 0, 0 },
                { 0, 0, 0, 1, 0, 1, 0, 0, 0, 0 }
            };
        }

        /// <inheritdoc/>
        /// <remarks>
        /// Тут должен быть размещён код для генерации хода.
        /// </remarks>
        protected override (short x, short y) OnStepRequested()
        {
            return (x: (short)_random.Next(0, 9), y: (short)_random.Next(0, 9));
        }
    }
}
