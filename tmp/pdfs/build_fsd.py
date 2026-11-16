from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape
from pathlib import Path

OUT = Path('output/pdf/insurance-crm-backend-fsd.pdf')
NAVY = HexColor('#142D4E')
BLUE = HexColor('#2463A6')
PALE = HexColor('#EAF1F8')
INK = HexColor('#243447')
MUTED = HexColor('#5D6B7A')
GREEN = HexColor('#1E7158')
ORANGE = HexColor('#A76216')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitleX', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=27, leading=32, textColor=NAVY, alignment=TA_LEFT, spaceAfter=12))
styles.add(ParagraphStyle(name='SubtitleX', parent=styles['Normal'], fontSize=12, leading=18, textColor=MUTED, spaceAfter=12))
styles.add(ParagraphStyle(name='H1X', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=19, leading=24, textColor=NAVY, spaceBefore=6, spaceAfter=10, keepWithNext=True))
styles.add(ParagraphStyle(name='H2X', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=8, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name='BodyX', parent=styles['BodyText'], fontSize=9.2, leading=13.2, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name='SmallX', parent=styles['BodyText'], fontSize=8, leading=10.5, textColor=INK, spaceAfter=2))
styles.add(ParagraphStyle(name='TinyX', parent=styles['BodyText'], fontSize=7.3, leading=9, textColor=INK, spaceAfter=1))
styles.add(ParagraphStyle(name='CodeX', parent=styles['BodyText'], fontName='Courier', fontSize=8.4, leading=12.4, textColor=NAVY, leftIndent=9, rightIndent=7, backColor=PALE, borderPadding=7, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name='CalloutX', parent=styles['BodyText'], fontSize=9, leading=13, textColor=NAVY, backColor=PALE, borderPadding=8, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name='TableHeadX', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=7.7, leading=9.5, textColor=colors.white))
styles.add(ParagraphStyle(name='TableX', parent=styles['BodyText'], fontSize=7.2, leading=9, textColor=INK))
styles.add(ParagraphStyle(name='CoverMetaX', parent=styles['BodyText'], fontSize=9, leading=14, textColor=MUTED))


def p(text, style='BodyX'):
    return Paragraph(text, styles[style])
def bullet(text):
    return p('&bull; ' + text)
def grid(headers, rows, widths, font='TableX'):
    data = [[p(escape(str(x)), 'TableHeadX') for x in headers]]
    for row in rows:
        data.append([p(str(x), font) for x in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY), ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.35,HexColor('#CFD8E2')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,HexColor('#F5F8FB')]),
        ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    return t

def footer(canvas, doc):
    canvas.saveState()
    w,h=letter
    canvas.setStrokeColor(HexColor('#D6DEE7')); canvas.setLineWidth(.5)
    canvas.line(.65*inch,.52*inch,w-.65*inch,.52*inch)
    canvas.setFont('Helvetica',7.5); canvas.setFillColor(MUTED)
    canvas.drawString(.68*inch,.34*inch,'United Insurance CRM Backend | Functional Specification')
    canvas.drawRightString(w-.68*inch,.34*inch,f'{doc.page}')
    canvas.restoreState()

doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch, topMargin=.65*inch, bottomMargin=.72*inch, title='Insurance CRM Backend - Functional Specification', author='Project codebase analysis')
story=[]
# Cover
story += [Spacer(1,.75*inch), p('FUNCTIONAL SPECIFICATION', 'CoverMetaX'), Spacer(1,10), p('Insurance CRM<br/>Backend', 'CoverTitleX'), p('What the project does, how each workflow behaves, and the exact path an API request follows through the code.', 'SubtitleX'), Spacer(1,18)]
story += [grid(['PROJECT PROFILE','OBSERVED IMPLEMENTATION'],[
    ['Application','Branch-centric insurance CRM REST API'],
    ['Runtime','Node.js ES modules, Express 5'],
    ['Database','PostgreSQL via Prisma 7 and pg adapter'],
    ['Validation and access','Zod input validation; JWT authentication; named role permissions'],
    ['Document storage','Local disk uploads under public/uploads by default'],
    ['Analysis date','11 November 2026'],
], [1.65*inch,5.0*inch])]
story += [Spacer(1,18), p('<b>Scope note.</b> This document describes behavior visible in the repository at analysis time. It does not infer a frontend, insurer integration, scheduled job, or business process that is not implemented in the backend.', 'CalloutX'), Spacer(1,26), p('Prepared from the route, controller, service, model, serializer, middleware, Prisma schema, migration, and project documentation files.', 'CoverMetaX'), PageBreak()]

