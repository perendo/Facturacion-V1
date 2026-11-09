# Plan de Implementación — Aplicación de Facturación (Billing/Invoicing)

## 1. Visión general y alcance

Aplicación web full-stack para gestión de facturación de pequeños negocios/freelancers. Permite administrar clientes, productos/servicios, emitir facturas con numeración automática, calcular impuestos y totales, y hacer seguimiento del estado de cobro.

**Alcance (MVP):**
- Autenticación de usuarios con JWT (access token) — registro y login.
- CRUD de clientes y productos/servicios.
- Emisión de facturas con líneas de detalle, descuentos por línea y global, IVA por línea.
- Estados de factura: borrador → enviada → pagada / cancelada.
- Búsqueda y filtros (cliente, estado, rango de fechas, número).
- Dashboard con KPIs: facturado, cobrado, pendiente, conteo por estado.

**Fuera de alcance (futuro):** envío por email, PDF, multi-tenant, roles, paginación avanzada, refresh tokens.

## 2. Stack tecnológico

### Backend (`backend/`)
- Python 3.11+ (local: 3.12)
- FastAPI (ASGI) + Uvicorn
- SQLAlchemy 2.x (ORM) + SQLite (archivo `billing.db`)
- Pydantic v2 (schemas/validación)
- python-jose (JWT) + passlib[bcrypt] (hashing)
- python-multipart (formularios, opcional)
- pytest + httpx (tests)
- Alembic (migraciones de base de datos)
- fpdf2 (generación de PDF)
- qrcode[pil] (códigos QR para Veri*Factu)

### Frontend (`frontend/`)
- Next.js 16 (App Router) + TypeScript
- Tailwind CSS 4
- fetch para consumo de API (axios eliminado)
- react-hook-form + zod (formularios/validación)
- Recharts (opcional, gráficos del dashboard)
- Vitest + Testing Library (tests)

## 3. Estructura de carpetas

```
EquipoDeAgentes/
├── PLAN.md
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, routers
│   │   ├── config.py               # settings (SECRET_KEY, DB url, CORS origins)
│   │   ├── database.py             # engine, SessionLocal, Base, get_db
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── client.py
│   │   │   ├── product.py
│   │   │   ├── invoice.py
│   │   │   └── invoice_line.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── client.py
│   │   │   ├── product.py
│   │   │   ├── invoice.py
│   │   │   └── dashboard.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── clients.py
│   │   │   ├── products.py
│   │   │   ├── invoices.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   ├── auth_service.py     # hashing, JWT
│   │   │   ├── invoice_service.py  # numeración, cálculos, Veri*Factu
│   │   │   ├── dashboard_service.py
│   │   │   └── pdf_service.py
│   │   ├── dependencies.py         # get_current_user
│   │   ├── rate_limit.py           # rate limiting por IP
│   │   ├── utils.py
│   │   ├── alembic.ini             # configuración de migraciones
│   │   ├── alembic/                # scripts de migración Alembic
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   ├── tests/
│   │   │   ├── test_auth.py
│   │   │   ├── test_clients.py
│   │   │   ├── test_products.py
│   │   │   ├── test_invoices.py
│   │   │   ├── test_integration.py
│   │   │   └── conftest.py
│   │   ├── requirements.txt
│   │   └── billing.db                  # generado (gitignored)
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                # redirect /dashboard
    │   ├── (auth)/
    │   │   ├── login/page.tsx
    │   │   └── register/page.tsx
    │   ├── dashboard/page.tsx
    │   ├── clients/
    │   │   ├── page.tsx
    │   │   └── [id]/page.tsx
    │   ├── products/page.tsx
    │   └── invoices/
    │       ├── page.tsx
    │       ├── new/page.tsx
    │       └── [id]/page.tsx
    ├── components/
    │   ├── ui/                     # Button, Input, Modal, Table
    │   ├── clients/
    │   ├── products/
    │   ├── invoices/
    │   └── dashboard/
    ├── lib/
    │   ├── api.ts                  # cliente HTTP fetch con credenciales
    │   ├── auth.ts                 # token storage (HttpOnly cookie)
    │   └── types.ts
    ├── middleware.ts               # protección de rutas
    ├── tailwind.config.ts
    ├── next.config.ts
    ├── vitest.config.ts            # configuración de tests
    ├── vitest.setup.ts             # setup de tests
    ├── package.json
    └── package-lock.json
```

