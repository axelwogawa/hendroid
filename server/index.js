const express = require('express')
const app = express()
const http = require('http')
const server = http.createServer(app)
const io = require('socket.io')(server)

app.use(express.urlencoded())

let state = "no_idea"
/*'/' is the content of the initial GET request of a web browser calling the 
root document of a website (i.e. empty GET request)???????????????????????
-> answer by delivering website content*/
app.get('/', (req, res) => {
	/*res.sendFile('index.html', {root: __dirname })
	res.sendFile('huehner_.png', {root: __dirname })})*/
  res.send(`
    <script src="/socket.io/socket.io.js"></script>
    <script>
        const socket = io()

        const state_strs = {
	                    opened:       "ist geöffnet"
	                    ,closed:      "ist geschlossen"
	                    ,opening:     "öffnet sich"
	                    ,closing:     "schließt sich"
	                    ,intermediate:"steht halb geöffnet"
	                    ,no_idea:     "weiß nicht so recht"
                            }

        socket.emit("ui initial request")/*request full Pi state after website load/reload*/
        
        socket.on("state changed", function(state) {
          document.querySelector("#state").textContent = state_strs[state]
        })
        
        socket.on('timer update', function(update) {
          let update_cont = []
          update_cont = update.split('-')
          let elems = []
          if (update_cont[0] === "auto") {
            let active = update_cont[2].toLowerCase() === "true"
            let id_ = "cb_auto_" + update_cont[1]
            elems[0] = document.getElementById(id_)
            elems[0].checked = active
            if (active)
              set_style_active(elems[0])
            else
              set_style_inactive(elems[0])
          }
          else if (update_cont[0] === "time") {
            let id_h = "time_" + update_cont[1] + "_h"
            let id_m = "time_" + update_cont[1] + "_m"
            elems[0] = document.getElementById(id_h)
            elems[1] = document.getElementById(id_m)
            let time = update_cont[2].split(':')
            elems[0].value = parseInt(time[0])
            elems[1].value = parseInt(time[1])
            elems.forEach(set_style_confirmed)
          }
          
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
        
        function reset_style(elem) {
          elem.style.borderColor = ""
          elem.style.backgroundColor = ""
        }
        
        function set_style_confirmed(elem) {
          elem.style.borderColor = "SpringGreen"
        }
        
        function set_style_active(elem) {
          elem.parentElement.style.backgroundColor = "yellow"
        }
        
        function set_style_inactive(elem) {
          elem.parentElement.style.backgroundColor = "silver"
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
    <div style="border: 5px solid midnightblue">
      <h3>Steuern</h3>
      <p>Klappe <span id="state"></span></p>
    	<button onclick="motion_request('opening')">Öffnen</button>
    	<button onclick="motion_request('closing')">Schließen</button>
    </div>
    <div style="margin: 1em auto 1em auto">
      <input type="checkbox" id="cb_auto_open" onClick="timer_request(this, 'auto', 'open')">Automatisch Öffnen
      <br>
      <input type="number" id="time_open_h" min=0 max=23 defaultValue=0 onChange="reset_style(this)" onBlur="validate_value(this)">:
      <input type="number" id="time_open_m" min=0 max=59 defaultValue=0 step=10 onChange="reset_style(this)" onBlur="validate_value(this)">Uhr
      <button onClick="timer_request(this, 'time', 'open')">Uhrzeit übernehmen</button>
    </div>
    <div style="border: 1px solid grey; margin: 1em 5em 1em 5em"> </div>
    <div style="margin: 1em auto 1em auto">
      <input type="checkbox" id="cb_auto_close" onClick="timer_request(this, 'auto', 'close')">Automatisch Schließen
      <br>
      <input type="number" id="time_close_h" min=0 max=23 defaultValue=0 onChange="reset_style(this)" onBlur="validate_value(this)">:
      <input type="number" id="time_close_m" min=0 max=59 defaultValue=0 step=10 onChange="reset_style(this)" onBlur="validate_value(this)">Uhr
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
    console.log("state changed: ", _state)
    state = _state
    socket.broadcast.emit('state changed', _state)
  })
  
  socket.on('timer update', function(_update) {
    console.log("timer update: ", _update)
    socket.broadcast.emit('timer update', _update)
  })

  socket.on('ui initial request', function() {
    console.log('New user is a UI client')
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
})

server.listen(3030, function() {
  console.log('listening on *:3030')
})
