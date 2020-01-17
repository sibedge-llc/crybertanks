namespace CyberTankClient
{
    /// <summary>
    /// Режим запуска игры.
    /// </summary>
    public enum GameMode
    {
        /// <summary>
        /// Отладка - для тестирования бота.
        /// </summary>
        Debug,

        /// <summary>
        /// Реальная игра с соперником.
        /// </summary>
        Fight,
        
        /// <summary>
        /// Игра с соперником без учета рейтинга.
        /// </summary>
        Test
    }
}
