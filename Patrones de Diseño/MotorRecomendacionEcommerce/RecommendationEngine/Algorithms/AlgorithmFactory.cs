// RecommendationEngine/Algorithms/AlgorithmFactory.cs
using RecommendationEngine.Settings;

namespace RecommendationEngine.Algorithms
{
  public static class AlgorithmFactory
  {
    public static IRecommendationStrategy CreateDefault()
    {
      var config = EngineConfig.Instance;

      return config.DefaultStrategy switch
      {
        "CollaborativeFiltering" => new CollaborativeFiltering(),
        "Content" => new ContentBasedFiltering(),
        // Por defecto, usar Filtrado Colaborativo
        _ => new CollaborativeFiltering()
      };
    }
  }
}