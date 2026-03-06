# Ejercicio 5: Motor de Procesamiento de Pagos Internacionales.

El sistema debe garantizar una configuración unificada y consistente para parámetros globales como la moneda predeterminada (USD), tasas de cambio base y umbrales de seguridad, por lo que el patrón **Singleton** implementado en PaymentConfig asegura que todos los módulos del motor de pagos accedan a la misma instancia de configuración, evitando inconsistencias críticas en operaciones financieras transfronterizas. Considerando la diversidad de métodos de pago que deben soportarse en diferentes regiones (tarjetas de crédito, transferencias bancarias SEPA/ACH, criptomonedas, billeteras digitales), el patrón **Factory Method** en PaymentFactory centraliza la creación de estos objetos, permitiendo incorporar nuevos métodos de pago específicos por país sin modificar la lógica central del procesador. Para el cálculo dinámico de comisiones, que varían según el tipo de cliente (estándar, premium) y la naturaleza internacional de la transacción, el patrón **Strategy** encapsula los diferentes algoritmos de comisión (StandardCommission, PremiumCommission, InternationalCommission), facilitando la selección en tiempo de ejecución basada en el perfil del comercio y las regulaciones locales. Ante la necesidad crítica de validación antifraude multicapa, el patrón **Chain of Responsibility** permite encadenar verificaciones progresivas (montos sospechosos, países de alto riesgo, patrones de comportamiento anómalos), donde cada eslabón puede procesar la solicitud o pasarla al siguiente, proporcionando flexibilidad para agregar nuevas reglas de seguridad sin acoplar la lógica de validación. Para la integración con múltiples pasarelas de pago externas (Stripe, PayPal, MercadoPago) que presentan interfaces heterogéneas, el patrón **Adapter** normaliza la comunicación, envolviendo APIs externas no modificables y proporcionando una interfaz uniforme que el motor principal puede consumir independientemente del proveedor subyacente. En cuanto a la notificación de eventos transaccionales, el patrón **Observer** desacopla el procesamiento de pagos de los mecanismos de notificación, permitiendo que cada transacción exitosa o fallida notifique automáticamente a comerciantes y clientes a través de múltiples canales (email, SMS, webhooks) sin modificar la lógica central. Finalmente, el patrón **Facade** en PaymentFacade ofrece una interfaz simplificada que unifica todas estas capacidades (selección de método de pago, cálculo de comisiones, validación antifraude, procesamiento con gateway externo y notificaciones), ocultando la complejidad subyacente y proporcionando un punto de entrada único que los equipos de integración pueden consumir mediante una simple llamada `pay(method_type, amount, country)`. Esta arquitectura basada en patrones garantiza un motor de pagos internacional robusto, extensible y preparado para escalar conforme se expanda a nuevos mercados, con nuevos métodos de pago, regulaciones locales y proveedores de servicios financieros.

**Objetivo:** Diseñar un motor flexible que valide, procese y adapte pagos según país y regulación.  
**Competencias específicas**

- Encadenar validaciones con Chain of Responsibility.
- Definir flujo base con Template Method.
- Crear procesadores por región con Factory.
- Aplicar Strategy para conversión monetaria.

**Contexto**  
Empresa global procesa pagos con:

- Diferentes monedas.
- Diferentes regulaciones.
- Validaciones antifraude.

**Requerimientos técnicos**

- Aplicar validaciones encadenadas.
- Convertir monedas dinámicamente.
- Crear procesadores según país.

**Patrones involucrados**

- Chain of Responsibility (validaciones)
- Factory Method (procesadores por país)
- Strategy (conversión de moneda)
- Template Method (flujo general del pago)

**Preguntas de reflexión**

- ¿Qué ventaja tiene encadenar validaciones?
- ¿Cómo evitar múltiples if por país?
- ¿Qué parte del algoritmo debe ser invariable?
- ¿Cómo escalar a nuevos países?
- ¿Qué patrón reduce duplicación de lógica?
