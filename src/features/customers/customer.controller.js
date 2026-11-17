import { customerService } from "./customer.service.js";
import { serializeCustomer } from "./customer.serializer.js";

export const customerController = {
  async list(req, res) {
    const result = await customerService.list(
      req.auth,
      req.validatedQuery ?? req.query,
    );
    res.json({
      success: true,
      data: result.records.map(serializeCustomer),
      meta: result.meta,
    });
  },
  async get(req, res) {
    const record = await customerService.get(req.auth, req.params.id);
    res.json({ success: true, data: serializeCustomer(record) });
  },
  async create(req, res) {
    const result = await customerService.create(req.auth, req.body);
    res.status(result.created ? 201 : 200).json({
      success: true,
      message: result.created ? "Customer created successfully" : "Existing customer account found",
      data: serializeCustomer(result.record),
    });
  },
  async update(req, res) {
    const record = await customerService.update(
      req.auth,
      req.params.id,
      req.body,
    );
    res.json({
      success: true,
      message: "Customer updated successfully",
      data: serializeCustomer(record),
    });
  },
  async remove(req, res) {
    await customerService.remove(req.auth, req.params.id);
    res.json({
      success: true,
      message: "Customer deleted successfully",
      data: null,
    });
  },
};
