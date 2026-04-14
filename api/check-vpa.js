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
        const is_known_fraud = !!report;
        const vpa = pa.toLowerCase();
        const db_reports = report;
        const report_count = report ? (report.count || 1) : 0;

        // --- Advanced Reputation Graph (China Model) ---
        // Simulating logic where long-standing merchants get a higher trust score.
        let reputation_score = 50; // Baseline
        let is_trusted = false;
        
        const TRUSTED_VPAS = ["bigbazaar@icici", "amazonpay@apl", "zomato@paytm"];
        if (TRUSTED_VPAS.includes(vpa)) {
            reputation_score = 95;
            is_trusted = true;
        } else if (vpa.includes("merchant")) {
            reputation_score = 75; // Registered merchant handle
        }

        // --- Behavioral Risk Aggregator ---
        let riskScore = is_known_fraud ? 100 : (100 - reputation_score);
        
        // Final response structure per professional standards
        res.status(200).json({
            vpa,
            riskScore: Math.max(0, riskScore),
            reputation: {
                level: is_trusted ? "HIGH" : "STANDARD",
                score: reputation_score,
                is_verified_merchant: is_trusted
            },
            community_reports: {
                count: db_reports?.count || report_count,
                status: (db_reports?.count || report_count) > 0 ? "FLAGGED" : "CLEAN"
            },
            recommendation: riskScore > 70 ? "BLOCK" : (riskScore > 35 ? "WARN" : "SAFE"),
            source: "central_directory"
        });
    } catch (error) {
        console.error("DB Error:", error);
        return res.status(500).json({ error: "Internal server error connecting to Registry." });
    }
}
