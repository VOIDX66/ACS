// RecommendationEngine/PostProcessing/BlackListFilter.cs
using RecommendationEngine.Catalog;

namespace RecommendationEngine.PostProcessing;

public class BlacklistFilter : BaseFilter
{
  public override List<Product> Filter(List<Product> products, int userId)
  {
    Console.WriteLine("[Filtro] Aplicando exclusiones (Blacklist) para el usuario...");

    // Simulación: El ID 999 está prohibido por negocio
    var filtered = products.Where(p => p.Id != 999).ToList();

    return base.Filter(filtered, userId);
  }
}