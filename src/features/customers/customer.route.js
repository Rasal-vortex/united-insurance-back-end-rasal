import { Router } from "express";
import { authenticate } from "../../middlewares/auth.middleware.js";
import { authorize } from "../../middlewares/authorization.middleware.js";
import { validate } from "../../middlewares/zod.middleware.js";
import { asyncHandler } from "../../utils/async-handler.js";
import { customerController } from "./customer.controller.js";
import { vehicleController } from "../vehicles/vehicle.controller.js";
import {
  vehicleParamsSchema,
  createVehicleSchema,
  updateVehicleSchema,
} from "../vehicles/vehicle.schema.js";
import {
  customerQuerySchema,
  customerIdSchema,
  createCustomerSchema,
  updateCustomerSchema,
} from "./customer.schema.js";

const router = Router();

router.get(
  "/",
  authenticate,
  authorize("customer:read"),
  validate(customerQuerySchema, "query"),
  asyncHandler(customerController.list),
);
router.get(
  "/:id",
  authenticate,
  authorize("customer:read"),
  validate(customerIdSchema, "params"),
  asyncHandler(customerController.get),
);
router.post(
  "/",
  authenticate,
  authorize("customer:create"),
  validate(createCustomerSchema),
  asyncHandler(customerController.create),
);
router.patch(
  "/:id",
  authenticate,
  authorize("customer:update"),
  validate(customerIdSchema, "params"),
  validate(updateCustomerSchema),
  asyncHandler(customerController.update),
);
router.delete(
  "/:id",
  authenticate,
  authorize("customer:delete"),
  validate(customerIdSchema, "params"),
  asyncHandler(customerController.remove),
);

router.get(
  "/:id/vehicles",
  authenticate,
  authorize("vehicle:read"),
  validate(customerIdSchema, "params"),
  asyncHandler(vehicleController.list),
);
router.post(
  "/:id/vehicles",
  authenticate,
  authorize("vehicle:create"),
  validate(customerIdSchema, "params"),
  validate(createVehicleSchema),
  asyncHandler(vehicleController.create),
);
router.get(
  "/:id/vehicles/:vehicleId",
  authenticate,
  authorize("vehicle:read"),
  validate(vehicleParamsSchema, "params"),
  asyncHandler(vehicleController.get),
);
router.patch(
  "/:id/vehicles/:vehicleId",
  authenticate,
  authorize("vehicle:update"),
  validate(vehicleParamsSchema, "params"),
  validate(updateVehicleSchema),
  asyncHandler(vehicleController.update),
);
router.delete(
  "/:id/vehicles/:vehicleId",
  authenticate,
  authorize("vehicle:delete"),
  validate(vehicleParamsSchema, "params"),
  asyncHandler(vehicleController.remove),
);

export default router;
