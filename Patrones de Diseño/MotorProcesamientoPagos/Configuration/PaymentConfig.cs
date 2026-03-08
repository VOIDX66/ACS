// Configuration/PaymentConfig.cs
namespace Configuration
{
  public sealed class PaymentConfig
  {
    // Instancia única y perezosa (Lazy) para seguridad en hilos
    private static readonly Lazy<PaymentConfig> _instance =
        new Lazy<PaymentConfig>(() => new PaymentConfig());

    public static PaymentConfig Instance => _instance.Value;

    // Propiedades globales según el enunciado
    public string DefaultCurrency { get; } = "USD";
    public decimal BaseExchangeRate { get; set; } = 1.0m;
    public decimal GlobalSecurityThreshold { get; set; } = 10000.0m;
    public List<string> HighRiskCountries { get; private set; }

    private PaymentConfig()
    {
      // En un escenario real, esto vendría de una DB o archivo .env
      HighRiskCountries = new List<string> { "NorthKorea", "UnknownRegion" };
      Console.WriteLine("[Singleton] Configuración de Pagos Inicializada.");
    }

    // Método de utilidad para el motor
    public bool IsCountryRestricted(string country) => HighRiskCountries.Contains(country);
  }
}

