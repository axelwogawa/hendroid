const io = require("socket.io-client");
const request = require("request");

const socket = io("http://localhost:3030");

const express = require("express");
const app = express();
app.use(express.urlencoded({ extended: false }));

socket.emit("i am a raspi");

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

app.post("/stateChange", function(req, res) {
  console.log("stateChange info from raspi", req.body);
  socket.emit("state changed", req.body.new_state)
  res.send("all good");
});

app.listen(3031, function() {
  console.log("proxy listening on port 3031!");
});
