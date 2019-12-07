using System.Threading.Tasks;

namespace CyberTankClient
{
    using System;

    internal class Program
    {
        const string ServerUrl = "https://cybertank.sibedge.com:5001/gameHub";

        private async static Task Main(string[] args)
        {
            await using var bot = new CyberTankBot(ServerUrl, GameMode.Debug, "NLO");

            bot.OnReceiveMessage += message => { Console.WriteLine(message); };

            await bot.Start();

            Console.Read();
        }
    }
}
