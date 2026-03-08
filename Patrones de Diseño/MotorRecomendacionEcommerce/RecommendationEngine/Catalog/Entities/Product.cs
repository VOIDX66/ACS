// RecommendationEngine/Catalog/Entities/Product.cs
namespace RecommendationEngine.Catalog
{
  public class Product
  {
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public bool InStock { get; set; }
  }
}