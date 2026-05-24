# Diagrama de Clases — ACS Payment Engine

```mermaid
classDiagram
    direction TB

    %% ═══════════════════════════════════════════════════════════════
    %% DOMAIN LAYER
    %% ═══════════════════════════════════════════════════════════════
    namespace Domain_Entities {
        class PaymentRequest {
            +str request_id
            +int merchant_id
            +float amount
            +str currency
            +MethodType method_type
            +int priority
            +PaymentStatus status
            +float commission
            +float final_amount
            +display_amount() str
            +display_commission() str
            +display_final() str
        }
        class User {
            +int id
            +str email
            +str full_name
            +datetime created_at
        }
        class Job {
            +int id
            +int user_id
            +str input_text
            +JobStatus status
            +int priority
            +datetime created_at
            +datetime updated_at
            +datetime cancelled_at
        }
        class TextResult {
            +int id
            +int job_id
            +int word_count
            +int char_count
            +str processed_text
            +datetime created_at
        }
        class JobStatus {
            <<enumeration>>
            PENDING
            PROCESSING
            COMPLETED
            CANCELLED
            FAILED
        }
        class PaymentStatus {
            <<enumeration>>
            PENDING
            PROCESSING
            COMPLETED
            FAILED
        }
        class MethodType {
            <<enumeration>>
            CARD
            WIRE
            WALLET
        }
    }

    namespace Domain_ValueObjects {
        class Email {
            <<value object>>
            +str address
            +__post_init__() validation
        }
        class Password {
            <<value object>>
            +str hash
            +validate(raw) static
        }
    }

    namespace Domain_Events {
        class JobCompletedEvent {
            +int job_id
            +int user_id
            +str result_summary
            +str event_id
            +datetime occurred_at
        }
    }

    namespace Domain_Interfaces {
        class BalanceRepository {
            <<interface>>
            +get_balance(merchant_id) float
            +add_funds(merchant_id, amount)
        }
        class PaymentRepository {
            <<interface>>
            +save(request)
            +find_by_id(request_id) PaymentRequest
        }
        class UserRepository {
            <<interface>>
            +find_by_email(email) User
            +create(email, hashed_password, full_name) User
        }
        class JobRepository {
            <<interface>>
            +create(user_id, input_text, priority) Job
            +find_by_id(job_id) Job
            +find_by_user(user_id) List~Job~
            +update_status(job_id, status)
            +cancel_job(job_id) bool
        }
    }

    %% ═══════════════════════════════════════════════════════════════
    %% APPLICATION LAYER
    %% ═══════════════════════════════════════════════════════════════
    namespace Application_Services {
        class AuthService {
            -SQLUserRepository _repo
            +register(email, password, full_name) dict
            +login(email, password) str
        }
        class JobService {
            -SQLJobRepository _repo
            -Session _db
            +create_job(user_id, input_text, priority) dict
            +get_job(job_id) dict
            +list_user_jobs(user_id) list
            +cancel_job(job_id) bool
            +update_priority(job_id, priority) dict
        }
        class ProcessTextService {
            -Session _db
            -SQLJobRepository _repo
            +process(job_id) tuple
        }
        class ReportService {
            -Session _db
            +summary() dict
            +user_report(user_id) dict
        }
        class NotificationService {
            +notify_job_completed(event) static
        }
        class PaymentService {
            -WorkerPoolManager _pool
            +process_batch(requests) Table
            -_enqueue_request(producer_id, request)
            -_build_summary_table(requests) Table
        }
    }

    namespace Application_UoW {
        class UnitOfWork {
            -Session _session
            +__enter__() Session
            +__exit__(exc_type, exc_val, exc_tb)
            +begin() contextmanager
            +get_uow() UnitOfWork static
        }
    }

    %% ═══════════════════════════════════════════════════════════════
    %% INFRASTRUCTURE LAYER
    %% ═══════════════════════════════════════════════════════════════
    namespace Infrastructure_Persistence {
        class UserModel {
            <<ORM>>
            +int id
            +str email
            +str hashed_password
            +str full_name
            +datetime created_at
        }
        class JobModel {
            <<ORM>>
            +int id
            +int user_id
            +str status
            +int priority
            +str input_text
            +datetime created_at
            +datetime updated_at
            +datetime cancelled_at
        }
        class TextResultModel {
            <<ORM>>
            +int id
            +int job_id
            +int word_count
            +int char_count
            +str processed_text
            +datetime created_at
        }
        class PaymentModel {
            <<ORM>>
            +int id
            +str request_id
            +int merchant_id
            +float amount
            +str currency
            +str method_type
            +int priority
            +str status
            +float commission
            +float final_amount
            +datetime created_at
        }
        class SQLUserRepository
        class SQLJobRepository
        class SQLPaymentRepository
        class InMemoryBalanceRepository {
            -dict _balances
            -Lock _lock
            +get_balance(merchant_id) float
            +add_funds(merchant_id, amount)
        }
    }

    namespace Infrastructure_Sync {
        class PaymentQueue {
            <<singleton>>
            -Queue _q
            -bool _use_priority
            -counter _counter
            +enqueue(request) bool
            +dequeue(timeout) PaymentRequest
            +enable_priority()
            +task_done()
            +join()
        }
        class ReadWriteLock {
            -Condition _cond
            -int _readers
            -int _writers_waiting
            -bool _writing
            +acquire_read()
            +release_read()
            +acquire_write()
            +release_write()
        }
        class PaymentConfig {
            <<singleton>>
            -dict _rates
            -ReadWriteLock _rwlock
            +get_rate(currency) float
            +update_rates(new_rates)
        }
    }

    namespace Infrastructure_Workers {
        class PaymentWorker {
            <<thread>>
            +str _label
            +int processed
            +run()
        }
        class WorkerPoolManager {
            -PaymentQueue _queue
            -InMemoryBalanceRepository _repo
            -List~PaymentWorker~ _workers
            +start()
            +join()
        }
        class WorkerPoolFactory {
            +create_pool(num_workers, use_priority) static
        }
    }

    namespace Infrastructure_Auth {
        class JWTHandler {
            +hash_password(raw) str
            +verify_password(raw, hashed) bool
            +create_access_token(subject) str
            +decode_access_token(token) dict
        }
    }

    namespace Infrastructure_WS {
        class WebSocketManager {
            -dict _connections
            +connect(user_id, websocket) async
            +disconnect(user_id, websocket) async
            +notify(user_id, payload) async
        }
    }

    namespace Infrastructure_Metrics {
        class MetricsCollector {
            <<singleton>>
            -dict _counters
            -dict _timings
            +increment(metric)
            +record_timing(metric, elapsed)
            +snapshot() dict
            +display_live()
        }
    }

    %% ═══════════════════════════════════════════════════════════════
    %% PRESENTATION LAYER
    %% ═══════════════════════════════════════════════════════════════
    namespace Presentation_Routes {
        class AuthRoutes {
            +register(UserRegister) UserResponse
            +login(UserLogin) TokenResponse
        }
        class JobRoutes {
            +create_job(JobCreate) JobResponse
            +list_jobs() List~JobResponse~
            +get_job(job_id) JobResponse
            +cancel_job(job_id) JobResponse
            +update_priority(job_id, priority) JobResponse
            +process_job(job_id, background) JobResultResponse
        }
        class PaymentRoutes {
            +submit_batch(PaymentCreate[]) PaymentResponse[]
        }
        class ReportRoutes {
            +system_summary() ReportSummary
            +user_report(user_id) UserReportResponse
        }
        class WebSocketRoutes {
            +websocket_endpoint(ws, user_id) async
        }
        class Dependencies {
            +get_current_user(token) UserModel
            +get_db() Session
            +get_uow() UnitOfWork
        }
    }

    namespace Presentation_Schemas {
        class UserRegister
        class UserLogin
        class TokenResponse
        class UserResponse
        class JobCreate
        class JobResponse
        class JobUpdatePriority
        class JobResultResponse
        class PaymentCreate
        class PaymentResponse
        class ReportSummary
        class UserReportResponse
    }

    namespace Core {
        class Settings {
            <<pydantic>>
            +str DATABASE_URL
            +str SECRET_KEY
            +int QUEUE_MAX_SIZE
            +int PAYMENT_WORKERS
            +float COMMISSION_RATE
        }
        class RichConsole {
            <<singleton>>
            +Console console
            +Theme _acs_theme
        }
        class Database {
            +Engine engine
            +SessionLocal sessionmaker
            +Base declarative_base
        }
        class FastAPIApp {
            +create_app() FastAPI
        }
    }

    %% ═══════════════════════════════════════════════════════════════
    %% RELACIONES DE HERENCIA / REALIZACIÓN DE INTERFACES
    %% ═══════════════════════════════════════════════════════════════
    UserRepository <|.. SQLUserRepository : implements
    JobRepository <|.. SQLJobRepository : implements
    BalanceRepository <|.. InMemoryBalanceRepository : implements
    PaymentRepository <|.. SQLPaymentRepository : implements
    PaymentWorker --|> threading.Thread : extends

    %% ═══════════════════════════════════════════════════════════════
    %% RELACIONES DE DEPENDENCIA / COMPOSICIÓN
    %% ═══════════════════════════════════════════════════════════════

    %% Application → Domain
    AuthService ..> UserRepository : usa
    AuthService ..> Email : valida
    AuthService ..> Password : valida
    JobService ..> JobRepository : usa
    ProcessTextService ..> JobRepository : usa
    ProcessTextService ..> JobCompletedEvent : emite
    NotificationService ..> JobCompletedEvent : recibe

    %% Application → Infrastructure
    AuthService ..> JWTHandler : bcrypt + JWT
    JobService ..> JobModel : consulta
    ProcessTextService ..> TextResultModel : crea
    PaymentService --> WorkerPoolManager : orquesta
    PaymentService ..> PaymentQueue : encola
    ReportService ..> UserModel : consulta
    ReportService ..> JobModel : consulta
    ReportService ..> TextResultModel : consulta
    ReportService ..> MetricsCollector : snapshot
    NotificationService --> WebSocketManager : dispatch

    %% Infrastructure internal
    WorkerPoolManager --> PaymentWorker : crea hilos
    WorkerPoolManager --> PaymentQueue : comparte cola
    WorkerPoolManager --> InMemoryBalanceRepository : comparte repo
    WorkerPoolFactory ..> WorkerPoolManager : factory
    WorkerPoolFactory ..> PaymentQueue : configura prioridad
    PaymentWorker --> PaymentQueue : dequeue
    PaymentWorker --> InMemoryBalanceRepository : add_funds
    PaymentWorker --> PaymentConfig : get_rate
    PaymentConfig --> ReadWriteLock : protege tasas
    PaymentConfig ..> ReadWriteLock : acquire/release read
    PaymentConfig ..> ReadWriteLock : acquire/release write
    SQLUserRepository ..> UserModel : ORM
    SQLJobRepository ..> JobModel : ORM
    SQLPaymentRepository ..> PaymentModel : ORM

    %% Presentation → Application
    AuthRoutes --> AuthService : invoca
    JobRoutes --> JobService : invoca
    JobRoutes --> ProcessTextService : invoca
    JobRoutes --> NotificationService : background
    PaymentRoutes --> PaymentService : invoca
    ReportRoutes --> ReportService : invoca
    Dependencies ..> UnitOfWork : inyecta
    Dependencies ..> JWTHandler : decode

    %% Presentation ↔ Infrastructure
    WebSocketRoutes --> WebSocketManager : connect/notify
    AuthRoutes ..> UserRegister : DTO
    AuthRoutes ..> UserLogin : DTO
    AuthRoutes ..> TokenResponse : DTO
    JobRoutes ..> JobCreate : DTO
    JobRoutes ..> JobResponse : DTO
    JobRoutes ..> JobUpdatePriority : DTO
    JobRoutes ..> JobResultResponse : DTO
    PaymentRoutes ..> PaymentCreate : DTO
    PaymentRoutes ..> PaymentResponse : DTO
    ReportRoutes ..> ReportSummary : DTO
    ReportRoutes ..> UserReportResponse : DTO

    %% Core → All
    Settings --> Database : configura
    Database ..> UnitOfWork : SessionLocal
    FastAPIApp --> AuthRoutes : include_router
    FastAPIApp --> JobRoutes : include_router
    FastAPIApp --> PaymentRoutes : include_router
    FastAPIApp --> ReportRoutes : include_router
    FastAPIApp --> WebSocketRoutes : include_router

    %% ═══════════════════════════════════════════════════════════════
    %% ESTILOS
    %% ═══════════════════════════════════════════════════════════════
    style PaymentRequest fill:#1a237e,stroke:#3949ab,color:#fff
    style User fill:#1a237e,stroke:#3949ab,color:#fff
    style Job fill:#1a237e,stroke:#3949ab,color:#fff
    style TextResult fill:#1a237e,stroke:#3949ab,color:#fff

    style Email fill:#311b92,stroke:#651fff,color:#fff
    style Password fill:#311b92,stroke:#651fff,color:#fff

    style JobCompletedEvent fill:#004d40,stroke:#00bfa5,color:#fff

    style BalanceRepository fill:#1b5e20,stroke:#4caf50,color:#fff
    style PaymentRepository fill:#1b5e20,stroke:#4caf50,color:#fff
    style UserRepository fill:#1b5e20,stroke:#4caf50,color:#fff
    style JobRepository fill:#1b5e20,stroke:#4caf50,color:#fff

    style AuthService fill:#e65100,stroke:#ff9800,color:#fff
    style JobService fill:#e65100,stroke:#ff9800,color:#fff
    style ProcessTextService fill:#e65100,stroke:#ff9800,color:#fff
    style ReportService fill:#e65100,stroke:#ff9800,color:#fff
    style NotificationService fill:#e65100,stroke:#ff9800,color:#fff
    style PaymentService fill:#e65100,stroke:#ff9800,color:#fff

    style UnitOfWork fill:#bf360c,stroke:#f4511e,color:#fff

    style PaymentQueue fill:#4a148c,stroke:#7b1fa2,color:#fff
    style ReadWriteLock fill:#4a148c,stroke:#7b1fa2,color:#fff
    style PaymentConfig fill:#4a148c,stroke:#7b1fa2,color:#fff
    style PaymentWorker fill:#4a148c,stroke:#7b1fa2,color:#fff
    style WorkerPoolManager fill:#4a148c,stroke:#7b1fa2,color:#fff
    style WorkerPoolFactory fill:#4a148c,stroke:#7b1fa2,color:#fff
    style JWTHandler fill:#4a148c,stroke:#7b1fa2,color:#fff
    style WebSocketManager fill:#4a148c,stroke:#7b1fa2,color:#fff
    style MetricsCollector fill:#4a148c,stroke:#7b1fa2,color:#fff

    style SQLUserRepository fill:#006064,stroke:#00bcd4,color:#fff
    style SQLJobRepository fill:#006064,stroke:#00bcd4,color:#fff
    style SQLPaymentRepository fill:#006064,stroke:#00bcd4,color:#fff
    style InMemoryBalanceRepository fill:#006064,stroke:#00bcd4,color:#fff
    style UserModel fill:#006064,stroke:#00bcd4,color:#fff
    style JobModel fill:#006064,stroke:#00bcd4,color:#fff
    style TextResultModel fill:#006064,stroke:#00bcd4,color:#fff
    style PaymentModel fill:#006064,stroke:#00bcd4,color:#fff

    style AuthRoutes fill:#2c3e50,stroke:#546e7a,color:#fff
    style JobRoutes fill:#2c3e50,stroke:#546e7a,color:#fff
    style PaymentRoutes fill:#2c3e50,stroke:#546e7a,color:#fff
    style ReportRoutes fill:#2c3e50,stroke:#546e7a,color:#fff
    style WebSocketRoutes fill:#2c3e50,stroke:#546e7a,color:#fff
    style Dependencies fill:#2c3e50,stroke:#546e7a,color:#fff

    style Settings fill:#3e2723,stroke:#795548,color:#fff
    style RichConsole fill:#3e2723,stroke:#795548,color:#fff
    style Database fill:#3e2723,stroke:#795548,color:#fff
    style FastAPIApp fill:#3e2723,stroke:#795548,color:#fff
```

