import { vehicleService } from "./vehicle.service.js";
import { serializeVehicle } from "./vehicle.serializer.js";

export const vehicleController = {
  async list(req, res) {
    const vehicles = await vehicleService.list(req.auth, req.params.id);
    res.json({ success: true, data: vehicles.map(serializeVehicle) });
  },
  async get(req, res) {
    const vehicle = await vehicleService.get(
      req.auth,
      req.params.id,
      req.params.vehicleId,
    );
    res.json({ success: true, data: serializeVehicle(vehicle) });
  },
  async create(req, res) {
    const vehicle = await vehicleService.create(
      req.auth,
      req.params.id,
      req.body,
    );
    res.status(201).json({
      success: true,
      message: "Vehicle added successfully",
      data: serializeVehicle(vehicle),
    });
  },
  async update(req, res) {
    const vehicle = await vehicleService.update(
      req.auth,
      req.params.id,
      req.params.vehicleId,
      req.body,
    );
    res.json({
      success: true,
      message: "Vehicle updated successfully",
      data: serializeVehicle(vehicle),
    });
  },
  async remove(req, res) {
    await vehicleService.remove(req.auth, req.params.id, req.params.vehicleId);
    res.json({ success: true, message: "Vehicle deleted successfully", data: null });
  },
};