story += [p('1. Executive summary','H1X'), p('This is a feature-based monolithic API for an insurance office organized by branches. Admins manage branches and can see cross-branch operational data. Branch accounts operate within their own branch. The backend stores customers, sales leads, insurance policies, policy renewals, claims, follow-ups, documents, activities, and commissions. It also exposes dashboard and report summaries.'), p('A normal API call is handled synchronously: Express applies global middleware, the matching feature route validates the caller and input, a controller delegates to a service, the service applies business rules and branch scope, a model calls Prisma, and the response serializer returns a stable JSON shape.'), p('2. Product boundary and actors','H1X'), grid(['Actor','Capabilities in code'],[
 ['Admin','Sign in with email/password; create, read, and update branches; access read and reporting endpoints across branches; create selected operational records by supplying a branchId.'],
 ['Branch user','Sign in with username/password; manage day-to-day records for its own branch, subject to feature permissions; read dashboards and reports scoped to its branch.'],
 ['Staff record','A CRM assignment/contact associated with branch records. Staff are not accounts and have no login route.'],
 ['Customer / external user','No customer login, customer portal, or public customer API is implemented.'],
], [1.2*inch,5.45*inch]), Spacer(1,8), p('3. System and request architecture','H1X'), p('Startup and global pipeline','H2X'), p('<b>Process:</b> server.js loads environment variables, imports src/app.js and the shared Prisma client, validates PORT, starts Express (trying the next port when the configured port is already in use), prints local/network addresses, and disconnects Prisma during SIGINT/SIGTERM shutdown.'), p('<b>HTTP setup:</b> src/app.js configures CORS, JSON parsing (1 MB), URL-encoded parsing, Morgan request logs, GET /health, Swagger UI at /api-docs, then mounts /api routes. Not-found and error middleware run after API routes.'), p('Exact path through the backend','H2X'), p('Client -> server.js -> src/app.js global middleware -> src/routes/index.js -> src/features/<feature>/<feature>.route.js -> authenticate -> authorize -> validate -> asyncHandler -> <feature>.controller.js -> <feature>.service.js -> <feature>.model.js -> src/config/prisma.js -> PostgreSQL -> serializer -> JSON response', 'CodeX'), p('Route middleware varies by operation. Login skips JWT authorization and runs body validation before its controller. Document upload authenticates and authorizes before multer parsing/content checks. Health does not pass through the /api router.'), PageBreak()]

