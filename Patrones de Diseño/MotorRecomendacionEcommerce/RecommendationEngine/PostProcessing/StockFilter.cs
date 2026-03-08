// RecommendationEngine/PostProcessing/StockFilter.cs
using RecommendationEngine.Catalog;

namespace RecommendationEngine.PostProcessing;

public class StockFilter : BaseFilter
{
  public override List<Product> Filter(List<Product> products, int userId)
  {
    Console.WriteLine("[Filtro] Eliminando productos sin stock...");

    var filtered = products.Where(p => p.InStock).ToList();

    // Llamamos al siguiente eslabón de la cadena
    return base.Filter(filtered, userId);
  }
}