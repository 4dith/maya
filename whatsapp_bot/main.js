const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const WebSocket = require("ws");

// Create a new client instance
const client = new Client({
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    },
    authStrategy: new LocalAuth()
});

const ws = new WebSocket("ws://127.0.0.1:8765");

ws.on("open", () => {
    console.log("Connected to Python bridge");
    ws.send(JSON.stringify({ type: "bridge.status", status: "connected" }));
});

ws.on("message", async (raw) => {
    const data = JSON.parse(raw.toString());

    // Python -> Node.js command
    if (data.type === "whatsapp.send") {
        // Use your existing WhatsApp client here.
        // Validate recipient and content before sending.
        try {
            await client.sendMessage(
                data.chatId,
                data.text
            );
            console.log("Message sent:", data.text);
        } catch (err) {
            console.error("WhatsApp send failed:", err.message);
        }
    }
});

// When the client is ready, run this code (only once)
client.once('ready', () => {
    console.log('Client is ready!');
});

// When the client received QR-Code
client.on('qr', (qr) => {
    qrcode.generate(qr, {small: true});
});

// Listening to all incoming messages
client.on('message_create', message => {
	console.log((message.fromMe ? "Me": "Someone else") + ": " + message.body);
    if (ws.readyState !== WebSocket.OPEN) {
        console.error("Python bridge unavailable; message not forwarded");
        return;
    }

    if (message.body.startsWith("!")) {
        ws.send(JSON.stringify({
            type: "whatsapp.incoming",
            id: message.id._serialized,
            chatId: message.from,
            author: message.author || message.from,
            timestamp: message.timestamp,
            messageType: message.type,
            text: message.body.substring(1)
        }));
    }
});

// Start your client
client.initialize();