story += [p('4. Exact file-to-file example: create a policy','H1X'), p('For POST /api/policies, this is the concrete execution path based on the implementation:'), p('1. server.js starts the Express app exported by src/app.js.<br/>2. src/app.js parses JSON, logs the request, and mounts src/routes/index.js at /api.<br/>3. src/routes/index.js mounts policy.route.js at /policies.<br/>4. policy.route.js matches POST / and calls authenticate, authorize("policy:create"), validate(createPolicySchema), then asyncHandler(policyController.create).<br/>5. auth.middleware.js verifies the Bearer JWT and places claims on req.auth. authorization.middleware.js confirms the claim userType is allowed. zod.middleware.js parses the body and replaces req.body with validated data.<br/>6. async-handler.js forwards rejected async work into Express error handling.<br/>7. policy.controller.js calls policyService.create(req.auth, req.body).<br/>8. policy.service.js determines branchId from the branch token or admin-supplied body; verifies the customer belongs to that branch; opens a Prisma transaction.<br/>9. policy.model.js creates the Policy row using the transaction client. The service then creates a Renewal row due on the policy expiryDate and an Activity row noting policy creation, in the same transaction.<br/>10. src/config/prisma.js provides the Prisma client backed by PostgreSQL. If any transactional write fails, the transaction rolls back.<br/>11. policy.serializer.js shapes the policy response; the controller sends HTTP 201 with { success, message, data }.', 'SmallX'), p('Result shape: { success: true, message: "Policy created successfully", data: <serialized policy> }. A duplicate policyNumber within the same branch violates the branchId + policyNumber unique key and is returned as HTTP 409 by error.middleware.js.', 'CalloutX'), p('Cross-cutting response and error behavior','H2X'), grid(['Condition','Observed response behavior'],[
 ['Successful list','{ success: true, data: [...], meta: { page, limit, total, totalPages } }'],
 ['Successful create','HTTP 201, success true, feature message, serialized data'],
 ['Validation error','HTTP 400, message "Validation failed", errors list field/message'],
 ['No/invalid token','HTTP 401'], ['Insufficient role','HTTP 403'], ['Missing scoped record','Usually HTTP 404'],
 ['Duplicate unique value','HTTP 409, generic duplicate message'],
 ['Unexpected failure','HTTP 500 with generic response; error logged server-side'],
], [1.65*inch,5*inch]), p('List endpoints commonly accept page, limit, search, sortBy, sortOrder, and a feature-specific status. Zod schemas restrict sortBy/status per feature. Pagination converts page and limit to Prisma skip/take.', 'BodyX'), PageBreak()]

story += [p('5. Business workflows','H1X'), p('Lead intake and conversion','H2X'), p('A branch creates and works a lead (NEW, CONTACTED, QUALIFIED, CONVERTED, LOST), optionally assigning staff and a next follow-up date. POST /api/leads/:id/convert checks the lead is visible and not already converted. In one database transaction it creates a Customer using the lead contact details, updates the Lead to CONVERTED with convertedCustomerId/convertedAt, and writes a LEAD_CONVERTED activity. A repeat conversion returns 409.'), p('Customer management','H2X'), p('Customers belong to one branch and may be assigned to a staff record in that branch. Branch identity determines branchId on create; admin creation requires branchId. Updates first verify record access and validate any staff relation against that branch. Deletion behavior can cascade through dependent policy/claim/follow-up/document/activity relations as defined by the database schema.'), p('Policy and renewal lifecycle','H2X'), p('A policy belongs to a customer in the same branch. Creating the policy is transactional and also creates one initial renewal record with dueDate equal to policy.expiryDate plus a POLICY_CREATED activity. Renewal records can be listed/read and updated; they cannot be created or deleted through a renewal route. Renewal status and reminders are stored fields managed through data/API updates; no scheduled renewal status updater or notification sender appears in the repository.'), p('Claims','H2X'), p('Claims require a customer in the selected branch. An optional policy must also belong to that branch and to the same customer. Status values are REPORTED, UNDER_REVIEW, APPROVED, REJECTED, SETTLED. API supports list, get, create, update; there is no delete route.'), p('Follow-ups','H2X'), p('A follow-up has title and dueAt, optional customer/lead/staff relations, and PENDING/COMPLETED/CANCELLED status. Supplied relations are checked for branch consistency. The API supports create, read, update, delete. Completion timestamps are fields but the service does not automatically set completedAt when status changes.'), p('Documents','H2X'), p('POST /api/documents/upload accepts one multipart file in field file and metadata type plus at least one customerId, policyId, claimId. Multer accepts PDF/JPEG/PNG up to MAX_UPLOAD_SIZE_BYTES (default 5 MiB), writes a UUID-named file to UPLOAD_DIR (default public/uploads), then checks the file signature. The service validates linked records and same-branch linkage, saves document metadata and /uploads/<generated-name> in the database, and removes the disk file if service validation or DB creation fails. GET /:id/content is authenticated and branch-scoped; delete removes the local file and metadata row.'), p('Activities, commissions, dashboard, reports','H2X'), p('Activities are read-only through the API; this code automatically writes activities during lead conversion and policy creation. Commissions are branch-scoped records created/updated by branch users, optionally linked to policy/customer, with PENDING/PAID/CANCELLED states. Dashboard aggregates counts, pending follow-ups, commission amount, and renewals due today/this week/this month. Reports return summary counts and grouped renewal/commission totals.'), PageBreak()]

