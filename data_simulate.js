const { MongoClient } = require('mongodb');

const mongoUrl = 'mongodb://utl:2041$$@218.161.3.98:27017/';
const dbName = 'DCA632971FC3';
const collectionName = 'posture_data';
const DEVICE_ID = "SIM_DCA632971FC3";

async function startSimulation() {
    const client = new MongoClient(mongoUrl);
    try {
        await client.connect();
        console.log(`✅ Simulasi Multi-Fase dimulai untuk: ${DEVICE_ID}`);
        const col = client.db(dbName).collection(collectionName);
        
        let hr = 75;
        let spo2 = 98;
        let state = "NORMAL"; // NORMAL -> DETERIORATING -> EMERGENCY
        let ticks = 0;

        setInterval(async () => {
            ticks++;
            
            // --- LOGIKA PERUBAHAN FASE ---
            if (ticks < 30) {
                state = "NORMAL";
                hr = 75 + Math.floor(Math.random() * 5);
                spo2 = 98;
                posture = 1; // Sitting
                area = 2;    // Laboratory
            } else if (ticks < 60) {
                state = "DETERIORATING"; // Memicu Predictor Agent
                hr += 1;   // HR perlahan naik (Tachycardia trend)
                spo2 -= 0.2; // SpO2 perlahan turun (Hypoxia trend)
                posture = 2; // Standing
                area = 3;    // Corridor
            } else if (ticks < 70) {
                state = "EMERGENCY"; // Memicu Monitor & Alert Agent
                hr = 125;
                spo2 = 85;
                posture = 5; // FALL!
                area = 6;    // Bathroom (Contextual Risk)
            } else {
                ticks = 0; // Reset siklus
            }

            const dummyData = {
                timestamp: new Date(),
                device_ID: DEVICE_ID,
                HR: Math.floor(hr),
                Blood_oxygen: Math.floor(spo2),
                Posture_state: posture,
                Area: area,
                // Variabel fisik tetap disertakan agar data terlihat real
                ACC_X: 0.01, ACC_Y: 0.02, ACC_Z: -1,
                MAG_X: 50, MAG_Y: -400, MAG_Z: -150,
                safe_battery: 80, band_battery: 30,
                Step: 100 + ticks,
                is_simulated: true
            };

            await col.insertOne(dummyData);
            console.log(`[${state}] Sent: HR ${dummyData.HR} | SpO2 ${dummyData.Blood_oxygen} | Posture ${posture}`);

        }, 1000); // Kirim setiap 1 detik

    } catch (err) {
        console.error("❌ Error:", err);
    }
}
startSimulation();