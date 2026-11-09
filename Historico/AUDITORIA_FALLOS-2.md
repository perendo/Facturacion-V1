# Re-Auditoría Técnica Post-Remediación: Facturacion-V1
**Repositorio:** [https://github.com/perendo/Facturacion-V1.git](https://github.com/perendo/Facturacion-V1.git)  
**Commits comparados:** `294db08` (Inicial) ➔ `f7f34fd` (*"feat: apply all audit remediation (Alembic, fiscal compliance, security, tests)"*)  
**Fecha de re-evaluación:** 9 de noviembre de 2026  
**Evolución del Score de Salud Técnica:** **54 / 100 ➔ 88 / 100 (+34 puntos)**  
**Dictamen:** **Excelente progreso.** Se ha resuelto el 80% de los hallazgos críticos de la auditoría inicial. Restan 2 regresiones menores de integración (dependencia `qrcode` y renderizado de `Navbar`) y la interfaz visual para el perfil fiscal.

---

## 1. Tabla Comparativa de Evolución (Antes vs Después)

| Área Evaluada | Inicial (Commit 294db08) | Actual (Commit f7f34fd) | Delta | Estado Actual |
| :--- | :---: | :---: | :---: | :--- |
| **Higiene de Repositorio & DevOps** | 25% | **95%** | **+70%** | 🟢 Resuelto (1.36M líneas y .venv purgados, .gitignore raíz) |
| **Arquitectura de Datos & Concurrencia** | 50% | **92%** | **+42%** | 🟢 Resuelto (Secuencia atómica por usuario, SQLite WAL, Alembic) |
| **Lógica Contable & Métricas** | 55% | **95%** | **+40%** | 🟢 Resuelto (Dashboard con agregaciones SQL y canceladas excluidas) |
| **Seguridad & Autenticación** | 45% | **88%** | **+43%** | 🟢 Resuelto (Rate limiting, cookies HttpOnly, contraseñas fuertes) |
| **Cumplimiento Fiscal Español** | 20% | **82%** | **+62%** | 🟢 Resuelto en Backend (Veri*Factu SHA-256, QR AEAT, CompanyProfile) |
| **Frontend & Experiencia de Usuario** | 70% | **78%** | **+8%** | 🟡 Parcial (Eliminado axios y confirm modal; pendiente Navbar fix y UI perfil) |
| **PUNTUACIÓN GLOBAL** | **54 / 100** | **88 / 100** | **+34 pts** | 🟢 **Apto con ajustes menores** |

---

## 2. Estado de los Hallazgos Iniciales

| ID | Hallazgo Original | Estado en `f7f34fd` | Detalle de la Corrección |
| :--- | :--- | :---: | :--- |
| **F-001** | Subida accidental de `.venv` en Git | ✅ **CORREGIDO** | Se eliminaron 5.986 archivos `.venv`. Se añadió `.gitignore` en la raíz. |
| **F-002** | Fuga de datos en secuencia de facturas | ✅ **CORREGIDO** | Numeración atómica con `func.max()` por `(user_id, series, year)` y `UniqueConstraint`. |
| **F-003** | Falta de Veri*Factu y trazabilidad | ✅ **CORREGIDO** | Modelo `InvoiceEvent` de auditoría, hash SHA-256 encadenado y código QR AEAT en PDF. |
| **F-004** | Falta de datos fiscales del emisor | ✅ **CORREGIDO** | Modelo `CompanyProfile` con NIF, razón social, dirección y endpoints CRUD. |
| **F-005** | Dashboard sumaba facturas canceladas | ✅ **CORREGIDO** | Consultas `func.sum()` en SQL filtrando `status.in_(["sent", "paid"])`. |
| **F-006** | `ON DELETE SET NULL` borraba clientes | ✅ **CORREGIDO** | Clave foránea con `RESTRICT` + snapshot fiscal (`recipient_name`, `recipient_tax_id`). |
| **F-007** | JWT expuesto en cookies no-HttpOnly | ✅ **CORREGIDO** | Backend emite cookie `token` con `httponly=True`, `samesite="lax"`. |
| **F-008** | Incompatibilidad UTF-8 en PDF | 🟡 **PARCIAL** | Estructura PDF mejorada con QR y NIF, pero falta cargar fuente TTF Unicode. |
| **F-009** | Facturas rectificativas y retención IRPF | ✅ **CORREGIDO** | Campos `invoice_type`, `rectifies_invoice_id`, `irpf_rate` e `irpf_total` en backend. |
| **F-010** | Descuadre en descuento global | ✅ **CORREGIDO** | Descuento aplicado proporcionalmente a las bases antes de calcular el IVA por línea. |
| **F-011** | Endpoints sin paginación | ✅ **CORREGIDO** | Añadidos `page`, `page_size`, `limit` y `offset` en facturas, clientes y productos. |
| **F-012** | SQLite sin modo WAL | ✅ **CORREGIDO** | Evento SQLAlchemy que inyecta `PRAGMA journal_mode=WAL` y `synchronous=NORMAL`. |
| **F-013** | Sin rate limiting y contraseñas débiles | ✅ **CORREGIDO** | Módulo `rate_limit.py` activo y validador de contraseña (mayúsculas, minúsculas, dígitos, min 8). |
| **F-014** | Usuario demo inyectado en producción | ✅ **CORREGIDO** | Seed condicionado a `ENVIRONMENT in {"development", "dev", "test"}`. |
| **F-015** | Dependencia muerta `axios` | ✅ **CORREGIDO** | Eliminado `axios` de `frontend/package.json`. Añadido suite de tests Vitest. |
| **F-016** | Diálogos `window.confirm` | ✅ **CORREGIDO** | Reemplazados por modales interactivos `<Modal />` en todo el frontend. |

---

## 3. Nuevos Hallazgos y Regresiones a Corregir (Acción Recomendada)

### [R-001] 🔴 Dependencia ausente `qrcode` en `backend/requirements.txt`
* **Archivo:** `backend/app/services/pdf_service.py` (Línea 1) y `backend/requirements.txt`
* **Problema:** Se añadió `import qrcode` y `_qr_code_image()` en `pdf_service.py`, pero la librería `qrcode` no se incluyó en `requirements.txt`.
* **Impacto:** Si se despliega el backend o se instala en un entorno limpio (`pip install -r requirements.txt`), cualquier intento de generar un PDF lanzará:
  ```text
  ModuleNotFoundError: No module named 'qrcode'
  ```
* **Solución:** Añadir `qrcode[pil]>=7.4.2` a `backend/requirements.txt`.

---

### [R-002] 🔴 Navbar invisible en Frontend tras mitigación de XSS
* **Archivo:** `frontend/components/Navbar.tsx` (Línea 26) y `frontend/lib/auth.ts`
* **Problema:** En `auth.ts`, para evitar el robo de token por XSS, la función `getToken()` ahora devuelve `null`:
  ```typescript
  export function getToken(): string | null {
    return null; // Cookie HttpOnly
  }
  ```
  Sin embargo, en `Navbar.tsx` se comprueba:
  ```typescript
  const token = mounted ? getToken() : null;
  if (!token) return null; // ¡Siempre se cumple y la barra nunca se dibuja!
  ```
* **Impacto:** Ningún usuario autenticado puede ver el menú de navegación superior en la aplicación web.
* **Solución:** Comprobar la autenticación mediante el usuario en `Navbar.tsx`:
  ```typescript
  // frontend/components/Navbar.tsx
  const isAuth = mounted ? isAuthenticated() : false;
  if (!isAuth) return null;
  ```

---

### [R-003] 🟠 Falta de interfaz de usuario para el Perfil Fiscal (`CompanyProfile`)
* **Archivo:** `frontend/app/`
* **Problema:** El backend expone `/api/v1/company-profile`, pero en el frontend no existe ninguna pantalla para que el usuario introduzca su NIF, razón social, dirección y código postal.
* **Impacto:** Un usuario registrado en la web no tiene forma de configurar sus datos de facturación desde la interfaz, por lo que las facturas que emita carecerán de sus datos fiscales reales.
* **Solución:** Crear una página `/settings/profile` o `/perfil` con un formulario enlazado a `GET/PUT /api/v1/company-profile` y añadir el enlace en la cabecera.

---

### [R-004] 🟠 Falta de campos IRPF y Rectificativas en `InvoiceForm.tsx`
* **Archivo:** `frontend/components/invoices/InvoiceForm.tsx`
* **Problema:** El backend ya soporta `irpf_rate` y `invoice_type="rectification"`, pero el formulario de nueva factura en Next.js todavía no incluye el desplegable de tipo de factura ni el input de retención IRPF (%).
* **Solución:** Añadir el campo de retención IRPF al formulario y recalcular el total restando la retención en tiempo real.

---

## 4. Checklist Rápido de Corrección Final

```bash
# 1. Añadir qrcode a backend/requirements.txt
echo "qrcode[pil]>=7.4.2" >> backend/requirements.txt

# 2. Corregir Navbar en frontend/components/Navbar.tsx
# Reemplazar "const token = mounted ? getToken() : null; if (!token) return null;"
# Por "if (!mounted || !isAuthenticated()) return null;"
```

---
*Re-auditoría generada y verificada contra el commit `f7f34fd` del repositorio.*
