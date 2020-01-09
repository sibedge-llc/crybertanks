package com.sibedge.cybertank.client;

import com.microsoft.signalr.HubConnection;
import com.microsoft.signalr.HubConnectionBuilder;
import com.sibedge.cybertank.bot.Bot;
import com.sibedge.cybertank.bot.Step;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Client {

    private static final Logger LOGGER = LoggerFactory.getLogger(Client.class);
    private static final String HUB_URL = "https://cybertank.sibedge.com:5001/gameHub";

    private final HubConnection connection;
    private final Bot bot;


    public Client(final Bot bot) {
        this.connection = HubConnectionBuilder.create(HUB_URL).build();
        this.bot = bot;
    }

    public void start(final PlayMode mode) {
        connection.on("requestArrangement", () ->
                connection.send("ReceiveArrangement", bot.sendArrangement()));
        connection.on("requestStep", () -> {
            final Step step = bot.sendStep();
            connection.send("ReceiveStep", step.getY(), step.getX());
        });
        connection.on("receiveMessage", message -> {
            LOGGER.info("received message {}", message);
            bot.handleMessage(message);
        }, String.class);

        connection.onClosed(exception -> {
            LOGGER.info("End of the game");
            connection.stop();
        });

        connection.start().blockingAwait();
        connection.send(mode.getName(), bot.getName());
    }
}
