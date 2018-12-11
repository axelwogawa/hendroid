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
        function motion_request(state) {
          socket.emit("ui motion request", state)
        }
        function timer_request(elem, cat, subcat) {
          if (cat === "auto")
            socket.emit("ui timer request", cat.concat(":", subcat ,":", elem.value.toString()))
        }
    </script>

    <h1>Hendroid</h1>
    <h2>Die automatische Hühnerklappe</h2>
    <p>Current state: <span id="state">${state}</span></p>
    <button onclick="motion_request('opening')">Öffnen</button>
    <button onclick="motion_request('closing')">Schließen</button>
    <br>
    <input type="checkbox" id="cb_auto_open" onClick="timer_request(this, 'auto', 'open')">Automatisch Öffnen
    <input type="time" id="time_open" onBlur="timer_request(this, 'time', 'open')">
    <br>
    <input type="checkbox" id="cb_auto_close" onClick="timer_request(this, 'auto', 'close')">Automatisch Schließen
    <input type="time" id="time_close" onClick="timer_request(this, 'time', 'close')">
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

  socket.on('ui motion request', function(_state) {
    console.log('emitting stateChange to socket', _state)
    socket.broadcast.emit('motion request', _state)
  })

  socket.on('ui timer request', function(_request) {
    console.log('emitting timer setting to socket', _request)
    socket.broadcast.emit('set timer request', _request)
  })
})

server.listen(3030, function() {
  console.log('listening on *:3030')
})
