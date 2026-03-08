// ReommendationEngine/ExternalServices/AmazonMLAdapter.cs
using RecommendationEngine.Algorithms;
using RecommendationEngine.Catalog;
namespace RecommendationEngine.ExternalServices
{
  public class AmazonMLAdapter : IRecommendationStrategy
  {
    private readonly IExternalPredictor _amazonService;

    public AmazonMLAdapter(IExternalPredictor amazonService)
    {
      _amazonService = amazonService;
    }

    public List<Product> Recommend(int userId, List<Product> allProducts)
    {
      Console.WriteLine("[Adapter] Solicitando predicciones a Amazon ML...");

      // Llamada al servicio externo
      var predictedProducts = _amazonService.GetExternalPredictions(userId);
      // Adaptacion, convertimos los productos externos a productos internos
      return allProducts
        .Where(p => predictedProducts.Contains(p.Name))
        .ToList();
    }
  }
}