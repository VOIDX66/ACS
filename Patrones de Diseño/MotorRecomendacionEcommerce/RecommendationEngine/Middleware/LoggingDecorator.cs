// RecommendationEngine/Middleware/LoggingDecorator.cs
using System.Diagnostics;
using RecommendationEngine.Catalog;
using RecommendationEngine.Algorithms;
namespace RecommendationEngine.Middleware
{
  public class LoggingDecorator : IRecommendationStrategy
  {
    private readonly IRecommendationStrategy _inner;

    public LoggingDecorator(IRecommendationStrategy inner)
    {
      _inner = inner;
    }

    public List<Product> Recommend(int userId, List<Product> allProducts)
    {
      var sw = Stopwatch.StartNew();
      var results = _inner.Recommend(userId, allProducts);
      sw.Stop();
      Console.WriteLine($"[LOG] Estrategia ejecutada | Usuario: {userId} | Tiempo: {sw.ElapsedMilliseconds} ms");
      return results;
    }
  }
}