import { z } from "zod";
import { baseListQuerySchema } from "../../utils/query-params.js";
import { normalizePhoneNumber } from "../../utils/phone.js";

const phoneSchema = z.string().trim().min(5).transform((value, context) => {
  try {
    return normalizePhoneNumber(value);
  } catch (error) {
    context.addIssue({ code: "custom", message: error.message });
    return z.NEVER;
  }
});

export const createCustomerSchema = z
  .object({
    branchId: z.string().uuid().optional(),
    name: z.string().trim().min(1),
    phone: phoneSchema,
    email: z.string().email().nullable().optional(),
    dob: z.coerce.date().nullable().optional(),
    gender: z.string().trim().nullable().optional(),
    address: z.string().trim().nullable().optional(),
    notes: z.string().trim().nullable().optional(),
    status: z.enum(["ACTIVE", "INACTIVE"]).optional(),
    staffId: z.string().uuid().nullable().optional(),
  })
  .strict();

export const updateCustomerSchema = createCustomerSchema
  .partial()
  .refine(
    (data) => Object.keys(data).length > 0,
    "At least one field is required",
  );

export const customerIdSchema = z.object({ id: z.string().uuid() });

export const customerQuerySchema = baseListQuerySchema
  .extend({
    status: z.enum(["ACTIVE", "INACTIVE"]).optional(),
    sortBy: z.enum(["name", "createdAt", "updatedAt"]).optional(),
  })
  .strict();
