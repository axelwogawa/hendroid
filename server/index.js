const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const io = require('socket.io')(server)

app.use(express.urlencoded())
app.use(express.static(__dirname + '/static'))

let state = "no_idea"
/*'/' is the content of the initial GET request of a web browser calling the 
root document of a website (i.e. empty GET request)???????????????????????
-> answer by delivering website content*/
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

io.on('connection', function connection(socket) {
  console.log('a user connected', socket.id)
  socket.on('state changed', function(_state) {
    console.log("state changed: ", _state)
    state = _state
    socket.broadcast.emit('state changed', _state)
  })
  
  socket.on('timer update', function(_update) {
    console.log("timer update: ", _update)
    socket.broadcast.emit('timer update', _update)
  })

  socket.on('ui initial request', function() {
    console.log('New user is a UI client', socket.id)
    socket.broadcast.emit('full state request')
  })

  socket.on('ui motion request', function(_state) {
    console.log('emitting stateChange to socket', _state)
    socket.broadcast.emit('motion request', _state)
  })

  socket.on('ui timer request', function(_request) {
    console.log('emitting timer setting to socket', _request)
    socket.broadcast.emit('set timer request', _request)
  })
  socket.on('disconnect', function() {
    console.log('user disconnected', socket.id)
  })
})

server.listen(3030, function() {
  console.log('listening on *:3030')
})
