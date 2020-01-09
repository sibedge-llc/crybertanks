package com.sibedge.cybertank;

import com.sibedge.cybertank.bot.Bot;
import com.sibedge.cybertank.bot.Step;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Random;

/**
 * Эталонная реализация бота
 */
public class TestBot implements Bot {

    private final Logger logger = LoggerFactory.getLogger(TestBot.class);


    private final String name;


    TestBot(final String name) {
        this.name = name;
    }

    /**
     * Оправка расстановки
     *
     * @return матрица 10*10 в формате json
     */
    @Override
    public String sendArrangement() {
        return "{}";
    }

    /**
     * Ход
     * Требований к алгоритму, решающему какой сделать ход нет, можно подключать любые библиотеки
     *
     * @return объект с координатими x,y
     */
    @Override
    public Step sendStep() {
        final Random random = new Random();
        random.setSeed(System.nanoTime());
        return new Step(random.nextInt(9), random.nextInt(9));
    }

    /**
     * Получение сообщения от сервера в формате json
     *
     * @param message Сообщение может содержать расстановку с сервера(в случае, если отправленная расстановка
     *                com.sibedge.cybertank.TestBot#sendArrangement() некорректна) или результат прошлого хода
     */
    @Override
    public void handleMessage(final String message) {
        logger.info(message);
    }


    @Override
    public String getName() {
        return this.name;
    }
}
