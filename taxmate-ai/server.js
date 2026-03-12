const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const fs = require('fs');
const path = require('path');

// Express app setup
const app = express();
const server = http.createServer(app);
const io = socketIO(server);

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// Store messages
const messages = [];
const clients = new Map();

// WhatsApp Client
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './whatsapp-auth'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// QR Code generation
client.on('qr', (qr) => {
    console.log('\n📱 Scan this QR code with your WhatsApp:\n');
    qrcode.generate(qr, { small: true });
    
    // Send QR to web interface
    io.emit('qr', qr);
});

// Ready event
client.on('ready', () => {
    console.log('\n✅ WhatsApp connected successfully!\n');
    io.emit('ready', { message: 'WhatsApp Connected' });
});

// Message received
client.on('message_create', async (msg) => {
    // Only process incoming messages (not from bot)
    if (!msg.fromMe) {
        const messageData = {
            id: msg.id.id,
            from: msg.from,
            fromName: msg._data.notifyName || 'Unknown',
            body: msg.body,
            timestamp: new Date().toISOString(),
            type: msg.type
        };
        
        messages.push(messageData);
        
        // Broadcast to web interface
        io.emit('new_message', messageData);
        
        // Save to file
        saveMessages();
        
        console.log(`\n💬 New message from ${messageData.fromName}:`);
        console.log(`   ${msg.body}\n`);
    }
});

// Save messages to file
function saveMessages() {
    fs.writeFileSync(
        './messages.json', 
        JSON.stringify(messages, null, 2)
    );
}

// Load existing messages
function loadMessages() {
    if (fs.existsSync('./messages.json')) {
        const data = JSON.parse(fs.readFileSync('./messages.json'));
        messages.push(...data);
    }
}

// API Routes
app.get('/api/messages', (req, res) => {
    res.json(messages);
});

app.get('/api/status', (req, res) => {
    res.json({ 
        connected: client.info ? true : false,
        timestamp: new Date().toISOString()
    });
});

// Send reply
app.post('/api/reply', async (req, res) => {
    const { to, message } = req.body;
    try {
        await client.sendMessage(to, message);
        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`\n🚀 TaxMate AI Server running on http://localhost:${PORT}`);
    console.log('\n📱 Open this URL to scan QR code and connect WhatsApp\n');
});

// Initialize
loadMessages();
client.initialize();
