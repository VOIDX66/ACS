// RecommendEngine/ExternalServices/Interfaces/IExternalPredictor.cs
namespace RecommendationEngine.ExternalServices
{
  public interface IExternalPredictor
  {
    string[] GetExternalPredictions(int userId);
  }
}