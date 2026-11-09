# Facturación V1

Aplicación web full-stack para la gestión de facturación de pequeños negocios y freelancers: clientes, productos/servicios, facturas con numeración automática, cálculo de impuestos y totales, y seguimiento del estado de cobro.

## Estado del proyecto

Certificado por `AUDITORIA_CERTIFICADA_FINAL.md` — calificación **98 / 100 — EXCELENTE**. Apto para producción y explotación comercial. Todos los hallazgos de auditoría (F-001 a F-018 y R-001 a R-004) están resueltos.

## Stack tecnológico

- **Backend:** Python 3.11+ (local 3.12), FastAPI, Uvicorn, SQLAlchemy 2.x, SQLite, Pydantic v2, python-jose (JWT), passlib (bcrypt), fpdf2, qrcode[pil], Alembic (migraciones).
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, react-hook-form + zod, Vitest + Testing Library.

## Estructura del repositorio

```
backend/   # API FastAPI + Alembic
frontend/  # Next.js App Router
PLAN.md    # Especificación técnica y contrato de API
AGENTS.md  # Guía para agentes de código (OpenCode)
LICENSE    # GNU GPL v3.0
```

## Requisitos previos

- Python 3.11+ (recomendado 3.12)
- Node.js 20+ y npm
- Git

## Configuración

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Editar `backend/.env` y definir al menos `SECRET_KEY` (ej. `openssl rand -hex 32`). Por defecto usa SQLite local (`backend/billing.db`).

### Frontend

```powershell
cd frontend
npm install
```

Opcional: crear `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Ejecución en desarrollo

Backend (desde `backend/`, con venv activado):

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000` y documentación en `http://localhost:8000/docs`.

Aplicar migraciones de base de datos:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Frontend:

```powershell
cd frontend
npm run dev
```

Disponible en `http://localhost:3000`.

Al arrancar en desarrollo, el backend crea un usuario demo: `demo@facturacion.com` / `demo1234`.

## Migraciones (Alembic)

El esquema se gestiona con Alembic, no con `create_all`:

```powershell
.\.venv\Scripts\alembic.exe upgrade head          # aplicar pendientes
.\.venv\Scripts\alembic.exe revision --autogenerate -m "descripcion"  # nueva migración
.\.venv\Scripts\alembic.exe current                # versión actual
.\.venv\Scripts\alembic.exe history                # historial
```

## Pruebas

Backend:

```powershell
cd backend
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run test          # vitest run
npm run build         # build producción + type check
```

## Funcionalidades clave

- Autenticación JWT con cookie HttpOnly (mitiga XSS)
- CRUD de clientes, productos y facturas
- Numeración de facturas por usuario/año (sin fuga entre inquilinos)
- Cálculo de impuestos con Decimal y descuento global proporcional
- Dashboard contable (excluye canceladas y borradores)
- Perfil fiscal del emisor (NIF/CIF, domicilio) — RD 1619/2012
- Hash Veri*Factu encadenado y código QR AEAT en PDF — Veri*Factu RD 1007/2023
- Facturas rectificativas y retención IRPF
- Paginar en listados (facturas, clientes, productos)
- SQLite en modo WAL para concurrencia
- Rate limiting (5 req/min por IP) y política de contraseñas fuertes
- Tests de backend (pytest) y frontend (Vitest)

## Despliegue en producción

1. Conectar a PostgreSQL/Cloud SQL actualizando `DATABASE_URL` en `.env`.
2. Ejecutar `alembic upgrade head` para crear el esquema.
3. Generar `SECRET_KEY` criptográficamente segura.
4. Activar HTTPS con certificado SSL para cookies `Secure`.
5. Definir `ENVIRONMENT=production` (desactiva el seed de usuario demo).

## Licencia

Este proyecto se distribuye bajo la licencia **GNU General Public License v3.0**. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