story += [p('6. API capability catalogue','H1X'), p('All routes below are mounted under /api. Except login and /health, routes require a valid Bearer JWT and the named feature permission.'), grid(['Feature','Operations','Who can call (read / write)'],[
 ['Auth','POST /auth/admin/login; POST /auth/branch/login','Public sign-in endpoints'],
 ['Branches','GET /branches; GET /:id; POST /; PATCH /:id','Admin / Admin'],
 ['Staff','GET /staff; GET /:id; POST /; PATCH /:id; DELETE /:id','Admin or Branch / Branch'],
 ['Customers','GET /customers; GET /:id; POST /; PATCH /:id; DELETE /:id','Admin or Branch / Branch'],
 ['Leads','GET /leads; GET /:id; POST /; PATCH /:id; DELETE /:id; POST /:id/convert','Admin or Branch / Branch'],
 ['Policies','GET /policies; GET /:id; POST /; PATCH /:id','Admin or Branch / Branch'],
 ['Renewals','GET /renewals; GET /:id; PATCH /:id','Admin or Branch / Branch for update'],
 ['Claims','GET /claims; GET /:id; POST /; PATCH /:id','Admin or Branch / Branch'],
 ['Follow-ups','GET /follow-ups; GET /:id; POST /; PATCH /:id; DELETE /:id','Admin or Branch / Branch'],
 ['Documents','GET /documents; GET /:id; GET /:id/content; POST /upload; DELETE /:id','Admin or Branch / Branch for upload/delete'],
 ['Activities','GET /activities; GET /:id','Admin or Branch / read-only'],
 ['Commissions','GET /commissions; GET /:id; POST /; PATCH /:id','Admin or Branch / Branch'],
 ['Dashboard','GET /dashboard','Admin or Branch'],
 ['Reports','GET /reports/summary; /renewals; /commissions','Admin or Branch'],
 ['System','GET /health; GET /api-docs','Public health/docs UI'],
], [1.0*inch,3.35*inch,2.3*inch]), Spacer(1,8), p('Permissions come from src/constants/permissions.js. Admin has cross-branch read access across the listed operational resources. Branch write permissions vary by resource; branch users cannot write branches. The route list above reflects actual registered Express endpoints rather than only the high-level API-SCOPE.md summary.'), PageBreak()]

