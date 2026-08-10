FROM openjdk:17-slim
RUN apt-get update && apt-get install -y maven    