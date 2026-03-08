// RecommendationEngine/PostProcessing/BaseFilter.cs
using RecommendationEngine.Catalog;

namespace RecommendationEngine.PostProcessing;

public abstract class BaseFilter : IRecommendationFilter
{
  private IRecommendationFilter? _next;

  public IRecommendationFilter SetNext(IRecommendationFilter next)
  {
    _next = next;
    return next; // Retornamos el siguiente para permitir encadenamiento fluido (Fluent API)
  }

  public virtual List<Product> Filter(List<Product> products, int userId)
  {
    // Si no hay más filtros, devolvemos la lista actual.
    // Si hay uno, le pasamos el resultado de nuestro filtrado.
    return _next?.Filter(products, userId) ?? products;
  }
}