import mqtt from "./mqtt.min.js";

// GLOBAL VARIABLES
const client = mqtt.connect("ws://localhost:8081");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
let keyState = {};
const sentMessages = new Set();

// FUNCTIONS
function addLog(msg) {
    const p = document.createElement("div");
    p.textContent = msg;
    logEl.appendChild(p);
    logEl.scrollTop = logEl.scrollHeight;
}

addLog("[SITE] Keys are mapped NOW!");

function send(topic) {
    // this function also remembers what is sent so that we can filter out what messages have been sent and what are non-browser messages
    client.publish(topic, "1");
    sentMessages.add(topic + ":1");
    addLog(`[OUT] ${topic}: 1`);
}

// EVENT HANDLERS
client.on("connect", () => {
    statusEl.textContent = "Status: Connected";
    statusEl.className = "status connected";
    addLog("[SYSTEM] Connected to broker");
});

client.on("close", () => {
    statusEl.textContent = "Status: Disconnected";
    statusEl.className = "status disconnected";
    addLog("[SYSTEM] Disconnected");
});

client.on("message", (topic, message) => {
    const msg = topic + ":" + message.toString();
    if (sentMessages.has(msg)) {
        sentMessages.delete(msg); // to prevent memory leaks
        return;
    }
    if (topic === "move/info") {
        addLog(message);
        return;
    }
    addLog(`[IN] ${topic}: ${message.toString()}`);
});

// Subscribe to all movement and info topics
client.subscribe("move/#");
client.subscribe("info");

// Keybinding
document.addEventListener("keydown", (e) => {
    if (keyState[e.code]) return;
    keyState[e.code] = true;

    switch (e.code) {
        // Movement
        case "KeyW": send("move/forward"); break;
        case "KeyS": send("move/back"); break;
        case "KeyA": send("move/left"); break;
        case "KeyD": send("move/right"); break;
        case "Space": send("move/up"); break;
        case "ShiftLeft": send("move/down"); break;

        // Rotation
        case "KeyQ": send("move/yaw_left"); break;
        case "KeyE": send("move/yaw_right"); break;

        // kill switch
        case "KeyO": send("move/stop"); break;
    }
});

document.addEventListener("keyup", (e) => {
    keyState[e.code] = false;
});