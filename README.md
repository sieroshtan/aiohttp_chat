# README #

This doc describes how we can start this awesome project

### How do I get set up? ###

#### Summary of set up
* Need NATS queue from https://hub.docker.com/_/nats/

* sudo docker run -d --name chat-nats -p 4222:4222 nats
* sudo docker run -d --name chat-db   -p 5432:5432 postgres


see **create_db.sql** for init database


