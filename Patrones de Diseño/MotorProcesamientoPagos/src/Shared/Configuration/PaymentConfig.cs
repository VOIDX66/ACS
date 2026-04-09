namespace Configuration
{
  public sealed class PaymentConfig
  {
    private static readonly Lazy<PaymentConfig> _instance =
        new Lazy<PaymentConfig>(() => new PaymentConfig());

    public static PaymentConfig Instance => _instance.Value;

    public string DefaultCurrency { get; } = "USD";
    public decimal BaseExchangeRate { get; set; } = 1.0m;
    public decimal GlobalSecurityThreshold { get; set; } = 10000.0m;
    public List<string> HighRiskCountries { get; private set; }

    private PaymentConfig()
    {
      HighRiskCountries = new List<string> { "NorthKorea", "UnknownRegion" };
      Console.WriteLine("[Singleton] Configuración de Pagos Inicializada.");
    }

    public bool IsCountryRestricted(string country) => HighRiskCountries.Contains(country);
  }
}