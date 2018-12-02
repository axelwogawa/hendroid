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
    </script>

    <h1>Welcome to hendroid!</h1>
    <form method="POST">
      <p>Current state: <span id="state">${state}</span></p>
      <input type="submit" name="request" value="Öffnen">
      <input type="submit" name="request" value="Schliessen">
    </form>
  `)
})

app.post('/', (req, res) => {
  console.log('emitting stateChange to socket', req.body.request)
  io.emit('request', req.body.request === "Öffnen" ? 'opening' : 'closing')
  res.redirect('/')
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
})

server.listen(3030, function() {
  console.log('listening on *:3030')
})
