# Facturacion V1

Aplicación web full-stack para la gestión de facturación de pequeños negocios y freelancers: clientes, productos/servicios, facturas con numeración automática, cálculo de impuestos y totales, y seguimiento del estado de cobro.

## Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.x, SQLite, Pydantic v2, python-jose (JWT), passlib (bcrypt), fpdf2.
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, react-hook-form + zod.

## Estructura

```
backend/   # API FastAPI
frontend/  # Next.js App Router
PLAN.md    # Especificación técnica y contrato de API
AGENTS.md  # Guía para agentes de código
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

Edita `backend/.env` y define al menos `SECRET_KEY`. Por defecto usa SQLite local (`backend/billing.db`).

### Frontend

```powershell
cd frontend
npm install
```

Opcional: crea `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Ejecución en desarrollo

Backend (desde `backend/`):

```powershell
cd backend
..\.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

O con el entorno activado:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000` y documentación en `http://localhost:8000/docs`.

Frontend:

```powershell
cd frontend
npm run dev
```

Disponible en `http://localhost:3000`.

Al arrancar, el backend crea las tablas y genera un usuario demo: `demo@facturacion.com` / `demo1234`.

## Pruebas

Backend:

```powershell
cd backend
python -m pytest
```

Frontend (sin runner de tests dedicado):

```powershell
cd frontend
npm run lint
npm run build
```

## Licencia

Este proyecto se distribuye bajo la licencia **GNU General Public License v3.0**. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
