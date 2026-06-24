import express from 'express';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();

// Configuration
const PORT = process.env.WORKER_PORT || 3000;
const DB_PATH = process.env.DATABASE_PATH || '../rapidrepair.db';
const FULL_DB_PATH = path.resolve(__dirname, DB_PATH);

// Initialize database connection
let db = null;

async function initDatabase() {
  db = await open({
    filename: FULL_DB_PATH,
    driver: sqlite3.Database,
  });
  db.configure('busyTimeout', 5000);
  console.log('[Worker] Database connected:', FULL_DB_PATH);
  return db;
}

// Middleware
app.use(express.json());

// In-memory cache for estimates
const estimateCache = new Map();
const CACHE_TTL = (process.env.CACHE_TTL_SECONDS || 300) * 1000;

/**
 * Clear cache entry after TTL
 */
function setCacheWithTTL(key, value) {
  estimateCache.set(key, value);
  setTimeout(() => {
    estimateCache.delete(key);
  }, CACHE_TTL);
}

/**
 * Get all bookings with optional filtering
 */
app.get('/api/worker/bookings', async (req, res) => {
  try {
    const status = req.query.status;
    let query = `
      SELECT bookings.*, services.name AS service_name, services.category
      FROM bookings
      JOIN services ON services.slug = bookings.service_slug
    `;
    const params = [];

    if (status) {
      query += ' WHERE bookings.status = ?';
      params.push(status);
    }

    query += ' ORDER BY bookings.id DESC LIMIT 100';
    const bookings = await db.all(query, params);

    res.json({
      success: true,
      count: bookings.length,
      bookings,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('[Worker] Error fetching bookings:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Get booking statistics and analytics
 */
app.get('/api/worker/analytics', async (req, res) => {
  try {
    const totalBookings = await db.get('SELECT COUNT(*) as count FROM bookings');
    const bookingsByStatus = await db.all(`
      SELECT status, COUNT(*) as count
      FROM bookings
      GROUP BY status
    `);
    const bookingsByService = await db.all(`
      SELECT services.name, COUNT(*) as count
      FROM bookings
      JOIN services ON services.slug = bookings.service_slug
      GROUP BY bookings.service_slug
      ORDER BY count DESC
      LIMIT 10
    `);
    const totalRevenue = await db.get('SELECT COALESCE(SUM(estimate_price), 0) as total FROM bookings');
    const averageQuote = await db.get('SELECT COALESCE(AVG(estimate_price), 0) as avg FROM bookings');
    const averageServiceTime = await db.get('SELECT COALESCE(AVG(estimate_minutes), 0) as avg FROM bookings');

    const stats = {
      totalBookings: totalBookings.count,
      bookingsByStatus,
      bookingsByService,
      totalRevenue: totalRevenue.total,
      averageQuote: averageQuote.avg,
      averageServiceTime: averageServiceTime.avg,
    };

    res.json({
      success: true,
      analytics: stats,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('[Worker] Error calculating analytics:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Update booking status
 */
app.post('/api/worker/bookings/:id/status', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({ success: false, error: 'Status is required' });
    }

    const validStatuses = ['New', 'Confirmed', 'In Progress', 'Completed', 'Cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ success: false, error: 'Invalid status' });
    }

    const result = await db.run('UPDATE bookings SET status = ? WHERE id = ?', status, id);

    if (result.changes === 0) {
      return res.status(404).json({ success: false, error: 'Booking not found' });
    }

    const booking = await db.get(`
      SELECT bookings.*, services.name AS service_name
      FROM bookings
      JOIN services ON services.slug = bookings.service_slug
      WHERE bookings.id = ?
    `, id);

    console.log(`[Worker] Updated booking ${id} status to ${status}`);

    res.json({
      success: true,
      message: `Booking status updated to ${status}`,
      booking,
    });
  } catch (error) {
    console.error('[Worker] Error updating booking status:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Process booking notifications (extensible for email/SMS)
 */
app.post('/api/worker/bookings/:id/notify', async (req, res) => {
  try {
    const { id } = req.params;
    const { method } = req.body;

    const booking = await db.get(`
      SELECT bookings.*, services.name AS service_name
      FROM bookings
      JOIN services ON services.slug = bookings.service_slug
      WHERE bookings.id = ?
    `, id);

    if (!booking) {
      return res.status(404).json({ success: false, error: 'Booking not found' });
    }

    // Log notification intent
    console.log(`[Worker] Notification queued for booking ${id} via ${method || 'all channels'}`);

    // Simulated notification processing
    const notification = {
      booking_id: id,
      customer_name: booking.customer_name,
      service_name: booking.service_name,
      phone: booking.phone,
      message: `Your booking for ${booking.service_name} is confirmed. Total: ₹${booking.estimate_price}`,
      timestamp: new Date().toISOString(),
    };

    res.json({
      success: true,
      message: 'Notification queued successfully',
      notification,
    });
  } catch (error) {
    console.error('[Worker] Error queuing notification:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Health check endpoint
 */
app.get('/api/worker/health', async (req, res) => {
  try {
    // Verify database connection
    await db.get('SELECT 1');

    res.json({
      status: 'healthy',
      service: 'RapidRepair Worker',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
    });
  }
});

/**
 * Graceful shutdown
 */
process.on('SIGINT', async () => {
  console.log('[Worker] Shutting down gracefully...');
  if (db) await db.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('[Worker] Shutting down (SIGTERM)...');
  if (db) await db.close();
  process.exit(0);
});

// Start server
async function startServer() {
  await initDatabase();
  
  app.listen(PORT, () => {
    console.log(`[Worker] RapidRepair Worker running on port ${PORT}`);
    console.log(`[Worker] Database: ${FULL_DB_PATH}`);
    console.log(`[Worker] Health check: http://localhost:${PORT}/api/worker/health`);
  });
}

startServer().catch((error) => {
  console.error('[Worker] Failed to start:', error);
  process.exit(1);
});
