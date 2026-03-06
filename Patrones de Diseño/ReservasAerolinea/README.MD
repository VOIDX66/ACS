# Ejercicio 10: Motor de Recomendación para E-commerce.

El sistema requiere una configuración global unificada que establezca parámetros transversales como la estrategia de recomendación predeterminada (actualmente "collaborative"), umbrales de similitud y ventanas de tiempo para análisis de comportamiento, por lo que el patrón **Singleton** implementado en RecommendationConfig garantiza que todos los módulos del motor accedan a la misma instancia de configuración, permitiendo ajustes centralizados sin riesgos de inconsistencia en un entorno donde múltiples usuarios y sesiones generan recomendaciones simultáneamente. Ante la diversidad de algoritmos de recomendación que pueden implementarse (filtrado colaborativo, basado en contenido, híbrido, basado en tendencias, etc.), cada uno con diferentes enfoques matemáticos y requisitos computacionales, el patrón **Strategy** encapsula estos algoritmos en clases separadas (CollaborativeFilteringStrategy, ContentBasedStrategy, HybridStrategy), permitiendo que el motor seleccione dinámicamente la estrategia más adecuada según el contexto del usuario, el tipo de producto o la campaña promocional activa. Considerando la necesidad de instanciar estratégicamente estos algoritmos según la configuración global o preferencias específicas del usuario, el patrón **Factory Method** en RecommendationStrategyFactory centraliza la creación de objetos `RecommendationStrategy`, encapsulando la lógica de selección y facilitando la incorporación de nuevos algoritmos de recomendación (como redes neuronales o modelos basados en grafos) sin modificar el código cliente que los consume. Para la persistencia y recuperación eficiente del catálogo de productos, el patrón **Repository** abstrae el acceso a la fuente de datos (actualmente una lista en memoria, pero preparado para migrar a bases de datos SQL, NoSQL o índices de búsqueda como Elasticsearch), proporcionando una interfaz consistente para operaciones de consulta que alimentan los algoritmos de recomendación. Ante la necesidad de integrar servicios externos de machine learning que pueden generar predicciones más sofisticadas basadas en grandes volúmenes de datos, el patrón **Adapter** normaliza la comunicación envolviendo APIs externas no modificables (ExternalMLService) y proporcionando una interfaz uniforme (MLServiceAdapter) que el motor puede consumir independientemente del proveedor de ML, facilitando la incorporación de múltiples fuentes de inteligencia artificial. Para optimizar el rendimiento y evitar recomputaciones innecesarias, así como para mantener trazabilidad de las operaciones, el patrón **Decorator** permite añadir dinámicamente responsabilidades transversales al motor base (CacheDecorator para almacenar resultados previos, LoggingDecorator para registrar actividades) sin modificar la lógica central de recomendación, envolviendo objetos `RecommendationEngine` de manera transparente y permitiendo combinaciones flexibles según las necesidades del entorno de producción. En cuanto a la captura de eventos para análisis de negocio y retroalimentación del sistema, el patrón **Observer** desacopla la generación de recomendaciones de los mecanismos de notificación, permitiendo que cada recomendación generada notifique automáticamente a múltiples observadores (AnalyticsObserver para métricas de negocio, EmailObserver para campañas de marketing) sin acoplar el núcleo del motor a implementaciones específicas de análisis o comunicación. Finalmente, el patrón **Facade** en RecommendationFacade ofrece una interfaz simplificada que unifica todas estas capacidades (configuración global, selección de estrategia mediante fábrica, consulta de productos vía repositorio, aplicación de algoritmos estratégicos, integración con servicios ML mediante adaptador, decoración con cache y logging, y notificación a observadores), ocultando la complejidad subyacente y proporcionando un punto de entrada único que los equipos de desarrollo de frontend, aplicaciones móviles o servicios de personalización pueden consumir mediante una operación intuitiva como `get_recommendations(user_id)`. Esta arquitectura basada en patrones garantiza un motor de recomendación robusto, extensible y preparado para escalar conforme crezca el catálogo de productos y la base de usuarios, incorporando nuevos algoritmos de recomendación basados en deep learning, fuentes de datos en tiempo real, estrategias de cache distribuida y canales de análisis avanzados sin comprometer la estabilidad del núcleo del sistema.

**Objetivo:** Diseñar un sistema modular que combine múltiples algoritmos de recomendación.  
**Competencias específicas**

- Diseñar algoritmos intercambiables.
- Encadenar filtros.
- Decorar recomendaciones.
- Centralizar configuración.

**Contexto**  
Empresa quiere:

- Recomendaciones por historial.
- Recomendaciones por tendencia.
- Recomendaciones por perfil.

**Requerimientos técnicos**

- Permitir nuevos algoritmos.
- Encadenar filtros.
- Registrar comportamiento del usuario.

**Patrones involucrados**

- Strategy (algoritmos de recomendación)
- Chain of Responsibility (filtros)
- Decorator (personalización adicional)
- Singleton (gestor de configuración)

**Preguntas de reflexión**

- ¿Cómo permitir nuevos algoritmos?
- ¿Qué ventaja ofrece Decorator?
- ¿Por qué usar Chain of Responsibility?
- ¿Qué problema resuelve Singleton?
- ¿Cómo impacta en rendimiento y mantenimiento?
