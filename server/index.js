// REMOTE/LOCAL SERVER

const imageDir = './images/'

const express = require('express');
const http = require('http');
// const List = require('collections/list');
var path = require('path');
require('dotenv').config();

var multer = require('multer');
var upload = multer({ dest: imageDir });
const app = express();
const server = http.createServer(app);
const io = require('socket.io')(server);
// app.use(upload);
app.use(express.static(imageDir));


const mqtt = require('mqtt');
const mqttClient = mqtt.connect('mqtt://' + process.env.MQTT_HOST, {
  username: process.env.MQTT_USER,
  password: process.env.MQTT_PASSWORD
});

function logWithDate () {
  console.log(new Date().toLocaleString(), ...arguments);
}

app.use(express.urlencoded());
app.use(express.static(path.join(__dirname, 'static')));

let state = 'no_idea';
/* '/' is the content of the initial GET request of a web browser calling the
root directory of a website -> answer by delivering website content */
app.get('/', (req, res) => {
  res.sendFile('static/index.html', { root: __dirname });
});

// state request
app.get('/state', (req, res) => {
  res.send({
    state
  });
});

// dummy -> ignore post request to root url
app.post('/', (req, res) => {});

// posting images
app.post('/images', upload.single('file'), (req, res) => {
  // todo: ignore image, if not expecting one
  logWithDate('Received new image:', req);
  io.emit('image', req.file.filename);
  res.send('Received image');
});

function subscription (topic) {
  return err => {
    if (err) console.error(err);
    console.log(`subscribed to ${topic} topic`);
  };
}

mqttClient.on('connect', function () {
  mqttClient.subscribe('stateChange', subscription('stateChange'));
  mqttClient.subscribe('timerUpdate', subscription('timerUpdate'));
  mqttClient.subscribe('hello', subscription('hello'));
});

mqttClient.on('message', function (topic, message) {
  message = message.toString();

  const handlers = {
    stateChange: message => {
      logWithDate('Emitting state change to ui client:', message);
      state = message;
      io.emit('state changed', message);
    },
    timerUpdate: message => {
      logWithDate('Emitting timer update to ui client:', message);
      io.emit('timer update', message);
    },
    hello: message => {
      logWithDate("Received 'hello' message", message);
    },
  };

  handlers[topic]
    ? handlers[topic](message)
    : logWithDate('received unhandled message in', topic, message);
});

io.on('connection', function connection (socket) {
  logWithDate('A user connected (ID:', socket.id, ')');

  /* requests from UI client */
  socket.on('ui initial request', function () {
    logWithDate('New user is a UI client - updating him (ID:', socket.id, ')');
    mqttClient.publish('fullRequest', 'pls give info');
  });

  socket.on('ui_image_request', function () {
    logWithDate('Emitting single image request to raspi');
    mqttClient.publish('imageRequest', 'single');
  });

  socket.on('ui motion request', function (_state) {
    logWithDate('Emitting state change request to raspi:', _state);
    mqttClient.publish('motionRequest', _state);
  });

  socket.on('ui timer request', function (_request) {
    logWithDate('Emitting new timer setting request to raspi:', _request);
    mqttClient.publish('timerRequest', _request);
  });

  socket.on('disconnect', function (reason) {
    logWithDate('UI client disconnected (ID:', socket.id, ')');
    console.log('disconnection reason:', reason);
  });
});

server.listen(3030, function () {
  logWithDate('listening on *:3030');
});
