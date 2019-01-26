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


//Say hello to remote server on connection
socket.emit("i am a raspi");


//###### Messages from remote server (socketIO) to raspi (Flaws server) ########
//motion request
socket.on("motion request", function(state) {
  console.log("received motion request: state =", state);
  request.post(
    "http://localhost:5000/motionRequest",
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


//##### Messages from raspi (Express server) to remote server (socketIO) #######
//state change
app.post("/stateChange", function(req, res) {
  console.log("stateChange info from raspi", req.body);
  socket.emit("state changed", req.body.new_state);
  res.send("all good");
});


//######################### Start proxy server #################################
const port = 3031
app.listen(port, function() {
  console.log("proxy listening on port", port);
});