## 4. Modelo de datos

### `users`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | autoincrement |
| email | VARCHAR(255) UNIQUE NOT NULL | |
| hashed_password | VARCHAR(255) NOT NULL | bcrypt |
| full_name | VARCHAR(255) | |
| created_at | DATETIME | default now |

### `clients`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER FK users.id | propietario |
| name | VARCHAR(255) NOT NULL | |
| email | VARCHAR(255) | |
| phone | VARCHAR(50) | |
| address | TEXT | |
| tax_id | VARCHAR(50) | NIF/CIF |
| notes | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### `products`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER FK users.id | |
| name | VARCHAR(255) NOT NULL | |
| description | TEXT | |
| unit_price | NUMERIC(12,2) NOT NULL | |
| tax_rate | NUMERIC(5,2) NOT NULL | % IVA (ej. 21.00) |
| unit | VARCHAR(50) | ej. unidad, hora, kg |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### `invoices`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER FK users.id | |
| client_id | INTEGER FK clients.id | |
| number | VARCHAR(30) UNIQUE NOT NULL | INV-YYYY-NNNN |
| issue_date | DATE NOT NULL | |
| due_date | DATE | |
| status | VARCHAR(20) NOT NULL | draft/sent/paid/cancelled |
| global_discount | NUMERIC(5,2) | % descuento global (0-100) |
| subtotal | NUMERIC(12,2) | calculado |
| tax_total | NUMERIC(12,2) | calculado |
| total | NUMERIC(12,2) | calculado |
| notes | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### `invoice_lines`
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| invoice_id | INTEGER FK invoices.id (CASCADE) | |
| product_id | INTEGER FK products.id (nullable) | referencia opcional |
| description | VARCHAR(255) NOT NULL | snapshot del producto |
| quantity | NUMERIC(10,2) NOT NULL | |
| unit_price | NUMERIC(12,2) NOT NULL | |
| discount | NUMERIC(5,2) | % descuento línea |
| tax_rate | NUMERIC(5,2) NOT NULL | % IVA línea |
| line_subtotal | NUMERIC(12,2) | calculado |
| line_tax | NUMERIC(12,2) | calculado |
| line_total | NUMERIC(12,2) | calculado |

**Relaciones:** User 1-N Client/Product/Invoice; Client 1-N Invoice; Invoice 1-N InvoiceLine; Product 1-N InvoiceLine (opcional).

**Cálculo (invoice_service):**
- por línea: `base = qty * unit_price * (1 - discount/100)`; `line_subtotal = base`; `line_tax = base * tax_rate/100`; `line_total = base + line_tax`.
- global: `subtotal = sum(line_subtotal)`; aplicar `global_discount` → `subtotal_discounted = subtotal * (1 - global_discount/100)`; IVA proporcional o recalculado; `tax_total = sum(line_tax) * (1 - global_discount/100)` (o recalculo); `total = subtotal_discounted + tax_total`.
- Numeración: `INV-{year}-{seq:04d}` donde seq = count de facturas del usuario en el año + 1 (o tabla de contadores).

## 5. Contrato de API

Base URL: `http://localhost:8000/api/v1`. Auth: `Authorization: Bearer <token>`.

### Auth
- `POST /auth/register` — body `{email, password, full_name?}` → 201 `{id, email, full_name}`; 400 si email duplicado.
- `POST /auth/login` — form/json `{email, password}` → 200 `{access_token, token_type: "bearer"}`; 401 credenciales inválidas.
- `GET /auth/me` — 200 `{id, email, full_name}`.

