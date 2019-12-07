//REMOTE/LOCAL SERVER

const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const io = require('socket.io')(server)
const List = require("collections/list")

const mqtt = require('mqtt')
const mqttClient = mqtt.connect('mqtt://localhost', {
  username: "hendroid",
  password: "__secret__"
})

app.use(express.urlencoded())
app.use(express.static(__dirname + '/static'))

let state = "no_idea"
/*'/' is the content of the initial GET request of a web browser calling the 
root directory of a website -> answer by delivering website content*/
app.get('/', (req, res) => {
	res.sendFile('static/index.html', {root: __dirname });
})

app.post('/', (req, res) => {
})

app.get('/state', (req, res) => {
  res.send({
    state
  })
})


mqttClient.on("connect", function () {
  mqttClient.subscribe("stateChange", function (err) {
    if (err) console.error(err)
    console.log("subscribed to stateChange topic")
  });
  mqttClient.subscribe("timerUpdate", function (err) {
    if (err) console.error(err)
    console.log("subscribed to timerUpdate topic")
  });
})


mqttClient.on('message', function(topic, message) {
  message = message.toString()
  switch (topic) {
    case "stateChange":
      console.log(new Date().toLocaleString(),
                    "Emitting state change to ui client:", message)
      state = message
      io.emit('state changed', message)

    case "timerUpdate":
      console.log(new Date().toLocaleString(),
                    "Emitting timer update to ui client:", message)
      io.emit('timer update', message)

    default:
      console.log(
        new Date().toLocaleString(), 
        "received unhandled message in", 
        topic, 
        message
      )
  }
})

io.on('connection', function connection(socket) {
  console.log(new Date().toLocaleString(), "A user connected (ID:",
                  socket.id, ")")

  /*requests from UI client*/
  socket.on('ui initial request', function() {
    console.log(new Date().toLocaleString(),
                  "New user is a UI client - updating him (ID:",
                  socket.id, ")")
    mqttClient.publish('fullRequest', "pls give info")
  })

  socket.on('ui motion request', function(_state) {
    console.log(new Date().toLocaleString(), 
                  "Emitting state change request to raspi:", _state)
    mqttClient.publish('motionRequest', _state)
  })

  socket.on('ui timer request', function(_request) {
    console.log(new Date().toLocaleString(),
                  "Emitting new timer setting request to raspi:", _request)
    socket.broadcast.emit('timerRequest', _request)
  })


  socket.on('disconnect', function(reason) {
    console.log(new Date().toLocaleString(), "UI client disconnected (ID:",
                    socket.id, ")")
    console.log("disconnection reason:", reason)
  })
})

server.listen(3030, function() {
  console.log(new Date().toLocaleString(), "listening on *:3030")
})
