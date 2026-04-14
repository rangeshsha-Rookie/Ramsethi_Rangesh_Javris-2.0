/**
 * /api/report-fraud
 * POST: Logs a new fraud report to the centralized database.
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
    if (req.method !== 'POST') {
        return res.status(405).json({ error: "Method not allowed. Use POST." });
    }

    const { type, target, flags, evidence } = req.body;

    if (!type || !target) {
        return res.status(400).json({ error: "Missing required fields: 'type' and 'target'." });
    }

    try {
        const { db } = await connectToDatabase();
        const collection = db.collection('fraud_reports');

        // Target can be a VPA or a URL
        const query = { vpa: target.toLowerCase() };
        
        const update = {
            $set: {
                type: type,
                evidence: evidence || "Community Report",
                time: Date.now()
            },
            $addToSet: { flags: { $each: flags || ["USER_REPORTED"] } },
            $inc: { count: 1 }
        };

        const result = await collection.updateOne(query, update, { upsert: true });

        return res.status(200).json({
            ok: true,
            message: "Report logged successfully.",
            id: result.upsertedId || "updated"
        });
    } catch (error) {
        console.error("DB Error:", error);
        return res.status(500).json({ error: "Internal server error logging report." });
    }
}
