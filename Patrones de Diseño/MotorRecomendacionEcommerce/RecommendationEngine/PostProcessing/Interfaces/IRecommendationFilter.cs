// RecommendationEngine/PostProcessing/Interfaces/IRecommendationFilter.cs
using RecommendationEngine.Catalog;
namespace RecommendationEngine.PostProcessing
{
  public interface IRecommendationFilter
  {
    IRecommendationFilter SetNext(IRecommendationFilter next);
    List<Product> Filter(List<Product> products, int userId);
  }
}