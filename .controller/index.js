import mqtt from "./mqtt.min.js";

// GLOBAL VARIABLES
const client = mqtt.connect("ws://localhost:8081");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
let keyState = {};
const sentMessages = new Set();

// FUNCTIONS
function addLog(msg, type = "default") {
  const div = document.createElement("div");
  div.textContent = msg;
  div.classList.add("log-item", `log-${type}`);
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

addLog("[SITE] Keys are mapped NOW!", "system");

function send(topic) {
  client.publish(topic, "1");
  sentMessages.add(topic + ":1");
  addLog(`[OUT] ${topic}: 1`, "out");
}

// EVENT HANDLERS
client.on("connect", () => {
  statusEl.textContent = "Status: Connected";
  statusEl.className = "status connected";
  addLog("[SYSTEM] Connected to broker", "system");
});

client.on("close", () => {
  statusEl.textContent = "Status: Disconnected";
  statusEl.className = "status disconnected";
  addLog("[SYSTEM] Disconnected", "system");
});

client.on("message", (topic, message) => {
  const msg = topic + ":" + message.toString();

  if (sentMessages.has(msg)) {
    sentMessages.delete(msg);
    return;
  }

  if (topic === "info") {
    addLog(`[INFO] ${message.toString()}`, "info");
    return;
  }

  addLog(`[IN] ${topic}: ${message.toString()}`, "in");
});

// Subscribe to all movement and info topics
client.subscribe("move/#");
client.subscribe("info");

// Keybinding
document.addEventListener("keydown", (e) => {
  // if (keyState[e.code]) return; // comment if you want repeat on hold

  keyState[e.code] = true;

  switch (e.code) {
    // Movement
    case "KeyW":
      send("move/forward");
      break;
    case "KeyS":
      send("move/back");
      break;
    case "KeyA":
      send("move/left");
      break;
    case "KeyD":
      send("move/right");
      break;
    case "Space":
      send("move/up");
      break;
    case "ShiftLeft":
      send("move/down");
      break;

    // Rotation
    case "KeyQ":
      send("move/yaw_left");
      break;
    case "KeyE":
      send("move/yaw_right");
      break;

    // off
    case "KeyO":
      send("move/disarm");
      break;
    // on
    case "KeyN":
      addLog("[SITE] Arming motors. Wait for it and BE CAREFUL!", "info");
      send("move/arm");
      break;
  }
});

document.addEventListener("keyup", (e) => {
  keyState[e.code] = false;
});
