const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const io = require('socket.io')(server)

app.use(express.urlencoded())

let state = "no idea"

app.get('/', (req, res) => {
  res.send(`
    <script src="/socket.io/socket.io.js"></script>
    <script>
        const socket = io()
        socket.on("state changed", function(state) {
          document.querySelector("#state").textContent = state
        })
        function request(state) {
          socket.emit("ui request", state)
        }
    </script>

    <h1>Welcome to hendroid!</h1>
    <p>Current state: <span id="state">${state}</span></p>
    <button onclick="request('opening')">Öffnen</button>
    <button onclick="request('closing')">Schließen</button>
  `)
})

app.post('/', (req, res) => {
})

app.get('/state', (req, res) => {
  res.send({
    state
  })
})

io.on('connection', function connection(socket) {
  console.log('a user connected')
  socket.on('state changed', function(_state) {
    console.log("state changed:", _state)
    state = _state
    socket.broadcast.emit('state changed', _state)
  })

  socket.on('ui request', function(_state) {
    console.log('emitting stateChange to socket', _state)
    socket.broadcast.emit('request', _state)
  })
})

server.listen(3030, function() {
  console.log('listening on *:3030')
})
