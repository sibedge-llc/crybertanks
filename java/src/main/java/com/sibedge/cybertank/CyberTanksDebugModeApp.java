package com.sibedge.cybertank;

import com.sibedge.cybertank.client.Client;
import com.sibedge.cybertank.client.PlayMode;


public class CyberTanksDebugModeApp {

    public static void main(final String[] args) {
        final TestBot testBot = new TestBot("GLaDOS");
        //Запускать несколько тестовых ботов в режиме Fight нельзя, за это последуют санкции =)
        new Client(testBot).start(PlayMode.DEBUG);

    }
}
