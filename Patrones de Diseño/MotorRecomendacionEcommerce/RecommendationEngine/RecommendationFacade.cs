// RecommendationEngine/RecommendationFacade.cs
using RecommendationEngine.Algorithms;
using RecommendationEngine.Catalog;
using RecommendationEngine.PostProcessing;
using RecommendationEngine.Middleware;
using RecommendationEngine.Settings;

namespace RecommendationEngine;

public class RecommendationFacade
{
  private readonly IProductRepository _repository;

  public RecommendationFacade(IProductRepository repository)
  {
    _repository = repository;
  }

  public List<Product> GetRecommendations(int userId)
  {
    // 1. EXTRAER: Obtenemos el catálogo completo del Repositorio (SQL)
    var allProducts = _repository.GetAll();

    // 2. CREAR ESTRATEGIA: La Factory decide según el Singleton (EngineConfig)
    // Podría devolver CollaborativeFiltering, ContentBasedFiltering o AmazonMLAdapter
    IRecommendationStrategy strategy = AlgorithmFactory.CreateDefault();

    // 3. ENVOLVER (MIDDLEWARE): Aplicamos Decoradores para Cache y Telemetría
    // El orden es: Logging envuelve a Cache, Cache envuelve a la Estrategia real
    strategy = new LoggingDecorator(new CacheDecorator(strategy));

    // 4. GENERAR: El algoritmo (o el adaptador) genera la lista base
    var rawList = strategy.Recommend(userId, allProducts);

    // 5. FILTRAR (CHAIN OF RESPONSIBILITY): Purificamos los resultados
    var stockFilter = new StockFilter();
    var blacklistFilter = new BlacklistFilter();

    // Configuramos la cadena: Primero Stock, luego Blacklist
    stockFilter.SetNext(blacklistFilter);

    // 6. RETORNAR: La lista final "limpia" de reglas de negocio
    return stockFilter.Filter(rawList, userId);
  }
}