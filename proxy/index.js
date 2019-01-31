//PROXY SOCKET-SERVER
// receiving messages from remote server (via socketIO) and transmitting them to 
// raspi's python code (where raspi acts as a Flaws server)
// receiving messages from raspi (where proxy acts as express server) and 
// transmitting them to remote server (via socketIO)

const io = require("socket.io-client");
const request = require("request");
const sockets = [io("http://localhost:3030"), io("https://hendroid.zosel.ch")];

const express = require("express");
const app = express();
app.use(express.urlencoded({ extended: false }));

const raspi_addr = "http://localhost:5000/"



sockets.forEach(function (socket){
  //Say hello to remote server on connection
  socket.emit("i am a raspi");


  //###### Messages from server (socketIO) to raspi (Flaws server) ########
  //full state request
  socket.on(eventName="fullRequest", function() {
    transmitRequest("fullRequest", "");
  });

  //motion request
  socket.on(eventName="motionRequest", function(body) {
    transmitRequest("motionRequest", body);
  });

  //set timer request
  socket.on(eventName="timerRequest", function(body) {
    transmitRequest("timerRequest", body);
  });

  //generic transmission routine
  function transmitRequest(eventName, body){
    console.log("received", eventName, body);
    request.post(
      raspi_addr + eventName,
      {
        form: { body }
      },
      function(error, response, body) {
        if (error) {
          console.error("Error from raspi", error);
        }
        console.log("Raspi response", response && response.statusCode, body);
      }
    );
  }
});


//##### Messages from raspi (Express server) to remote server (socketIO) #######
//state change
app.post("/stateChange", function(req, res) {
  transmitRequest("stateChange", req, res);
});

//timer update
app.post("/timerUpdate", function(req, res) {
  transmitRequest("timerUpdate", req, res);
});

function transmitRequest(eventName, req, res){
  console.log(eventName, "from raspi", req.body);
  sockets.forEach(function (socket){
    socket.emit(eventName, req.body.body);
  });
  res.send("all good");
}


//######################### Start proxy server #################################
const port = 3031
app.listen(port, function() {
  console.log("proxy listening on port", port);
});