## Leyenda de Colores

| Color | Capa / Responsabilidad |
|---|---|
| Azul oscuro (`#1a237e`) | **Domain Entities** — Entidades de negocio puras |
| Violeta (`#311b92`) | **Domain Value Objects** — Objetos de valor inmutables |
| Verde oscuro (`#004d40`) | **Domain Events** — Eventos de dominio |
| Verde (`#1b5e20`) | **Domain Interfaces** — Contratos de repositorio |
| Naranja (`#e65100`) | **Application Services** — Casos de uso / lógica de aplicación |
| Rojo oscuro (`#bf360c`) | **Unit of Work** — Gestión transaccional |
| Púrpura (`#4a148c`) | **Infrastructure** — Implementaciones técnicas (sync, workers, queue, JWT, WS, metrics) |
| Cian (`#006064`) | **Infrastructure Persistence** — ORM models y repositorios SQL |
| Gris azulado (`#2c3e50`) | **Presentation** — Endpoints FastAPI, DTOs, WebSocket |
| Marrón (`#3e2723`) | **Core** — Configuración, base de datos, aplicación principal |

## Patrones de Diseño Aplicados

| Símbolo Mermaid | Patrón | Clases involucradas |
|---|---|---|
| `..|>` | **Repository** | `UserRepository`, `JobRepository`, `BalanceRepository`, `PaymentRepository` → implementaciones SQL/InMemory |
| `UnitOfWork` con `begin()` contextmanager | **Unit of Work** | `UnitOfWork` → maneja commit/rollback atómico sobre `Session` |
| `<<singleton>>` | **Singleton** | `PaymentQueue`, `PaymentConfig`, `MetricsCollector`, `RichConsole` |
| `WorkerPoolFactory ..> WorkerPoolManager` | **Factory** | `WorkerPoolFactory.create_pool()` → `WorkerPoolManager` |
| `InMemoryBalanceRepository` con `Lock` | **Thread-Safe Object** | `InMemoryBalanceRepository` protege acceso concurrente |
| `ReadWriteLock` con `Condition` | **Reader-Writer Lock** | `ReadWriteLock` → `PaymentConfig` (lectura concurrente + prioridad escritor) |
| `PaymentWorker` con `<<thread>>` | **Producer-Consumer** | `PaymentQueue` (cola) → `PaymentWorker` (consumidores) |
| `JobCompletedEvent` + `NotificationService` | **Observer** | `ProcessTextService` emite evento → `WebSocketManager` notifica |
