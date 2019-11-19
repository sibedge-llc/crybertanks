FROM java:8-jdk-alpine
COPY . /usr/app/
WORKDIR /usr/app
CMD ["javac", "-cp", "lib/gson-2.8.6.jar:lib/gson-2.8.6.jar:lib/signalr-client-sdk.jar:lib/Java-WebSocket-1.4.0.jar:src", "src/**/*.java"] 
 ENTRYPOINT ["java", "-cp", "lib/gson-2.8.6.jar:lib/gson-2.8.6.jar:lib/signalr-client-sdk.jar:lib/Java-WebSocket-1.4.0.jar:src",  "com.sibedge.cybertank.BotT"]
