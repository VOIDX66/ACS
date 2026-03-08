// RecommendationEngine/Algorithms/Interfaces/IRecommendationStrategy.cs
using RecommendationEngine.Catalog;
namespace RecommendationEngine.Algorithms
{
  public interface IRecommendationStrategy
  {
    List<Product> Recommend(int userId, List<Product> allProducts);
  }
}