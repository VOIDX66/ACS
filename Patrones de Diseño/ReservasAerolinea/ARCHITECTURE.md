# Arquitectura del Sistema de Reservas de Aerolínea

## Diagrama de Clases

```mermaid
classDiagram
    direction TB

    namespace Reservations_Feature {
        class Reservation {
            +string PassengerName
            +string PassportNumber
            +string FlightNumber
            +string SeatNumber
            +decimal BasePrice
            +List~string~ AdditionalServices
            -IReservationState _currentState
            +IPricingStrategy PricingStrategy
            -List~IReservationObserver~ _observers
            +TransitionTo(IReservationState)
            +GetTotal() decimal
            +Confirmar()
            +Cancelar()
            +RealizarCheckIn()
            +Subscribe(IReservationObserver)
        }

        class ReservationBuilder {
            -Reservation _reservation
            +ConPasejero(name, passport)
            +ParaVuelo(flight, seat)
            +ConPrecioBase(price, strategy)
            +AgregarServicioExtra(service)
            +Build() Reservation
        }
    }

    namespace Lifecycle_State {
        class IReservationState {
            <<interface>>
            +Confirmar(Reservation)
            +Cancelar(Reservation)
            +RealizarCheckIn(Reservation)
        }
        class PendingState
        class ConfirmedState
        class CancelledState
    }

    namespace Pricing_Strategy {
        class IPricingStrategy {
            <<interface>>
            +GetTotal(decimal) decimal
        }
        class EconomyPricing
        class PremiumPricing
        class HolidayPricing
    }

    namespace Notifications_Observer {
        class IReservationObserver {
            <<interface>>
            +Update(Reservation, string)
        }
        class EmailNotifier
        class SmsNotifier
        class AppNotifier
    }

    %% Relaciones de Construcción
    ReservationBuilder ..> Reservation : Instancia y Configura

    %% Relaciones de Estado
    Reservation o-- IReservationState : Posee
    IReservationState <|.. PendingState
    IReservationState <|.. ConfirmedState
    IReservationState <|.. CancelledState

    %% Relaciones de Estrategia
    Reservation o-- IPricingStrategy : PricingStrategy
    IPricingStrategy <|.. EconomyPricing
    IPricingStrategy <|.. PremiumPricing
    IPricingStrategy <|.. HolidayPricing

    %% Relaciones de Observación
    Reservation o-- IReservationObserver : Notifica
    IReservationObserver <|.. EmailNotifier
    IReservationObserver <|.. SmsNotifier
    IReservationObserver <|.. AppNotifier

    %% Estilos Profesionales
    style Reservation fill:#1a237e,stroke:#3949ab,color:#fff
    style ReservationBuilder fill:#2c3e50,stroke:#546e7a,color:#fff
    style IReservationState fill:#4a148c,stroke:#7b1fa2,color:#fff
    style IPricingStrategy fill:#1b4d3e,stroke:#2e7d32,color:#fff
    style IReservationObserver fill:#e65100,stroke:#ef6c00,color:#fff
```

---

## Patrones de Diseño Implementados

### 1. Builder Pattern - ReservationBuilder

**Ubicación:** `Reservations/ReservationBuilder.cs`

**Propósito:** Construir objetos `Reservation` complejos paso a paso sin constructores telescópicos.

**Implementación:**
- `ReservationBuilder` permite encadenar métodos fluent:
  - `ConPasejero(string nombre, string pasaporte)` - Define el pasajero
  - `ParaVuelo(string numeroVuelo, string asiento)` - Define el vuelo y asiento
  - `ConPrecioBase(decimal precio, IPricingStrategy estrategia)` - Define precio y estrategia
  - `AgregarServicioExtra(string servicio)` - Agrega servicios adicionales
- Valida reglas de negocio en `Build()` antes de retornar la reserva
- El builder es reutilizable (crea nueva instancia después de cada Build)

**Validaciones del Builder:**
- No se puede construir una reserva sin pasajero
- Toda reserva debe tener una estrategia de precio definida

---

### 2. Strategy Pattern - IPricingStrategy

**Ubicación:** 
- Interfaz: `Reservations/Pricing/Interfaces/IPricingStrategy.cs`
- Implementaciones: `Reservations/Pricing/EconomyPricing.cs`, `Reservations/Pricing/HolidayPricing.cs`

