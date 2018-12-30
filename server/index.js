const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const io = require('socket.io')(server)
const List = require("collections/list")

app.use(express.urlencoded())
app.use(express.static(__dirname + '/static'))

let state = "no_idea"
let uis = new List()
let pis = new List()
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

io.on('connection', function connection(socket) {
  console.log(new Date().toLocaleString(), "A user connected (ID:",
                  socket.id, ")")


  /*messages from pi client*/
  socket.on('i am a raspi', function() {
    console.log(new Date().toLocaleString(), "New user is a Pi client (ID:",
                  socket.id, ")")
    pis.push(socket.id)
  })

  socket.on('state changed', function(_state) {
    console.log(new Date().toLocaleString(),
                  "Emitting state change to ui client:", _state)
    state = _state
    socket.broadcast.emit('state changed', _state)
  })

  socket.on('timer update', function(_update) {
    console.log(new Date().toLocaleString(),
                  "Emitting timer update to ui client:", _update)
    socket.broadcast.emit('timer update', _update)
  })


  /*requests from UI client*/
  socket.on('ui initial request', function() {
    console.log(new Date().toLocaleString(),
                  "New user is a UI client - updating him (ID:",
                  socket.id, ")")
    socket.broadcast.emit('full state request')
    uis.push(socket.id)
  })

  socket.on('ui motion request', function(_state) {
    console.log(new Date().toLocaleString(), 
                  "Emitting state change request to raspi:", _state)
    socket.broadcast.emit('motion request', _state)
  })

  socket.on('ui timer request', function(_request) {
    console.log(new Date().toLocaleString(),
                  "Emitting new timer setting request to raspi:", _request)
    socket.broadcast.emit('set timer request', _request)
  })


  /*general connection events (all types of clients)*/
  socket.on('disconnect', function(reason) {
    if(uis.delete(socket.id)) {
      console.log(new Date().toLocaleString(), "UI client disconnected (ID:",
                    socket.id, ")")
    } else if(pis.delete(socket.id)) {
      console.log(new Date().toLocaleString(),
                    "PI client disconnected!!!!!111 (ID:", socket.id, ")")
    } else {
      console.log(new Date().toLocaleString(), "Old socket disconnected (ID:",
                    socket.id, ")")
    }
    console.log("disconnection reason:", reason)
  })
})

server.listen(3030, function() {
  console.log(new Date().toLocaleString(), "listening on *:3030")
})