story += [p('7. Data model and important rules','H1X'), p('Primary record relationships','H2X'), grid(['Record','Important links / constraints'],[
 ['Branch','Parent tenant for staff, customers, leads, policies, renewals, claims, follow-ups, documents, activities, commissions.'],
 ['Staff','Belongs to a branch; optional assignment on customers, leads, follow-ups, activities. Not an auth principal.'],
 ['Customer','Belongs to a branch; optional staff assignment; owns policies, claims, follow-ups, documents, activities, commissions.'],
 ['Lead','Belongs to a branch; optional staff assignment; can convert once to a customer.'],
 ['Policy','Belongs to branch and customer; unique policyNumber per branch; has renewals, claims, documents, commissions.'],
 ['Renewal','Belongs to branch and policy; due date and renewal state.'],
 ['Claim','Belongs to branch and customer; optional policy must match customer and branch when written via service.'],
 ['Document','Belongs to branch; optionally linked to customer, policy, claim; local disk path represented by fileUrl.'],
 ['Commission','Belongs to branch; optional policy/customer association and payment state.'],
], [1.15*inch,5.5*inch]), p('Branch scope rules','H2X'), bullet('A BRANCH token carries branchId. Feature services use that branchId to scope find/list/count and related-record validation.'), bullet('An ADMIN scope is generally empty for reads, making queries cross-branch. Admin-created operational records need a branchId where the service requires it.'), bullet('For branch writes, the service derives branchId from the JWT; request body branchId is deleted or overwritten so it cannot move a record across branches.'), bullet('The helper src/context/request.context.js and middleware branch.middleware.js exist, but the feature routes shown do not mount requireBranch; actual branch scoping is implemented primarily in each feature service.'), p('8. Configuration and deployment assumptions','H1X'), grid(['Setting / component','Observed behavior'],[
 ['PORT','Defaults to 3000; if occupied, server tries successive ports until available or invalid.'],
 ['DATABASE_URL','PostgreSQL connection used by PrismaPg, connection pool max 10.'],
 ['JWT_SECRET','Required operationally for signing/verifying access tokens.'],
 ['JWT_EXPIRES_IN','Defaults to 365d. Token payload includes id, userType, branchId.'],
 ['UPLOAD_DIR','Defaults to public/uploads; local filesystem storage.'],
 ['MAX_UPLOAD_SIZE_BYTES','Defaults to 5 MiB; one file per request.'],
 ['CORS','Development allows any origin; other modes currently allow https://yourdomain.com.'],
 ['Seed','prisma/seed.js creates or ensures initial admin from ADMIN_EMAIL and ADMIN_PASSWORD; uses bcrypt cost 12.'],
 ['Docs','Swagger UI serves openapiSpec at /api-docs; JSON endpoint is commented out.'],
], [1.55*inch,5.1*inch]), PageBreak()]

story += [p('9. Implementation observations and caveats','H1X'), p('These points clarify the current behavior and are useful when returning to the project after a gap.'), bullet('<b>No background scheduler is present.</b> Renewals are initially created at policy creation; dashboard/report calculations read persisted statuses. No timer/cron job advances statuses or sends reminders.'), bullet('<b>Local uploads require persistent local storage.</b> Document metadata points to a file under the server upload directory. The repository does not show cloud object storage or a static public uploads route; content is served by authenticated download.'), bullet('<b>Admin branch ownership is not consistently filtered.</b> Operational admin reads use broad scope. Branch list/get behavior constrains branch users to their own branch, while admin branch queries are not filtered to adminId in branchService.'), bullet('<b>Policy updates do not synchronize renewals.</b> The create transaction initializes a renewal due date, but policyService.update only updates the policy row.'), bullet('<b>Validation and DB constraints both matter.</b> Zod rejects malformed/unknown request fields; Prisma/database constraints catch referential integrity and unique collisions. Error middleware maps P2002 to a generic 409.'), bullet('<b>Configured CORS origin is a placeholder outside development.</b> Replace https://yourdomain.com for a real production frontend origin.'), bullet('<b>Staff service logs auth claims.</b> staff.service.js includes console.log(auth) in getScope; JWT identity metadata may therefore appear in application logs.'), p('10. Source map for future navigation','H1X'), grid(['Concern','Start here'],[
 ['Process lifecycle and HTTP middleware','server.js; src/app.js'],
 ['Route registry','src/routes/index.js'],
 ['Roles and endpoint permissions','src/constants/permissions.js; src/constants/roles.js'],
 ['Request authentication/validation/errors','src/middlewares/auth.middleware.js; authorization.middleware.js; zod.middleware.js; error.middleware.js'],
 ['Feature rules','src/features/<feature>/<feature>.route.js, controller.js, service.js, model.js, schema.js, serializer.js'],
 ['Database relations and enums','prisma/schema.prisma; prisma/migrations/20261007000000_init/migration.sql'],
 ['DB client','src/config/prisma.js'],
 ['API documentation','src/openapi.js; /api-docs'],
 ['Seed and syntax check','prisma/seed.js; scripts/check.js'],
], [2.1*inch,4.55*inch]), Spacer(1,8), p('Analysis basis','H2X'), p('The behavior described here was read from the checked-in code and repository documentation, not inferred from a running deployment. This document is an as-built functional specification; it does not claim that a database is currently reachable or that the API has been exercised against live data.', 'CalloutX')]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