**Propósito:** Encapsular diferentes algoritmos de cálculo de precios permitiendo selección dinámica en tiempo de ejecución.

**Implementación:**
- Interfaz `IPricingStrategy` define el contrato `GetTotal(decimal basePrice)`
- Estrategias disponibles:
  - `EconomyPricing` - Precio clase económica
  - `PremiumPricing` - Precio clase premium
  - `HolidayPricing` - Precio temporada alta
- Cada reserva tiene una propiedad `PricingStrategy` que calcula el total

---

### 3. State Pattern - IReservationState

**Ubicación:**
- Interfaz: `Reservations/LifeCycle/Interfaces/IReservationState.cs`
- Estados: `Reservations/LifeCycle/PendingState.cs`, `ConfirmedState.cs`, `CancelledState.cs`

**Propósito:** Modelar el comportamiento específico de cada estado de la reserva, permitiendo cambiar el comportamiento dinámicamente.

**Implementación:**
- Interfaz `IReservationState` define métodos: `Confirmar`, `Cancelar`, `RealizarCheckIn`
- Estados concretos:
  - `PendingState` - Estado inicial, permite confirmar o cancelar
  - `ConfirmedState` - Reserva confirmada, permite check-in
  - `CancelledState` - Reserva cancelada, estado terminal
- La clase `Reservation` mantiene una referencia al estado actual y delega comportamiento

---

### 4. Observer Pattern - IReservationObserver

**Ubicación:**
- Interfaz: `Reservations/Notifications/Interfaces/IReservationObserver.cs`
- Implementaciones: `Reservations/Notifications/EmailNotifier.cs`, `SmsNotifier.cs`

**Propósito:** Desacoplar la lógica de la reserva de los mecanismos de notificación, permitiendo múltiples observadores.

**Implementación:**
- Interfaz `IReservationObserver` define el método `Update(Reservation reservation, string message)`
- Observadores concretos:
  - `EmailNotifier` - Notifica por correo electrónico
  - `SmsNotifier` - Notifica por SMS
  - `AppNotifier` - Notifica en la aplicación
- La reserva mantiene una lista de observadores y notifica cambios de estado automáticamente

---

## Estructura del Proyecto

```
ReservasAerolinea/
├── Reservations/
│   ├── Reservation.cs                 # Clase principal de la reserva
│   ├── ReservationBuilder.cs          # Constructor de reservas (Builder)
│   ├── Pricing/
│   │   ├── Interfaces/
│   │   │   └── IPricingStrategy.cs    # Interfaz Strategy
│   │   ├── EconomyPricing.cs          # Estrategia precio económica
│   │   └── HolidayPricing.cs          # Estrategia precio temporada alta
│   ├── LifeCycle/
│   │   ├── Interfaces/
│   │   │   └── IReservationState.cs   # Interfaz State
│   │   ├── PendingState.cs            # Estado pendiente
│   │   ├── ConfirmedState.cs          # Estado confirmada
│   │   └── CancelledState.cs          # Estado cancelada
│   └── Notifications/
│       ├── Interfaces/
│       │   └── IReservationObserver.cs # Interfaz Observer
│       ├── EmailNotifier.cs            # Notificador email
│       └── SmsNotifier.cs              # Notificador SMS
└── Program.cs                         # Punto de entrada
```

---

## Flujo de Uso Típico

1. **Construcción:** Se usa `ReservationBuilder` para crear una reserva
2. **Suscripción:** Se registran observadores (Email, SMS) para recibir notificaciones
3. **Confirmación:** Se llama `Confirmar()` que cambia el estado a `ConfirmedState`
4. **Cálculo:** Se usa `GetTotal()` para obtener el precio final según la estrategia
5. **Check-in:** Solo disponible desde estado confirmado

---

## Resumen de Patrones

| Patrón | Interfaz/Clase Base | Implementaciones |
|--------|---------------------|------------------|
| **Builder** | `ReservationBuilder` | - |
| **Strategy** | `IPricingStrategy` | `EconomyPricing`, `PremiumPricing`, `HolidayPricing` |
| **State** | `IReservationState` | `PendingState`, `ConfirmedState`, `CancelledState` |
| **Observer** | `IReservationObserver` | `EmailNotifier`, `SmsNotifier`, `AppNotifier` |