### Clients
- `GET /clients?search=` → 200 list.
- `POST /clients` → 201 client.
- `GET /clients/{id}` → 200 / 404.
- `PUT /clients/{id}` → 200.
- `DELETE /clients/{id}` → 204.

### Products
- `GET /products?search=` → 200 list.
- `POST /products` → 201.
- `GET /products/{id}` → 200/404.
- `PUT /products/{id}` → 200.
- `DELETE /products/{id}` → 204.

### Invoices
- `GET /invoices?client_id=&status=&date_from=&date_to=&number=` → 200 list (resumen).
- `POST /invoices` → 201 (crea borrador, calcula totales).
- `GET /invoices/{id}` → 200 (con líneas).
- `PUT /invoices/{id}` → 200 (solo borrador editable; recalcular).
- `PATCH /invoices/{id}/status` body `{status}` → 200 (valida transiciones).
- `DELETE /invoices/{id}` → 204 (solo borrador).
- `GET /invoices/{id}/pdf` → 200 (descarga PDF de la factura).

### Dashboard
- `GET /dashboard/summary` → 200 `{total_invoiced, total_paid, total_pending, count_by_status: {draft, sent, paid, cancelled}}`.

Códigos: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation Error (FastAPI default), 500 Internal.

## 6. Flujos principales

**Registro/Login:** Frontend envía credenciales → backend hashea password (bcrypt) → guarda user → login verifica → emite JWT (sub=user_id, exp=24h) → frontend guarda en localStorage → adjunta en requests.

**Crear factura:** Usuario selecciona cliente, añade líneas (producto o manual), define descuento global y fechas → POST → backend genera número, calcula totales, status=draft → respuesta con totales.

**Cambiar estado:** PATCH /status con validación de transiciones: draft→sent/cancelled; sent→paid/cancelled; paid/cancelled son terminales (no cambios). Cancelled no reversible.

## 7. Plan de implementación por fases

### Fase 1 — Backend base
1. Crear estructura, `requirements.txt`, config, database.
2. Modelos SQLAlchemy + relaciones.
3. Schemas Pydantic.
4. Auth (register/login/me) + JWT dependency.
5. CRUD clients y products.

### Fase 2 — Facturas
6. invoice_service (numeración, cálculos).
7. Endpoints invoices (CRUD, filtros, status).
8. Dashboard summary.
9. Tests (pytest) para auth, clients, invoices.

### Fase 3 — Frontend
10. Setup Next.js + Tailwind, cliente API, auth context.
11. Páginas auth (login/register).
12. Middleware de protección.
13. CRUD clients y products.
14. Formulario de factura + listado + detalle.
15. Dashboard con KPIs.

### Fase 4 — Integración
16. Conectar frontend↔backend, manejo de errores global.
17. CORS configurado (origins localhost:3000).
18. Pruebas end-to-end manuales.
19. (Opcional) Docker/compose.

## 8. Consideraciones

**CORS:** Backend permite origins `http://localhost:3000` (y 127.0.0.1), métodos `*`, headers `*`, credentials true. Configurable vía env `CORS_ORIGINS`.

**Autenticación:** Bearer token en header `Authorization`. Token JWT firmado con HS256, expiración 24h. Frontend almacena en localStorage; interceptor adjunta; en 401 redirige a login. (Producción: considerar httpOnly cookie.)

**Manejo de errores:** FastAPI HTTPException con `detail`. Formato uniforme `{detail: string | object}`. Frontend muestra toast/alert. Validación Pydantic devuelve 422 con `detail` array. Logs en backend con logging estándar.

**Seguridad mínima:** passwords hasheados, validación de ownership (cada recurso filtrado por user_id), SQL parametrizado vía ORM, CORS restrictivo.

**SQLite:** archivo local; crear tablas al startup (`Base.metadata.create_all`). Para producción migrar a Postgres + Alembic.