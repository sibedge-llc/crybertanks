package com.sibedge.cybertank.bot;

public interface Bot {

    String sendArrangement();

    Step sendStep();

    void receiveMessage(final String message);

    String giveMeYourName();
}
