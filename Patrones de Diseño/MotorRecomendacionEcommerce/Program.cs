using RecommendationEngine;
using RecommendationEngine.Catalog;
using RecommendationEngine.Settings;

namespace Program
{
  public class Program
  {
    static void Main(string[] args)
    {
      // 1. Configuración Global (Singleton)
      var config = EngineConfig.Instance;
      config.DefaultStrategy = "Content"; // O "Collaborative"

      // 2. Inicialización del Repositorio y la Facade
      var repo = new SqlProductRepository();
      var facade = new RecommendationFacade(repo);

      Console.WriteLine("--- Iniciando Motor de Recomendaciones ---");

      // Primera llamada: Debería ejecutar el algoritmo y loguear el tiempo
      var recs1 = facade.GetRecommendations(userId: 101);
      PrintRecs(recs1);

      Console.WriteLine("\n--- Segunda llamada (Mismo usuario) ---");

      // Segunda llamada: Debería entrar el CACHE y ser casi instantáneo (0ms)
      var recs2 = facade.GetRecommendations(userId: 101);
      PrintRecs(recs2);

      void PrintRecs(List<Product> products)
      {
        foreach (var p in products)
        {
          Console.WriteLine($"- [ID: {p.Id}] {p.Name} ({p.Category})");
        }
      }
    }
  }
}