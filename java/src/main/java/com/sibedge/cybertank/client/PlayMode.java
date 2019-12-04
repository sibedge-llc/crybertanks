package com.sibedge.cybertank.client;

public enum PlayMode {

    FIGHT("Fight"),
    DEBUG("Debug"),
    DEBUG_TIMEOUT("DebugTimeout");

    public String getName() {
        return name;
    }

    private final String name;

    PlayMode(final String name) {
        this.name = name;
    }
}
