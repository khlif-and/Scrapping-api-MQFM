const fs = require('fs');
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');

const app = express();
app.use(express.json());

// Inisialisasi WhatsApp Client dengan Headless Chrome (Puppeteer)
// Menggunakan LocalAuth agar sesi tersimpan secara lokal dan persisten
const client = new Client({
    authStrategy: new LocalAuth({ clientId: "mqfm-api" }),
    puppeteer: { 
        headless: true, // Berjalan di background tanpa jendela browser visual
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    }
});

let isReady = false;

// Event saat QR Code perlu di-scan oleh HP
client.on('qr', (qr) => {
    isReady = false;
    console.log('\n=============================================');
    console.log('SCAN QR CODE INI MENGGUNAKAN WHATSAPP ANDA:');
    console.log('=============================================\n');
    qrcode.generate(qr, { small: true });
});

// Event saat Bot sukses login dan siap mengirim pesan
client.on('ready', () => {
    isReady = true;
    console.log('\n✅ BROWSER WHATSAPP TELAH SIAP! API BISA DIGUNAKAN!');
    console.log(`Berjalan sebagai: ${client.info.pushname} (${client.info.wid.user})\n`);
});

// Event jika sesi terputus (misal di-logout dari HP)
client.on('disconnected', (reason) => {
    isReady = false;
    console.log('\n❌ KONEKSI WA TERPUTUS:', reason);
    console.log('Menyiapkan ulang sesi WhatsApp...');
    client.initialize();
});

// Nyalakan bot
client.initialize();

// ==========================================
// ENDPOINT EXPRESS JS UNTUK DITEMBAK PYTHON
// ==========================================
app.post('/send', async (req, res) => {
    try {
        if (!isReady) {
            return res.status(503).json({ 
                success: false, 
                error: 'Bot WhatsApp belum di-scan atau belum siap.' 
            });
        }

        let { phone, message } = req.body;
        
        if (!phone || !message) {
            return res.status(400).json({ success: false, error: 'Phone dan message wajib diisi!' });
        }

        // Format nomor HP ke format internasional JID WhatsApp
        if (phone.startsWith('0')) {
            phone = '62' + phone.substring(1);
        } else if (phone.startsWith('+')) {
            phone = phone.substring(1);
        }
        
        // Buang karakter aneh selain angka
        phone = phone.replace(/\D/g, '');
        const jid = `${phone}@c.us`; // format c.us untuk kontak individual

        // Memastikan nomor terdaftar di WA
        const isRegistered = await client.isRegisteredUser(jid);
        if (!isRegistered) {
             return res.status(404).json({ success: false, error: `Nomor ${phone} tidak terdaftar di WhatsApp!` });
        }

        // Eksekusi pengiriman pesan
        const sentMsg = await client.sendMessage(jid, message);
        console.log(`[BERHASIL] Mengirim OTP ke ${phone}`);
        
        res.json({ success: true, jid: jid, id: sentMsg.id.id });
        
    } catch (error) {
        console.error("[GAGAL] Error saat ngirim:", error);
        res.status(500).json({ success: false, error: error.toString() });
    }
});

app.listen(3000, () => {
    console.log(`\nServer WhatsApp-Web.js berjalan di Port 3000`);
    console.log(`Menunggu inisialisasi browser... (Agak lama untuk pertama kalinya)`);
});
