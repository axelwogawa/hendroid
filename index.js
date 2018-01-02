const app = require('express')()
const http = require('http').Server(app)
const io = require('socket.io')(http)

let state = 'closed'
let socket = null

app.get('/', (req, res) => {
  res.send(`
    <h1>Welcome to hendroid!</h1>
    <form method="POST">
      <p>Current state: ${state}</p>
      <button>Toggle</button>
    </form>
    <script src="/socket.io/socket.io.js"></script>
    <script>
      var io = io();
      io.on('stateChange', function(state) {
        console.log('new State!: ' + state);
      });
    </script>
  `)
})

app.post('/', (req, res) => {
  state = state === 'closed' ? 'open' : 'closed'
  console.log('emitting stateChange to socket', socket === null)
  io.emit('stateChange', state)
  res.redirect('/')
})

app.get('/state', (req, res) => {
  res.send({
    state
  })
})

io.on('connection', function(socket) {
  console.log('a user connected')

  socket.on('disconnect', function() {
    console.log('user disconnected')
  })
})

http.listen(3010, function() {
  console.log('listening on *:3010')
})
