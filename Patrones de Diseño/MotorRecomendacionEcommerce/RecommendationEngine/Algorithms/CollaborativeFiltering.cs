// Recommendengine/Algorithms/CollaborativeFiltering.cs
using RecommendationEngine.Catalog;
namespace RecommendationEngine.Algorithms
{
  public class CollaborativeFiltering : IRecommendationStrategy
  {
    public List<Product> Recommend(int userId, List<Product> allProducts)
    {
      Console.WriteLine("[Algoritmo] Ejecutando Filtrado Colaborativo (User-to-User)...");
      // Lógica simulada: Tomar los primeros 3 productos de la lista
      return allProducts.Take(3).ToList();
    }
  }
}