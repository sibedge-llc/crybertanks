package com.sibedge.cybertank;

import com.google.gson.Gson;
import microsoft.aspnet.signalr.client.LogLevel;
import microsoft.aspnet.signalr.client.Logger;
import microsoft.aspnet.signalr.client.hubs.HubConnection;
import microsoft.aspnet.signalr.client.hubs.HubProxy;

/**
 * @author gzheyts
 */
public class BotT {
    private static final String URL = "https://cybertank.sibedge.com:5001";
    private static final Gson MAPPER = new Gson();
    private static final boolean DEBUG = false;

    public static void main(final String[] args) {

        // Create a new console logger
        Logger logger = (message, level) -> System.out.println(message);

        // Connect to the server
        HubConnection conn = new HubConnection(URL, "", true, logger);

        // Create the hub proxy
        HubProxy proxy = conn.createHubProxy("gameHub");

        // Start the connection
        conn.start()
            .done(obj -> {
                // Subscribe to the error event
                conn.error(error -> {
                    error.printStackTrace();
                    conn.stop();
                });

                // Subscribe to the connected event
                conn.connected(() -> logger.log("CONNECTED", LogLevel.Information));

                // Subscribe to the closed event
                conn.closed(() -> logger.log("DISCONNECTED", LogLevel.Information));

                proxy.on("requestArrangement", () -> {
                    Byte[][] scene = {
                            {1, 0, 0, 1, 0, 0, 0, 0, 1, 1},
                            {1, 0, 0, 1, 0, 0, 0, 0, 0, 0},
                            {0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                            {0, 1, 0, 0, 0, 0, 1, 1, 0, 0},
                            {0, 1, 0, 0, 0, 0, 0, 0, 0, 0},
                            {0, 0, 0, 0, 0, 0, 0, 1, 1, 0},
                            {0, 0, 0, 1, 1, 0, 0, 0, 0, 0},
                            {0, 1, 0, 0, 0, 0, 0, 0, 0, 0},
                            {0, 1, 0, 1, 0, 1, 0, 0, 0, 0},
                            {0, 0, 0, 1, 0, 1, 0, 0, 0, 0},
                    };
                    proxy.invoke("ReceiveArrangement", MAPPER.toJson(scene));
                });

                proxy.on("requestStep", () -> proxy.invoke("ReceiveStep", 3, 0));
                proxy.on("receiveMessage", it -> logger.log("received: " + it, LogLevel.Information), String.class);
                proxy.invoke(DEBUG ? "Debug" : "Fight", "Player");
            });

    }
}
