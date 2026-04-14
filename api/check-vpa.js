/**
 * /api/check-vpa?pa=handle@upi
 * Checks if a VPA exists in the centralized fraud database.
 */
const { MongoClient } = require('mongodb');

let cachedClient = null;
let cachedDb = null;

async function connectToDatabase() {
    if (cachedDb && cachedClient) return { client: cachedClient, db: cachedDb };

    if (!process.env.MONGODB_URI) {
        throw new Error("MONGODB_URI is not defined");
    }

    const client = new MongoClient(process.env.MONGODB_URI);
    await client.connect();
    const db = client.db('phishguard');

    cachedClient = client;
    cachedDb = db;
    return { client, db };
}

module.exports = async function handler(req, res) {
    const { pa } = req.query;

    if (!pa) {
        return res.status(400).json({ error: "VPA handle 'pa' is required." });
    }

    try {
        const { db } = await connectToDatabase();
        const collection = db.collection('fraud_reports');

        // Search for exact match
        const report = await collection.findOne({ vpa: pa.toLowerCase() });

        if (report) {
            return res.status(200).json({
                is_scammer: true,
                risk_score: 100,
                flags: report.flags || ["REPORTED_BY_COMMUNITY"],
                report_count: report.count || 1,
                last_reported: report.time
            });
        }

        return res.status(200).json({ is_scammer: false, message: "No central reports found." });
    } catch (error) {
        console.error("DB Error:", error);
        return res.status(500).json({ error: "Internal server error connecting to Registry." });
    }
}
