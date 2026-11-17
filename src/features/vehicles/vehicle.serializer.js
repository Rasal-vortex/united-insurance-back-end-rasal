export function serializeVehicle(record) {
  if (!record) return null;
  return {
    id: record.id,
    customerId: record.customerId,
    registrationNumber: record.registrationNumber,
    vehicleType: record.vehicleType,
    details: record.details,
    createdAt: record.createdAt,
    updatedAt: record.updatedAt,
  };
}
