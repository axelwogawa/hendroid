//REMOTE/LOCAL SERVER

const express = require("express");
const app = express();
const http = require("http");
const server = http.createServer(app);
const io = require("socket.io")(server);
const List = require("collections/list");

require("dotenv").config();

const mqtt = require("mqtt");
const mqttClient = mqtt.connect("mqtt://" + process.env.MQTT_HOST, {
  username: process.env.MQTT_USER,
  password: process.env.MQTT_PASSWORD
});

function logWithDate() {
  console.log(new Date().toLocaleString(), ...arguments);
}

app.use(express.urlencoded());
app.use(express.static(__dirname + "/static"));

let state = "no_idea";
/*'/' is the content of the initial GET request of a web browser calling the 
root directory of a website -> answer by delivering website content*/
app.get("/", (req, res) => {
  res.sendFile("static/index.html", { root: __dirname });
});

app.post("/", (req, res) => {});

app.get("/state", (req, res) => {
  res.send({
    state
  });
});

function subscription(topic) {
  return err => {
    if (err) console.error(err);
    console.log(`subscribed to ${topic} topic`);
  };
}

mqttClient.on("connect", function() {
  mqttClient.subscribe("stateChange", subscription("stateChange"));
  mqttClient.subscribe("timerUpdate", subscription("timerUpdate"));
  mqttClient.subscribe("hello", subscription("hello"));
});

mqttClient.on("message", function(topic, message) {
  message = message.toString();

  const handlers = {
    stateChange: message => {
      logWithDate("Emitting state change to ui client:", message);
      state = message;
      io.emit("state changed", message);
    },
    timerUpdate: message => {
      logWithDate("Emitting timer update to ui client:", message);
      io.emit("timer update", message);
    },
    hello: message => {
      logWithDate("Received 'hello' message", message);
    }
  };

  handlers[topic]
    ? handlers[topic](message)
    : logWithDate("received unhandled message in", topic, message);
});

io.on("connection", function connection(socket) {
  logWithDate("A user connected (ID:", socket.id, ")");

  /*requests from UI client*/
  socket.on("ui initial request", function() {
    logWithDate("New user is a UI client - updating him (ID:", socket.id, ")");
    mqttClient.publish("fullRequest", "pls give info");
  });

  socket.on("ui motion request", function(_state) {
    logWithDate("Emitting state change request to raspi:", _state);
    mqttClient.publish("motionRequest", _state);
  });

  socket.on("ui timer request", function(_request) {
    logWithDate("Emitting new timer setting request to raspi:", _request);
    mqttClient.publish("timerRequest", _request);
  });

  socket.on("disconnect", function(reason) {
    logWithDate("UI client disconnected (ID:", socket.id, ")");
    console.log("disconnection reason:", reason);
  });
});

server.listen(3030, function() {
  logWithDate("listening on *:3030");
});
