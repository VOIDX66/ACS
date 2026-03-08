// RecommendationEngine/Algorithms/ContentBasedFiltering.cs
using RecommendationEngine.Catalog;
namespace RecommendationEngine.Algorithms
{
  public class ContentBasedFiltering : IRecommendationStrategy
  {
    public List<Product> Recommend(int userId, List<Product> allProducts)
    {
      Console.WriteLine($"[Algoritmo] Filtrando Contenido para el usuario {userId}...");
      // Lógica simulada: Tomar los productos de la mitad de la lista
      return allProducts.Skip(allProducts.Count / 2).Take(3).ToList();
    }
  }
}