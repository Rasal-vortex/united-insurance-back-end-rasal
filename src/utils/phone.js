/**
 * Normalize customer phone numbers to an E.164-like representation.
 * Ten-digit national numbers are treated as India (+91), matching this CRM's
 * current market. Other international numbers must include their country code.
 */
export function normalizePhoneNumber(value) {
  let digits = String(value ?? "").replace(/\D/g, "");
  if (digits.startsWith("00")) digits = digits.slice(2);
  if (digits.length === 10) digits = `91${digits}`;
  else if (digits.length === 11 && digits.startsWith("0"))
    digits = `91${digits.slice(1)}`;

  if (!/^\d{8,15}$/.test(digits)) {
    throw new TypeError("Phone number must contain 8 to 15 digits and a country code when international.");
  }

  return `+${digits}`;
}
