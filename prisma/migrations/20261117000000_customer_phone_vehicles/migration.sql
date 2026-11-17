BEGIN;

-- Abort before changing schema if existing phone values cannot be normalized
-- or if normalization would collapse multiple customer IDs into one account.
DO $$
DECLARE
  invalid_count INTEGER;
  conflict_count INTEGER;
BEGIN
  WITH normalized AS (
    SELECT
      "id",
      CASE
        WHEN digits ~ '^[0-9]{10}$' THEN '91' || digits
        WHEN digits ~ '^0[0-9]{10}$' THEN '91' || SUBSTRING(digits FROM 2)
        WHEN digits ~ '^[0-9]{8,15}$' THEN digits
        ELSE NULL
      END AS canonical
    FROM (
      SELECT "id",
        CASE WHEN raw_digits LIKE '00%' THEN SUBSTRING(raw_digits FROM 3) ELSE raw_digits END AS digits
      FROM (
        SELECT "id", regexp_replace("phone", '[^0-9]', '', 'g') AS raw_digits
        FROM "Customer"
      ) raw_source
    ) source
  )
  SELECT COUNT(*) INTO invalid_count FROM normalized WHERE canonical IS NULL;

  WITH normalized AS (
    SELECT
      CASE
        WHEN digits ~ '^[0-9]{10}$' THEN '91' || digits
        WHEN digits ~ '^0[0-9]{10}$' THEN '91' || SUBSTRING(digits FROM 2)
        WHEN digits ~ '^[0-9]{8,15}$' THEN digits
        ELSE NULL
      END AS canonical
    FROM (
      SELECT CASE WHEN raw_digits LIKE '00%' THEN SUBSTRING(raw_digits FROM 3) ELSE raw_digits END AS digits
      FROM (
        SELECT regexp_replace("phone", '[^0-9]', '', 'g') AS raw_digits
        FROM "Customer"
      ) raw_source
    ) source
  )
  SELECT COUNT(*) INTO conflict_count
  FROM (
    SELECT canonical
    FROM normalized
    WHERE canonical IS NOT NULL
    GROUP BY canonical
    HAVING COUNT(*) > 1
  ) conflicts;

  IF invalid_count > 0 OR conflict_count > 0 THEN
    RAISE EXCEPTION
      'Customer phone preflight failed: % invalid phone record(s), % normalized duplicate group(s). Resolve without deleting customers, then retry.',
      invalid_count,
      conflict_count;
  END IF;
END $$;

ALTER TABLE "Customer" ADD COLUMN "phoneNormalized" TEXT;

UPDATE "Customer"
SET "phoneNormalized" = CASE
  WHEN digits ~ '^[0-9]{10}$' THEN '+91' || digits
  WHEN digits ~ '^0[0-9]{10}$' THEN '+91' || SUBSTRING(digits FROM 2)
  WHEN digits ~ '^[0-9]{8,15}$' THEN '+' || digits
  ELSE NULL
END
FROM (
  SELECT "id",
    CASE WHEN raw_digits LIKE '00%' THEN SUBSTRING(raw_digits FROM 3) ELSE raw_digits END AS digits
  FROM (
    SELECT "id", regexp_replace("phone", '[^0-9]', '', 'g') AS raw_digits
    FROM "Customer"
  ) raw_source
) normalized
WHERE "Customer"."id" = normalized."id";

ALTER TABLE "Customer" ALTER COLUMN "phoneNormalized" SET NOT NULL;
CREATE UNIQUE INDEX "Customer_phoneNormalized_key" ON "Customer"("phoneNormalized");

CREATE TABLE "CustomerBranch" (
  "branchId" UUID NOT NULL,
  "customerId" UUID NOT NULL,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerBranch_pkey" PRIMARY KEY ("branchId", "customerId")
);

INSERT INTO "CustomerBranch" ("branchId", "customerId")
SELECT "branchId", "id" FROM "Customer";

CREATE INDEX "CustomerBranch_customerId_idx" ON "CustomerBranch"("customerId");
ALTER TABLE "CustomerBranch" ADD CONSTRAINT "CustomerBranch_branchId_fkey"
  FOREIGN KEY ("branchId") REFERENCES "Branch"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "CustomerBranch" ADD CONSTRAINT "CustomerBranch_customerId_fkey"
  FOREIGN KEY ("customerId") REFERENCES "Customer"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE "Vehicle" (
  "id" UUID NOT NULL,
  "customerId" UUID NOT NULL,
  "registrationNumber" TEXT NOT NULL,
  "vehicleType" TEXT NOT NULL,
  "details" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Vehicle_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "Vehicle_customerId_idx" ON "Vehicle"("customerId");
CREATE INDEX "Vehicle_registrationNumber_idx" ON "Vehicle"("registrationNumber");
ALTER TABLE "Vehicle" ADD CONSTRAINT "Vehicle_customerId_fkey"
  FOREIGN KEY ("customerId") REFERENCES "Customer"("id") ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;
