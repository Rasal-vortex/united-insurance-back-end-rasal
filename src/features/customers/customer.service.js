import { getPagination, getPaginationMeta } from "../../utils/pagination.js";
import { ApiError } from "../../utils/ApiError.js";
import { customerModel } from "./customer.model.js";
import { staffModel } from "../staff/staff.model.js";
import { prisma } from "../../config/prisma.js";
import { normalizePhoneNumber } from "../../utils/phone.js";

function getScope(auth) {
  if (auth.userType === "ADMIN") return {};
  return { branchId: auth.branchId };
}

export const customerService = {
  async list(auth, query) {
    const where = auth.userType === "ADMIN"
      ? {}
      : { branchMemberships: { some: { branchId: auth.branchId } } };
    if (query.status) where.status = query.status;
    if (query.search)
      where.OR = [
        { name: { contains: query.search, mode: "insensitive" } },
        { phone: { contains: query.search, mode: "insensitive" } },
        { email: { contains: query.search, mode: "insensitive" } },
      ];
    const { skip, take } = getPagination(query.page, query.limit);
    const orderBy = { [query.sortBy || "createdAt"]: query.sortOrder };
    const [records, total] = await Promise.all([
      customerModel.findMany({ where, skip, take, orderBy }),
      customerModel.count(where),
    ]);
    return { records, meta: getPaginationMeta(total, query.page, query.limit) };
  },
  async get(auth, id) {
    const record = auth.userType === "ADMIN"
      ? await customerModel.findFirst({ id })
      : await customerModel.findFirst({
          id,
          branchMemberships: { some: { branchId: auth.branchId } },
        });
    if (!record) throw new ApiError(404, "Customer not found");
    return record;
  },
  async create(auth, input) {
    const branchId = auth.userType === "ADMIN" ? input.branchId : auth.branchId;
    if (!branchId)
      throw new ApiError(400, "branchId is required for admin-created records");
    await validateStaff(auth, input.staffId, branchId);
    const phoneNormalized = normalizePhoneNumber(input.phone);
    const existing = await customerModel.findByNormalizedPhone(phoneNormalized);
    if (existing) {
      await customerModel.addBranchMembership(existing.id, branchId);
      return { record: existing, created: false };
    }

    try {
      const record = await prisma.$transaction(async (tx) => {
        const customer = await customerModel.create(
          { ...input, branchId, phoneNormalized },
          tx,
        );
        await customerModel.addBranchMembership(customer.id, branchId, tx);
        return customer;
      });
      return { record, created: true };
    } catch (error) {
      if (error?.code !== "P2002") throw error;
      const record = await customerModel.findByNormalizedPhone(phoneNormalized);
      if (!record) throw error;
      await customerModel.addBranchMembership(record.id, branchId);
      return { record, created: false };
    }
  },

  async update(auth, id, input) {
    const current = await this.get(auth, id);
    await validateStaff(auth, input.staffId, current.branchId);
    delete input.branchId;
    if (input.phone) {
      input.phoneNormalized = normalizePhoneNumber(input.phone);
      const existing = await customerModel.findByNormalizedPhone(input.phoneNormalized);
      if (existing && existing.id !== id)
        throw new ApiError(409, "That phone number already belongs to another customer account");
    }
    return customerModel.update(id, input);
  },
  async remove(auth, id) {
    const customer = await this.get(auth, id);
    if (auth.userType === "BRANCH") {
      const memberships = await customerModel.listBranchMemberships(id);
      if (memberships.length > 1 || customer.branchId !== auth.branchId) {
        await customerModel.removeBranchMembership(id, auth.branchId);
        return;
      }
    }
    await customerModel.delete(customer.id);
  },
};

async function validateStaff(auth, staffId, branchId) {
  if (!staffId) return;
  const scope = auth.userType === "ADMIN" ? { branchId } : getScope(auth);
  const staff = await staffModel.findFirst({ id: staffId, ...scope });
  if (!staff)
    throw new ApiError(400, "staffId is invalid or outside this branch");
}
