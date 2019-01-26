//PROXY SOCKET-SERVER
// receiving messages from remote server (via socketIO) and transmitting them to 
// raspi's python code (where raspi acts as a Flaws server)
// receiving messages from raspi (where proxy acts as express server) and 
// transmitting them to remote server (via socketIO)

const io = require("socket.io-client");
const request = require("request");
// const socket = io("http://localhost:3030");
const socket = io("http://hendroid.zosel.ch");

const express = require("express");
const app = express();
app.use(express.urlencoded({ extended: false }));

const raspi_addr = "http://localhost:5000/"


//Say hello to remote server on connection
socket.emit("i am a raspi");


//###### Messages from remote server (socketIO) to raspi (Flaws server) ########
//full state request
socket.on("full state request", function() {
  console.log("received full state request");
  request.post(
    raspi_addr + "fullRequest",
    function(error, response, body) {
      if (error) {
        console.error("Error from raspi", error);
      }
      console.log("Raspi response", response && response.statusCode, body);
    }
  );
});

//motion request
socket.on("motion request", function(state) {
  console.log("received motion request: state =", state);
  request.post(
    raspi_addr + "motionRequest",
    {
      form: { state }
    },
    function(error, response, body) {
      if (error) {
        console.error("Error from raspi", error);
      }
      console.log("Raspi response", response && response.statusCode, body);
    }
  );
});

//set timer request
socket.on("set timer request", function(req) {
  console.log("received timer request: ", req);
  request.post(
    raspi_addr + "timerRequest",
    {
      form: { req }
    },
    function(error, response, body) {
      if (error) {
        console.error("Error from raspi", error);
      }
      console.log("Raspi response", response && response.statusCode, body);
    }
  );
});


//##### Messages from raspi (Express server) to remote server (socketIO) #######
//state change
app.post("/stateChange", function(req, res) {
  console.log("stateChange info from raspi", req.body);
  socket.emit("state changed", req.body.new_state);
  res.send("all good");
});

//timer update
app.post("/timerUpdate", function(req, res) {
  console.log("timerUpdate from raspi", req.body);
  socket.emit("timer update", req.body.update);
  res.send("all good");
});


//######################### Start proxy server #################################
const port = 3031
app.listen(port, function() {
  console.log("proxy listening on port", port);
});
