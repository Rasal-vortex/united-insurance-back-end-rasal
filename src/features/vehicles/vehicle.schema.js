import { z } from "zod";

export const vehicleParamsSchema = z.object({
  id: z.string().uuid(),
  vehicleId: z.string().uuid().optional(),
});

export const createVehicleSchema = z.object({
  registrationNumber: z.string().trim().min(1).max(40),
  vehicleType: z.string().trim().min(1).max(80),
  details: z.string().trim().max(2000).nullable().optional(),
}).strict();

export const updateVehicleSchema = createVehicleSchema.partial().refine(
  (data) => Object.keys(data).length > 0,
  "At least one field is required",
);
