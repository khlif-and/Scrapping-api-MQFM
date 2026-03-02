const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, Browsers, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

const app = express();
app.use(express.json());

let sock;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version } = await fetchLatestBaileysVersion();
    
    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: 'silent' }), // Silent agar terminal bersih
        browser: Browsers.macOS('Desktop'),
        syncFullHistory: false // Meringankan beban websocket
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log("\nSCAN QR DI BAWAH INI DENGAN HP ANDA:");
            qrcode.generate(qr, { small: true });
        }
        
        if(connection === 'close') {
            const statusCode = (lastDisconnect.error)?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            console.log('Koneksi tertutup, reconnecting:', shouldReconnect, 'Code:', statusCode);
            
            // Hancurkan referensi socket lama
            sock = null;

            if(shouldReconnect) {
                setTimeout(connectToWhatsApp, 3000);
            } else {
                console.log("Sesi WhatsApp Logged Out/Ditolak. Membersihkan auth_info_baileys...");
                // Jika server menolak sesi secara permanen, hapus cache dan generate QR baru
                if (fs.existsSync('./auth_info_baileys')) {
                    fs.rmSync('./auth_info_baileys', { recursive: true, force: true });
                }
                setTimeout(connectToWhatsApp, 3000);
            }
        } else if(connection === 'open') {
            console.log('API WA Ready');
        }
    });

    // PENTING: Menyimpan kredensial agar koneksi tidak diputus server setelah scan QR!
    sock.ev.on('creds.update', saveCreds);
}

connectToWhatsApp();

app.post('/send', async (req, res) => {
    try {
        let { phone, message } = req.body;
        
        if (!phone || !message) {
            return res.status(400).json({ success: false, error: "Phone and message required" });
        }

        if (phone.startsWith('0')) {
            phone = '62' + phone.substring(1);
        } else if (phone.startsWith('+')) {
            phone = phone.substring(1);
        }

        phone = phone.replace(/\D/g, '');
        const jid = `${phone}@s.whatsapp.net`;
        
        if (!sock || !sock.user || !sock.user.id) {
            return res.status(500).json({ 
                success: false, 
                error: "BOT BELUM LOGIN! Silakan scan QR Code di terminal NodeJS terlebih dahulu sebelum menembak API." 
            });
        }
        
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true, jid: jid });
        
    } catch (error) {
        console.error("Error ngirim JS:", error);
        res.status(500).json({ success: false, error: error.toString() });
    }
});

app.listen(3000, () => {
    console.log(`Server Baileys berjalan di Port 3000`);
});
