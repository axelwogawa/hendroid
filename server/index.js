const app = require('express')()
const http = require('http')
const server = http.createServer(app)
const WebSocket = require('ws')

const wss = new WebSocket.Server({ server })

let state = 'closed'

app.get('/', (req, res) => {
  res.send(`
    <h1>Welcome to hendroid!</h1>
    <form method="POST">
      <p>Current state: ${state}</p>
      <button>Toggle</button>
    </form>
  `)
})

app.post('/', (req, res) => {
  state = state === 'closed' ? 'open' : 'closed'
  console.log('emitting stateChange to socket')
  wss.broadcast('stateChange:' + state)
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
  })
}

server.listen(3030, function() {
  console.log('listening on *:3030')
})
