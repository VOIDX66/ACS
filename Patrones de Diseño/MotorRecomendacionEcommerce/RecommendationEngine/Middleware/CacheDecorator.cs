using RecommendationEngine.Algorithms;
using RecommendationEngine.Catalog;

namespace RecommendationEngine.Middleware;

public class CacheDecorator : IRecommendationStrategy
{
  private readonly IRecommendationStrategy _inner;
  private static readonly Dictionary<int, List<Product>> _cache = new();

  public CacheDecorator(IRecommendationStrategy inner) => _inner = inner;

  public List<Product> Recommend(int userId, List<Product> allProducts)
  {
    if (_cache.TryGetValue(userId, out var cachedResults))
    {
      Console.WriteLine($"[CACHE] HIT para usuario {userId}. Saltando ejecución de algoritmo.");
      return cachedResults;
    }

    var results = _inner.Recommend(userId, allProducts);
    _cache[userId] = results;

    return results;
  }
}