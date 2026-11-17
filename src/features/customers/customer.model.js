import { prisma } from "../../config/prisma.js";

export const customerModel = {
  findMany(options) {
    return prisma.customer.findMany(options);
  },
  count(where) {
    return prisma.customer.count({ where });
  },
  findFirst(where, client = prisma) {
    return client.customer.findFirst({ where });
  },
  findFirstInBranch(id, branchId, client = prisma) {
    return client.customer.findFirst({
      where: { id, branchMemberships: { some: { branchId } } },
    });
  },
  findByNormalizedPhone(phoneNormalized, client = prisma) {
    return client.customer.findUnique({ where: { phoneNormalized } });
  },
  addBranchMembership(customerId, branchId, client = prisma) {
    return client.customerBranch.upsert({
      where: { branchId_customerId: { branchId, customerId } },
      create: { branchId, customerId },
      update: {},
    });
  },
  listBranchMemberships(customerId, client = prisma) {
    return client.customerBranch.findMany({ where: { customerId } });
  },
  removeBranchMembership(customerId, branchId, client = prisma) {
    return client.customerBranch.delete({
      where: { branchId_customerId: { branchId, customerId } },
    });
  },
  create(data, client = prisma) {
    return client.customer.create({ data });
  },
  update(id, data, client = prisma) {
    return client.customer.update({ where: { id }, data });
  },
  delete(id) {
    return prisma.customer.delete({ where: { id } });
  },
};
