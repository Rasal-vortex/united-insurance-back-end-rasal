import "dotenv/config";
import pg from "pg";
import { normalizePhoneNumber } from "../src/utils/phone.js";

if (!process.env.DATABASE_URL) {
  console.error("Customer phone audit requires DATABASE_URL in the environment or dotenv configuration.");
  process.exit(2);
}

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  connectionTimeoutMillis: 5000,
  max: 1,
});

try {
  // Read-only audit. It reports IDs/branch IDs and masked phone suffixes only.
  const { rows } = await pool.query('SELECT "id", "branchId", "phone" FROM "Customer"');
  const groups = new Map();
  const invalid = [];

  for (const row of rows) {
    let normalized;
    try {
      normalized = normalizePhoneNumber(row.phone);
    } catch {
      invalid.push({ customerId: row.id, branchId: row.branchId });
      continue;
    }
    const records = groups.get(normalized) ?? [];
    records.push({ customerId: row.id, branchId: row.branchId });
    groups.set(normalized, records);
  }

  const duplicateGroups = [...groups.entries()]
    .filter(([, records]) => records.length > 1)
    .map(([normalized, records]) => ({
      phoneSuffix: normalized.slice(-4),
      records,
    }));

  console.log(JSON.stringify({
    customerRecords: rows.length,
    duplicatePhoneGroups: duplicateGroups,
    invalidPhoneRecords: invalid,
  }, null, 2));

  if (duplicateGroups.length || invalid.length) process.exitCode = 1;
} catch (error) {
  console.error(`Customer phone audit failed${error.code ? ` (${error.code})` : ""}.`);
  process.exitCode = 2;
} finally {
  await pool.end();
}
