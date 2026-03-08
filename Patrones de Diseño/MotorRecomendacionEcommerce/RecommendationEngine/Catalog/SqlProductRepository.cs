// RecommendationEngine/Catalog/SqlProductRepository.cs
namespace RecommendationEngine.Catalog
{
  public class SqlProductRepository : IProductRepository
  {
    public List<Product> GetAll()
    {
      // Lógica para obtener la lista de productos desde la base de datos
      return new List<Product>
      {
        new Product { Id = 1, Name = "Teclado Mecánico RGB", InStock = true },
        new Product { Id = 2, Name = "Monitor 144Hz", InStock = true },
        new Product { Id = 3, Name = "Mouse Pad Extendido", InStock = false }
      };
    }
  }
}