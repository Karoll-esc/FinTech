/**
 * MongoDB Initialization Script - Phase 7 (TASK-061-065)
 * 
 * Creates collections, indexes, and sample data for:
 * - Cards collection
 * - Card transactions
 * - Card audit trail
 * 
 * Run with: node scripts/init-mongodb.js
 */

const { MongoClient, ObjectId } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = 'fraud_detection';

async function initializeDatabase() {
  const client = new MongoClient(MONGODB_URI);

  try {
    console.log('📡 Connecting to MongoDB...');
    await client.connect();
    const db = client.db(DATABASE_NAME);

    console.log('🔧 Initializing collections...');

    // Drop existing collections (for development/testing)
    try {
      await db.collection('cards').drop();
      console.log('  ✓ Dropped cards collection');
    } catch (e) {
      // Collection doesn't exist, ignore
    }

    try {
      await db.collection('card_transactions').drop();
      console.log('  ✓ Dropped card_transactions collection');
    } catch (e) {
      // Collection doesn't exist, ignore
    }

    try {
      await db.collection('card_audits').drop();
      console.log('  ✓ Dropped card_audits collection');
    } catch (e) {
      // Collection doesn't exist, ignore
    }

    // Create cards collection with validation
    console.log('📝 Creating cards collection...');
    await db.createCollection('cards', {
      validator: {
        $jsonSchema: {
          bsonType: 'object',
          required: [
            'card_id',
            'user_id',
            'card_number',
            'cardholder_name',
            'current_balance',
            'expiry_month',
            'expiry_year',
            'status',
            'card_type',
            'created_at',
          ],
          properties: {
            card_id: { bsonType: 'string', description: 'Unique card identifier' },
            user_id: { bsonType: 'string', description: 'User who owns card' },
            card_number: { bsonType: 'string', description: 'Masked card number' },
            cardholder_name: { bsonType: 'string', description: 'Name on card' },
            current_balance: { bsonType: 'decimal', description: 'Available balance' },
            expiry_month: {
              bsonType: 'int',
              description: 'Expiry month (1-12)',
              minimum: 1,
              maximum: 12,
            },
            expiry_year: {
              bsonType: 'int',
              description: 'Expiry year (e.g., 2027)',
              minimum: 2024,
            },
            status: {
              bsonType: 'string',
              enum: ['ACTIVE', 'BLOCKED', 'EXPIRED', 'PENDING'],
              description: 'Card status',
            },
            card_type: {
              bsonType: 'string',
              enum: ['DEBIT', 'CREDIT'],
              description: 'Card type',
            },
            created_at: { bsonType: 'date', description: 'Creation timestamp' },
            updated_at: { bsonType: 'date', description: 'Last update timestamp' },
          },
        },
      },
    });
    console.log('  ✓ Cards collection created');

    // Create card_transactions collection
    console.log('📝 Creating card_transactions collection...');
    await db.createCollection('card_transactions');
    console.log('  ✓ Card transactions collection created');

    // Create card_audits collection
    console.log('📝 Creating card_audits collection...');
    await db.createCollection('card_audits');
    console.log('  ✓ Card audits collection created');

    // Create indexes
    console.log('🔍 Creating indexes...');

    // Cards indexes
    await db.collection('cards').createIndex({ user_id: 1 });
    console.log('  ✓ Index: cards.user_id');

    await db.collection('cards').createIndex({ card_id: 1 }, { unique: true });
    console.log('  ✓ Index: cards.card_id (unique)');

    await db.collection('cards').createIndex({ status: 1 });
    console.log('  ✓ Index: cards.status');

    await db.collection('cards').createIndex({ created_at: -1 });
    console.log('  ✓ Index: cards.created_at (descending)');

    // Transactions indexes
    await db.collection('card_transactions').createIndex({ card_id: 1 });
    console.log('  ✓ Index: card_transactions.card_id');

    await db.collection('card_transactions').createIndex({ timestamp: -1 });
    console.log('  ✓ Index: card_transactions.timestamp (descending)');

    // Audits indexes
    await db.collection('card_audits').createIndex({ card_id: 1 });
    console.log('  ✓ Index: card_audits.card_id');

    await db.collection('card_audits').createIndex({ user_id: 1 });
    console.log('  ✓ Index: card_audits.user_id');

    // Insert sample data
    console.log('📊 Inserting sample data...');

    const now = new Date();
    const expiryYear = now.getFullYear() + 3;

    const sampleCards = [
      {
        card_id: 'card_20260128_001',
        user_id: 'user_001',
        card_number: '4532-XXXX-XXXX-1234',
        cardholder_name: 'Juan Pérez',
        current_balance: 1250.5,
        expiry_month: 12,
        expiry_year: expiryYear,
        status: 'ACTIVE',
        card_type: 'DEBIT',
        created_at: new Date('2024-01-15'),
        updated_at: now,
      },
      {
        card_id: 'card_20260128_002',
        user_id: 'user_001',
        card_number: '5412-XXXX-XXXX-5678',
        cardholder_name: 'Juan Pérez',
        current_balance: 5000.0,
        expiry_month: 6,
        expiry_year: expiryYear,
        status: 'ACTIVE',
        card_type: 'CREDIT',
        created_at: new Date('2024-03-20'),
        updated_at: now,
      },
      {
        card_id: 'card_20260128_003',
        user_id: 'user_001',
        card_number: '3714-XXXX-XXXX-9012',
        cardholder_name: 'Juan Pérez',
        current_balance: 0.0,
        expiry_month: 3,
        expiry_year: expiryYear,
        status: 'BLOCKED',
        card_type: 'DEBIT',
        created_at: new Date('2024-05-10'),
        updated_at: new Date('2026-01-25'),
      },
      {
        card_id: 'card_20260128_004',
        user_id: 'user_002',
        card_number: '6011-XXXX-XXXX-3456',
        cardholder_name: 'María García',
        current_balance: 2500.75,
        expiry_month: 9,
        expiry_year: expiryYear,
        status: 'ACTIVE',
        card_type: 'DEBIT',
        created_at: new Date('2024-02-01'),
        updated_at: now,
      },
    ];

    const cardResult = await db.collection('cards').insertMany(sampleCards);
    console.log(
      `  ✓ Inserted ${cardResult.insertedCount} sample cards`
    );

    // Sample transactions
    const sampleTransactions = [
      {
        card_id: 'card_20260128_001',
        transaction_id: 'txn_20260128_001',
        transaction_date: new Date('2026-01-28T14:30:00Z'),
        description: 'Supermarket Purchase',
        amount: -45.99,
        merchant: 'Carrefour',
        status: 'Completed',
        user_id: 'user_001',
        created_at: new Date('2026-01-28T14:30:00Z'),
      },
      {
        card_id: 'card_20260128_001',
        transaction_id: 'txn_20260128_002',
        transaction_date: new Date('2026-01-27T10:15:00Z'),
        description: 'Gas Station',
        amount: -65.0,
        merchant: 'Exxon',
        status: 'Completed',
        user_id: 'user_001',
        created_at: new Date('2026-01-27T10:15:00Z'),
      },
      {
        card_id: 'card_20260128_002',
        transaction_id: 'txn_20260128_003',
        transaction_date: new Date('2026-01-26T20:00:00Z'),
        description: 'Restaurant Payment',
        amount: -125.5,
        merchant: 'Casa Ñoña',
        status: 'Completed',
        user_id: 'user_001',
        created_at: new Date('2026-01-26T20:00:00Z'),
      },
    ];

    const transResult = await db
      .collection('card_transactions')
      .insertMany(sampleTransactions);
    console.log(
      `  ✓ Inserted ${transResult.insertedCount} sample transactions`
    );

    // Sample audit records
    const sampleAudits = [
      {
        card_id: 'card_20260128_003',
        user_id: 'user_001',
        action: 'CARD_BLOCKED',
        reason: 'User requested block',
        timestamp: new Date('2026-01-25T09:00:00Z'),
        metadata: { blocked_by: 'user_request' },
      },
      {
        card_id: 'card_20260128_001',
        user_id: 'user_001',
        action: 'TRANSACTION_PROCESSED',
        reason: 'Transfer initiated',
        timestamp: new Date('2026-01-28T14:30:00Z'),
        metadata: {
          amount: 100.0,
          destination: 'account_xyz',
          fraud_score: 0.15,
        },
      },
    ];

    const auditResult = await db.collection('card_audits').insertMany(sampleAudits);
    console.log(
      `  ✓ Inserted ${auditResult.insertedCount} sample audit records`
    );

    // TTL index for audit logs (auto-delete after 90 days)
    await db.collection('card_audits').createIndex(
      { timestamp: 1 },
      { expireAfterSeconds: 90 * 24 * 60 * 60 }
    );
    console.log('  ✓ TTL Index: card_audits.timestamp (90 days)');

    console.log('\n✅ Database initialization complete!');
    console.log(`📊 Summary:`);
    console.log(
      `   - Cards: ${sampleCards.length} test cards created`
    );
    console.log(
      `   - Transactions: ${sampleTransactions.length} sample transactions`
    );
    console.log(
      `   - Audit Records: ${sampleAudits.length} sample audit entries`
    );
    console.log(
      `\n🔍 Collections ready for testing in MongoDB: ${DATABASE_NAME}`
    );
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Run initialization
initializeDatabase();
