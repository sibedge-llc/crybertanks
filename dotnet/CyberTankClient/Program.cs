namespace CyberTankClient
{
    using System;

    internal class Program
    {
        private static void Main(string[] args)
        {
            var serverUrl = "https://localhost:5001/gameHub";

            using (var bot = new CyberTankBot(serverUrl, GameMode.Debug, "Player_1"))
            {
                bot.OnReceiveMessage += message => { Console.WriteLine(message); };
                bot.Start();

                Console.Read();
            }
        }
    }
}
