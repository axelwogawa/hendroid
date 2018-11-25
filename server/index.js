const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const WebSocket = require('ws')

app.use(express.urlencoded());

const wss = new WebSocket.Server({ server })
let state = "no idea";

app.get('/', (req, res) => {
  res.send(`
    <h1>Welcome to hendroid!</h1>
    <form method="POST">
      <p>Current state: ${state}</p>
      <input type="submit" name="request" value="Öffnen">
      <input type="submit" name="request" value="Schliessen">
    </form>
  `)
})

app.post('/', (req, res) => {
  console.log('emitting stateChange to socket', req.body.request)
  wss.broadcast('request:' + (req.body.request === "Öffnen" ? 'opening' : 'closing'))
  res.redirect('/')
})

app.get('/state', (req, res) => {
  res.send({
    state
  })
})

wss.on('connection', function connection(ws) {
  console.log('a user connected')
})

wss.broadcast = function broadcast(data) {
  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data)
    }

    client.onmessage = function(event) {
      console.log("something happened!", event.data)
      state = event.data
    }
  })
}



server.listen(3030, function() {
  console.log('listening on *:3030')
})
