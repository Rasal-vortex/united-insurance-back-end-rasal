import { prisma } from "../../config/prisma.js";

export const vehicleModel = {
  findMany(customerId) {
    return prisma.vehicle.findMany({
      where: { customerId },
      orderBy: { createdAt: "desc" },
    });
  },
  findFirst(customerId, id) {
    return prisma.vehicle.findFirst({ where: { customerId, id } });
  },
  create(customerId, data) {
    return prisma.vehicle.create({ data: { ...data, customerId } });
  },
  update(id, data) {
    return prisma.vehicle.update({ where: { id }, data });
  },
  delete(id) {
    return prisma.vehicle.delete({ where: { id } });
  },
};
