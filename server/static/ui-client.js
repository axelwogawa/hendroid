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
	elem.parentElement.style.backgroundColor = "rgba(255, 255, 0, 0.7)"//"yellow"
}

function set_style_inactive(elem) {
	elem.parentElement.style.backgroundColor = "rgba(192, 192, 192, 0.7)"//"silver"
}

function validate_value(elem) {
	if(elem.value > elem.max)
		elem.value = elem.max
	else if(elem.value < elem.min)
		elem.value = elem.min
}
