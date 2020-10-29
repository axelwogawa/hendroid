/**
TODO: payload string encoding -> JSON structure
TODO: websocket -> mqtt
*/
const socket = io();
// const socket = new WebSocket("ws://localhost:9160")
// const id = Math.random();
// strings for showing actual state in UI
const stateStrs = {
  opened: 'ist geöffnet',
  closed: 'ist geschlossen',
  opening: 'öffnet sich',
  closing: 'schließt sich',
  intermediate: 'steht halb geöffnet',
  no_idea: 'weiß nicht'
};

let waitingForImage = false;
const waitForImageTimeout_ms = 8000;
// const msgTypeActions = {
//  "timer update": timerUpdate,
//  "state changed": stateChanged,
//   "image": showImage
// }

// socket.onopen = function (event) {
//  // socket.send("ui initial request");
//  setInterval(() => {
//    socket.send(id);
//  }, 2000)
// };

/**
* TODO: JSON encoding, e.g.:
* message format:
{
  eventType: "message",
  text: "text",
  id:   123,
  date: "28.11.1990"
}
*/
// socket.onmessage = function (event) {
//  console.log("received", event.data);
//  if (event.data.eventType && event.data.eventType in msgTypeActions) {
//    msgTypeActions[event.data.eventType](event.data.text);
//  } else {
//    console.log("Unknown message type");
//  }
// }

socket.emit('ui initial request');/* request full Pi state after website load/reload */

socket.on('image', function (encodedImage) {
  if (waitingForImage) {
    const decodedImage = atob(encodedImage); // 'a'scii 'to' 'b'inary
    // supported by most browsers
    document.getElementById('image').src = URL.createObjectURL(decodedImage);
  }
  waitingForImage = false;
});

/*
TODO: JSON structure
*/
socket.on('state changed', function (state) {
// function stateChanged (state) {
  document.querySelector('#state').textContent = stateStrs[state];
});

/*
TODO: JSON structure
{
  eventType: "auto",
  value: "true"
}
or
{
  eventType: "time",
  value: {
    direction: "open",
    hours: 12,
    minutes: 0
  }
}
*/
socket.on('timer update', function (update) {
// function timerUpdate (update) {
  let updateCont = [];
  updateCont = update.split('-');
  const elems = [];
  if (updateCont[0] === 'auto') {
    const active = updateCont[2].toLowerCase() === 'true';
    const id_ = 'cb_auto_' + updateCont[1];
    elems[0] = document.getElementById(id_);
    elems[0].checked = active;
    if (active) {
      setStyleActive(elems[0]);
    } else {
      setStyleInactive(elems[0]);
    }
  } else if (updateCont[0] === 'time') {
    const idH = 'time_' + updateCont[1] + '_h';
    const idM = 'time_' + updateCont[1] + '_m';
    elems[0] = document.getElementById(idH);
    elems[1] = document.getElementById(idM);
    const time = updateCont[2].split(':');
    elems[0].value = parseInt(time[0]);
    elems[1].value = parseInt(time[1]);
    elems.forEach(setStyleConfirmed);
  }
});

// ########################## UI Callbacks #####################################

/**
 * imageRequest - Send image request to Raspi (i.e. take an image and send it
 * back to client via websocket 'image' message), change HTML image element's
 * content to wait-gif, wait for <waitForImageTimeout_ms>. If within this
 * timeout no image was received, the image element will show "'Bildübertragung
 * fehlgeschlagen".
 *
 * @returns {undefined}
 */
async function imageRequest () {
  socket.emit('ui_imageRequest');
  waitingForImage = true;
  const imageTarget = document.getElementById('image');
  imageTarget.src = 'waiting4.gif';
  await new Promise(resolve => setTimeout(resolve, waitForImageTimeout_ms));
  if (waitingForImage) {
    imageTarget.src = '';
    imageTarget.alt = 'Bildübertragung fehlgeschlagen';
  }
  waitingForImage = false;
}

/*
TODO: JSON structure
*/
function motionRequest (state) {
  socket.emit('ui motion request', state);
}

/*
TODO: JSON structure
like timerUpdate()
*/
function timerRequest (elem, cat, subcat) {
  if (cat === 'auto') {
    socket.emit('ui timer request', cat + '-' + subcat + '-' + elem.checked.toString());
  } else if (cat === 'time') {
    const idH = 'time_' + subcat + '_h';
    const idM = 'time_' + subcat + '_m';
    let time = document.getElementById(idH).value.toString();
    time = time + ':' + document.getElementById(idM).value.toString();
    socket.emit('ui timer request', cat + '-' + subcat + '-' + time);
  }
}

/**
* Function to set local variable determining whether or not to switch on the
* light when taking an image
* @param elem - checkbox for setting/unsetting light
*/
function setImgLight (elem) {
  // TODO
}

function resetStyle (elem) {
  elem.style.borderColor = '';
  elem.style.backgroundColor = '';
}

function setStyleConfirmed (elem) {
  elem.style.borderColor = 'SpringGreen';
}

function setStyleActive (elem) {
  elem.parentElement.style.backgroundColor = 'rgba(255, 255, 0, 0.7)';// "yellow"
}

function setStyleInactive (elem) {
  elem.parentElement.style.backgroundColor = 'rgba(192, 192, 192, 0.7)';// "silver"
}

function validateValue (elem) {
  if (elem.value > elem.max) {
    elem.value = elem.max;
  } else if (elem.value < elem.min) {
    elem.value = elem.min;
  }
}
