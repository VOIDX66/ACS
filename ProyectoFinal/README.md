# ACS Payment Engine

Sistema concurrente distribuido para procesamiento de tareas en segundo plano con FastAPI, PostgreSQL y concurrencia con hilos.

## Requisitos

- Docker y Docker Compose
- Python 3.12+ (para ejecutar los milestones sin Docker)

## Levantar el sistema

```bash
docker-compose up --build
```

Esto levanta PostgreSQL 16 en `localhost:5432` y la API en `http://localhost:8000`.

Documentación interactiva disponible en:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### Health Check

```
GET /health
```

**Respuesta (200)**
```json
{"status": "ok"}
```

---

### Auth — Registro de Usuario

Crea una cuenta nueva.

```
POST /auth/register
```

**Body**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "clave1234",
  "full_name": "Juan Pérez"
}
```

**Respuesta (201)**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "full_name": "Juan Pérez"
}
```

**Nota:** La contraseña debe tener al menos 8 caracteres y el email debe ser válido.

---

### Auth — Login

Obtiene un token JWT para usar en los endpoints protegidos.

```
POST /auth/login
```

**Body**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "clave1234"
}
```

**Respuesta (200)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Usa el token en los siguientes endpoints con el header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### Jobs — Crear Tarea

Crea un job de procesamiento de texto.

```
POST /jobs/
Authorization: Bearer <token>
```

**Body**
```json
{
  "input_text": "Hola mundo desde ACS"
}
```

**Respuesta (201)**
```json
{
  "id": 1,
  "status": "pending",
  "input_text": "Hola mundo desde ACS"
}
```

---

### Jobs — Listar Tareas del Usuario

```
GET /jobs/
Authorization: Bearer <token>
```

**Respuesta (200)**
```json
[
  {
    "id": 1,
    "status": "pending",
    "input_text": "Hola mundo desde ACS"
  }
]
```

---

### Jobs — Obtener Tarea por ID

```
GET /jobs/{job_id}
Authorization: Bearer <token>
```

**Respuesta (200)**
```json
{
  "id": 1,
  "status": "completed",
  "input_text": "Hola mundo desde ACS"
}
```

---

### Jobs — Procesar Tarea

Ejecuta el procesamiento de texto: convierte a mayúsculas, cuenta palabras y caracteres.

```
POST /jobs/{job_id}/process
Authorization: Bearer <token>
```

**Respuesta (200)**
```json
{
  "job_id": 1,
  "word_count": 4,
  "char_count": 22,
  "processed_text": "HOLA MUNDO DESDE ACS"
}
```

---

### Payments — Procesar Lote de Pagos

Envía un lote de pagos para ser procesado por el pool de workers. Simula validación antifraude, cálculo de comisión (5%) y conversión a USD.

```
POST /payments/batch
Authorization: Bearer <token>
```

**Body**
```json
[
  {
    "merchant_id": 101,
    "amount": 150.00,
    "currency": "EUR",
    "method_type": "tarjeta"
  },
  {
    "merchant_id": 102,
    "amount": 200.00,
    "currency": "USD",
    "method_type": "transferencia"
  },
  {
    "merchant_id": 103,
    "amount": 50000,
    "currency": "JPY",
    "method_type": "billetera"
  }
]
```

**Campos de cada pago:**

| Campo | Tipo | Descripción |
|---|---|---|
| `merchant_id` | int | ID del comercio (101-107 recomendado) |
| `amount` | float | Monto en la moneda original |
| `currency` | str | `USD`, `EUR`, `GBP`, `JPY` |
| `method_type` | str | `tarjeta`, `transferencia`, `billetera` |

**Respuesta (200)**
```json
[
  {
    "request_id": "a1b2c3d4",
    "merchant_id": 101,
    "amount": 150.00,
    "currency": "EUR",
    "status": "completed",
    "commission": 7.50,
    "final_amount": 153.90
  },
  {
    "request_id": "e5f6g7h8",
    "merchant_id": 102,
    "amount": 200.00,
    "currency": "USD",
    "status": "completed",
    "commission": 10.00,
    "final_amount": 190.00
  },
  {
    "request_id": "i9j0k1l2",
    "merchant_id": 103,
    "amount": 50000.00,
    "currency": "JPY",
    "status": "completed",
    "commission": 2500.00,
    "final_amount": 318.25
  }
]
```

---

### WebSocket — Notificaciones en Tiempo Real

Conéctate para recibir notificaciones de jobs completados.

```
ws://localhost:8000/ws/{user_id}
```

Ejemplo con `websocat`:

```bash
websocat ws://localhost:8000/ws/1
```

O desde JavaScript:

```js
const ws = new WebSocket("ws://localhost:8000/ws/1");
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log("Notificación:", notification);
};
```

---

## Milestones — Ejecutar sin Docker

Los scripts de milestones ejecutan simulaciones de concurrencia con salida visual enriquecida con Rich. No requieren PostgreSQL.

```bash
# Instalar dependencias
pip install -r requirements.txt

# Pagos internacionales (15 pagos, 3 workers)
python scripts/milestone1_payments.py

# Reader-Writer Lock con prioridad de escritor
python scripts/milestone2_rwlock.py

# Liquidación de fin de día con Barrier
python scripts/milestone3_barrier.py
```

---

## Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_URL` | `postgresql://acs_user:acs_pass@localhost:5432/acs_payments` | Conexión PostgreSQL |
| `SECRET_KEY` | `dev-secret-key` | Clave para firmar JWT |
| `API_HOST` | `0.0.0.0` | Host de la API |
| `API_PORT` | `8000` | Puerto de la API |

---

## Arquitectura

```
src/
├── domain/           # Entidades, Value Objects, Interfaces
├── application/      # Casos de uso (AuthService, PaymentService, UoW)
├── infrastructure/   # SQLAlchemy, Workers, Locks, JWT, WebSocket
└── presentation/     # FastAPI routes, Pydantic schemas, WebSocket
```

**Patrones de diseño aplicados:** Repository, Unit of Work, Singleton, Factory, Thread-Safe Object, Reader-Writer Lock.
