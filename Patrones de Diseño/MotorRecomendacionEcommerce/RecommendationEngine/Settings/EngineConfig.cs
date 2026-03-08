// RecommendationEngine/Settings/EngineConfig.cs
namespace RecommendationEngine.Settings
{
  public sealed class EngineConfig
  {
    private static readonly Lazy<EngineConfig> _instance = new(() => new EngineConfig());

    public static EngineConfig Instance => _instance.Value;

    // Parametros de configuración
    public string DefaultStrategy { get; set; } = "CollaborativeFiltering";
    public double SimilarityThreshold { get; set; } = 0.75;
    public int CacheExpirationInMinutes { get; set; } = 30;

    private EngineConfig() { }
  }
}