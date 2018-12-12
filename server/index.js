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
            socket.emit("ui timer request", cat + "-" + subcat + "-" + elem.checked.toString())
          else if (cat === "time") {
          	let id_h = "time_" + subcat + "_h"
          	let id_m = "time_" + subcat + "_m"
            let time = document.getElementById(id_h).value.toString()
            time = time + ":" + document.getElementById(id_m).value.toString()
          	socket.emit("ui timer request", cat + "-" + subcat + "-" + time)
          }
        }
        function set_style_unconfirmed(elem) {
          elem.style.backgroundColor = "grey"
        }
        function validate_value(elem) {
          if(elem.value > elem.max)
            elem.value = elem.max
          else if(elem.value < elem.min)
            elem.value = elem.min
        }
    </script>

    <h1>Hendroid</h1>
    <h2>Die automatische Hühnerklappe</h2>
    <p>Current state: <span id="state">${state}</span></p>
    <button onclick="motion_request('opening')">Öffnen</button>
    <button onclick="motion_request('closing')">Schließen</button>
    <br>
    <input type="checkbox" id="cb_auto_open" onClick="timer_request(this, 'auto', 'open')">Automatisch Öffnen
    <div>
      <input type="number" id="time_open_h" min=0 max=23 defaultValue=0 onChange="set_style_unconfirmed(this)" onBlur="validate_value(this)">:
      <input type="number" id="time_open_m" min=0 max=59 defaultValue=0 step=10 onChange="set_style_unconfirmed(this)" onBlur="validate_value(this)">Uhr
      <button onClick="timer_request(this, 'time', 'open')">Uhrzeit übernehmen</button>
    </div>
    <input type="checkbox" id="cb_auto_close" onClick="timer_request(this, 'auto', 'close')">Automatisch Schließen
    <div>
      <input type="number" id="time_close_h" min=0 max=23 defaultValue=0 onChange="set_style_unconfirmed(this)" onBlur="validate_value(this)">:
      <input type="number" id="time_close_m" min=0 max=59 defaultValue=0 step=10 onChange="set_style_unconfirmed(this)" onBlur="validate_value(this)">Uhr
      <button onClick="timer_request(this, 'time', 'close')">Uhrzeit übernehmen</button>
    </div>
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
