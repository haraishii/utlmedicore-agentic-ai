const { MongoClient } = require('mongodb');

const mongoUrl = 'mongodb://utl:2041$$@218.161.3.98:27017/';
const dbName = 'DCA632971FC3';
const collectionName = 'posture_data';

async function startSimulation() {
    const client = new MongoClient(mongoUrl);
    try {
        await client.connect();
        console.log(`✅ Simulasi Multi-Node dimulai untuk Receiver: DCA632971FC3`);
        const col = client.db(dbName).collection(collectionName);
        
        setInterval(async () => {
            const now = new Date();

            // --- NODE 1 (Dari Gambar 1) ---
            const node1 = {
                timestamp: now,
                device_id: "DCA632971FC3",
                safe_Mac: "EDCE94AA94CB",
                band_Mac: "D612D90022EB",
                HR: 92 + Math.floor(Math.random() * 3), // Sedikit fluktuatif agar tampak hidup
                Blood_oxygen: 95,
                Posture_state: 10, // Unstable Temp
                Area: 4,           // Dining Table
                safe_battery: 75,
                band_battery: 16,
                Step: 27,
                Calories: 1,
                is_simulated: true
            };

            // --- NODE 2 (Dari Gambar 2) ---
            const node2 = {
                timestamp: now,
                device_id: "DCA632971FC3",
                safe_Mac: "C06EAC5BF9B0",
                band_Mac: "D612D90013FD",
                HR: 85 + Math.floor(Math.random() * 3),
                Blood_oxygen: 98,
                Posture_state: 1,  // Sitting
                Area: 7,           // Bedroom
                safe_battery: 100,
                band_battery: 88,
                Step: 112,
                Calories: 3,
                is_simulated: true
            };

            await col.insertMany([node1, node2]);
            console.log(`[Simulasi PUSH] 🚀 Node 1 SAFE ${node1.safe_Mac} | Node 2 SAFE ${node2.safe_Mac}`);

        }, 1500); // Kirim setiap 1.5 detik agar backend tidak shock lint

    } catch (err) {
        console.error("❌ Error Simulator:", err);
    }
}
startSimulation();