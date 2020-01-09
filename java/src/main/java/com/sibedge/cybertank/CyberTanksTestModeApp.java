package com.sibedge.cybertank;

import com.sibedge.cybertank.client.Client;
import com.sibedge.cybertank.client.PlayMode;


public class CyberTanksTestModeApp {

    public static void main(final String[] args) {
        final TestBot bot1 = new TestBot("GLaDOS_1");
        final TestBot bot2 = new TestBot("GLaDOS_2");

        new Client(bot1).start(PlayMode.TEST);
        new Client(bot2).start(PlayMode.TEST);
    }
}
