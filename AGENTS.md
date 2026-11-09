# AGENTS.md

Full-stack billing app: FastAPI backend in `backend/`, Next.js 16 App Router frontend in `frontend/`. Two independent projects (no root workspace/lockfile).

**Estado del proyecto:** Certificado por `AUDITORIA_CERTIFICADA_FINAL.md` — calificación 98/100, apto para producción y explotación comercial.

## Comandos

Backend (activar venv raíz primero; ejecutar desde `backend/` para que `.env` y SQLite resuelvan correctamente):

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload        # http://localhost:8000, docs /docs
python -m pytest                    # todos los tests backend
python -m pytest tests/test_invoices.py::test_integration_invoice_full_flow
.\.venv\Scripts\alembic.exe upgrade head          # aplicar migraciones pendientes
.\.venv\Scripts\alembic.exe revision --autogenerate -m "descripcion"  # nueva migración
.\.venv\Scripts\alembic.exe current                # mostrar migración actual
```

Frontend:

```powershell
cd frontend
npm install
npm run dev                         # http://localhost:3000
npm run build                       # build producción + type check
npm run lint
npm run test                        # vitest run
npx tsc --noEmit                    # typecheck solo
```

## Entorno

- Backend carga `backend/.env` (copiar desde `backend/.env.example`); nunca commitear `.env`.
- Frontend usa `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`), típicamente en `frontend/.env.local`.
- CORS permite solo `http://localhost:3000` / `http://127.0.0.1:3000`; backend puerto 8000, frontend 3000.
- Login demo solo en desarrollo: `demo@facturacion.com` / `demo1234`.
- Python deps en el venv raíz (Python 3.12); `backend/.venv` no se usa. Si falta: `python -m venv .venv` luego instalar `backend/requirements.txt`.
- Para despliegue final en nube: conectar a PostgreSQL/Cloud SQL vía `DATABASE_URL`, generar `SECRET_KEY` segura (`openssl rand -hex 32`) y activar HTTPS para cookies `Secure`.

## Estructura y límites

- `backend/app/main.py`: app FastAPI, CORS, registro de routers, startup semea usuario demo (solo dev). Esquema gestionado por Alembic (sin `create_all`).
- Routers bajo `/api/v1`: `/auth`, `/clients`, `/products`, `/invoices`, `/dashboard`, `/company-profile`.
- Frontend: páginas App Router; `lib/api.ts` (cliente fetch con credenciales, Bearer + redirect 401), `lib/auth.ts` (cookie HttpOnly vía backend, usuario en localStorage), `middleware.ts` (protección de rutas vía cookie `token`).
- `backend/billing.db` es SQLite local y gitignorado; `backend/.venv`, `frontend/node_modules`, `frontend/.next` están gitignored.
- Prompts de agente OpenCode: `.opencode/agents/*.md`, flujo maestro `facturacion.md`, especificación técnica `PLAN.md`.

## Quirks de datos y esquema

- **Alembic gestiona el esquema.** `backend/alembic.ini` apunta a `sqlite:///./billing.db`. Ejecutar `alembic upgrade head` para aplicar migraciones. No confiar en `create_all` para producción.
- Tests usan una BD SQLite en memoria (`conftest.py`, `StaticPool`) reseteada por test; no tocan `billing.db`.
- `auth_headers` registra/loguea `test@example.com`.
- Números de factura `INV-{year}-{seq:04d}` por usuario/serie/año (única `(user_id, series, year, sequence_number)`).
- Edición/eliminación de facturas solo si están en `draft`; transiciones: draft→sent/cancelled, sent→paid/cancelled; paid/cancelled son terminales.
- Valores monetarios son decimales serializados como números.
- `InvoiceEvent` registra eventos created/updated/status_changed por factura (inmutabilidad fiscal).
- `CompanyProfile` almacena datos fiscales del emisor (NIF/CIF, dirección) requeridos por RD 1619/2012.
- PDF incluye hash Veri*Factu y código QR para cotejo tributario AEAT.

## Quirks de seguridad

- JWT en cookie HttpOnly (`token`) emitida por backend; `lib/auth.ts` del frontend no lee/escribe token en JS.
- Rate limiting en `/auth/register`, `/auth/login` y endpoints mutables de `/clients`, `/products`, `/invoices` (5 req/min por IP).
- Política de contraseñas: mínimo 8 caracteres, mayúscula, minúscula, dígito.
- Seed de usuario demo solo en entornos `development`/`dev`/`test`.
- Endpoint `/auth/logout` para limpiar la cookie.

## Quirks de frontend

- Next.js es 16.4.5, no 14 como afirma `PLAN.md`. Leer `node_modules/next/dist/docs/` antes de escribir código de framework.
- `frontend/AGENTS.md` es auto-generado por `next dev`; no eliminar su bloque `nextjs-agent-rules`.
- `middleware.ts` está deprecado en Next 16 (build avisa) pero funciona; no migrar a menos que se pida.
- Token de autenticación es cookie HttpOnly; middleware lee cookie `token` para protección de rutas.
- Convención UI de `.opencode/agents/nextjs_dev.md`: Material Design 3 + paleta antifatiga (no `#FFFFFF`/`#000000` puros en superficies/texto).
- `axios` eliminado; `fetch` en todo el frontend.
- Nueva página `/settings/profile` para editar `CompanyProfile` (NIF/CIF, razón social, dirección fiscal).
- `InvoiceForm` incluye tipo de factura (ordinaria/rectificativa) y retención IRPF con recálculo en tiempo real.

## Testing y verificación

- Backend: pytest + FastAPI TestClient; suites en `backend/tests/` (auth, clients, products, invoices, integration). Todas pasan (16 tests).
- Frontend: Vitest + Testing Library (`npm run test`). Usar `npm run build` (type + compile) y `npm run lint` para verificación.
- Tests de integración incluyen preflight CORS, flujo completo de facturas, guardas de estado, filtros, dashboard y PDF (`%PDF`).

## Certificación y auditoría

- `AUDITORIA_CERTIFICADA_FINAL.md`: certificación técnica final, calificación 98/100 — apto para producción.
- `Historico/AUDITORIA_FALLOS.md`: auditoría inicial (54/100), 18 fallos resueltos.
- `Historico/AUDITORIA_FALLOS-2.md`: re-auditoría (88/100), 4 regresiones R-001 a R-004 resueltas en commit `90b4692`.
- Todos los hallazgos F-001 a F-018 y R-001 a R-004 están marcados como RESUELTOS.

## Notas sobre deriva de documentación

- `PLAN.md` actualizado para reflejar Next.js 16, `next.config.ts`, Alembic, eliminación de `axios`, adición de Vitest.
- Login/register aceptan cuerpos JSON (no form-encoded), a pesar de lo que diga `PLAN.md`.
- Requisito Python backend 3.11+; local usa 3.12.
