import { ApiError } from "../../utils/ApiError.js";
import { customerService } from "../customers/customer.service.js";
import { vehicleModel } from "./vehicle.model.js";

export const vehicleService = {
  async list(auth, customerId) {
    await customerService.get(auth, customerId);
    return vehicleModel.findMany(customerId);
  },
  async get(auth, customerId, vehicleId) {
    await customerService.get(auth, customerId);
    const vehicle = await vehicleModel.findFirst(customerId, vehicleId);
    if (!vehicle) throw new ApiError(404, "Vehicle not found");
    return vehicle;
  },
  async create(auth, customerId, input) {
    await customerService.get(auth, customerId);
    return vehicleModel.create(customerId, input);
  },
  async update(auth, customerId, vehicleId, input) {
    await this.get(auth, customerId, vehicleId);
    return vehicleModel.update(vehicleId, input);
  },
  async remove(auth, customerId, vehicleId) {
    await this.get(auth, customerId, vehicleId);
    await vehicleModel.delete(vehicleId);
  },
};
