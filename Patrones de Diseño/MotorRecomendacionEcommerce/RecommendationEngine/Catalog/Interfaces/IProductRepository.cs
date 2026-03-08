// Recommendation/Catalog/Interfaces/IProductRepository.cs
namespace RecommendationEngine.Catalog
{
  public interface IProductRepository
  {
    List<Product> GetAll();
  }
}