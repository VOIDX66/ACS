# Ejercicio 6: Sistema de Reservas para Aerolínea.

El sistema debe implementar una estructura flexible para la construcción de reservas que permita ensamblar objetos complejos paso a paso, considerando que una reserva puede incluir pasajero, vuelo, precio base, servicios adicionales y preferencias específicas; por ello, el patrón **Builder** en ReservationBuilder proporciona un mecanismo fluido y controlado para construir objetos `Reservation` con diferentes configuraciones, evitando constructores telescópicos y garantizando que el objeto resultante sea consistente antes de ser utilizado. Ante la necesidad de calcular tarifas dinámicamente según el tipo de clase (económica, premium, primera clase), temporada del año o anticipación de la compra, el patrón **Strategy** encapsula los diferentes algoritmos de cálculo de precios (EconomyPricing, PremiumPricing), permitiendo que cada reserva seleccione la estrategia adecuada en tiempo de ejecución sin modificar la lógica central de la reserva. Considerando que las reservas atraviesan diferentes estados durante su ciclo de vida (pendiente, confirmada, cancelada, check-in realizado, abordada), el patrón **State** modela estos comportamientos específicos mediante clases separadas (PendingState, ConfirmedState, CancelledState), permitiendo que la reserva cambie su comportamiento cuando su estado interno cambia, lo que facilita la implementación de reglas de negocio como "solo se pueden modificar reservas en estado pendiente" o "las reservas canceladas no generan cargos adicionales". Para mantener informados a los pasajeros y agentes de viaje sobre cambios en el estado de las reservas (confirmación, cancelación, cambios de horario), el patrón **Observer** desacopla la lógica de la reserva de los mecanismos de notificación, permitiendo que múltiples observadores (EmailNotifier, SMSNotifier, AppNotifier) sean notificados automáticamente cuando ocurren eventos relevantes, sin acoplar el núcleo del sistema a implementaciones específicas de mensajería. Finalmente, la interfaz unificada proporcionada por el builder, combinada con la flexibilidad de las estrategias de precios, la máquina de estados y el sistema de notificaciones, crea una arquitectura cohesiva donde los objetos reserva se construyen de manera controlada, responden dinámicamente a cambios de contexto y mantienen informados a todos los interesados, cumpliendo con los exigentes requisitos de disponibilidad, confiabilidad y escalabilidad propios de los sistemas de reservas aerocomerciales. Esta arquitectura basada en patrones garantiza un sistema extensible, mantenible y preparado para incorporar nuevos tipos de tarifas, estados adicionales (como overbooking o lista de espera) y canales de notificación emergentes sin afectar la estabilidad del núcleo del sistema.

**Objetivo:** Diseñar un sistema que gestione reservas complejas con cambios dinámicos de estado y cálculo flexible de precios.  
**Competencias específicas**

- Modelar comportamiento con State.
- Implementar precios dinámicos con Strategy.
- Construir objetos complejos con Builder.
- Notificar eventos con Observer.

**Contexto**  
Debe manejar:

- Reservas.
- Asientos.
- Pagos.
- Cancelaciones.

**Requerimientos técnicos**

- Calcular precios dinámicos.
- Notificar cambios.
- Permitir upgrades.

**Patrones involucrados**

- Strategy (cálculo de precio)
- Observer (notificaciones)
- State (estado de reserva)
- Builder (construcción de reserva compleja)

**Preguntas de reflexión**

- ¿Qué problemas genera usar múltiples condicionales para estados?
- ¿Cómo facilita Builder la creación de reservas complejas?
- ¿Qué ocurre si cambian las reglas de precio?
- ¿Cómo desacoplar notificaciones?
- ¿Qué patrón mejora cohesión en cambios de estado?
