package com.sibedge.cybertank.client;

public enum PlayMode {

    /**
     * Режим боя
     */
    FIGHT("Fight"),

    /**
     * Режим отладки
     */
    DEBUG("Debug"),

    /**
     * Режим тестового боя с визуальным отображением между двумя ботами
     */
    TEST("Test");

    public String getName() {
        return name;
    }

    private final String name;

    PlayMode(final String name) {
        this.name = name;
    }
}
