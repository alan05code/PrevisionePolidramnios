using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace PolidramniosMobile.Services;

/// <summary>Risposta del backend per la previsione.</summary>
public class RisultatoPrevisione
{
    [JsonPropertyName("previsione")] public int Previsione { get; set; }
    [JsonPropertyName("probabilita")] public double Probabilita { get; set; }
    [JsonPropertyName("errore")] public string? Errore { get; set; }
}

/// <summary>Client HTTP verso l'API Flask /previsione.</summary>
public class PrevisioneService
{
    // Su emulatore Android l'host (PC) si raggiunge a 10.0.2.2; altrove a 127.0.0.1.
#if ANDROID
    private const string BaseUrl = "http://10.0.2.2:5000";
#else
    private const string BaseUrl = "http://127.0.0.1:5000";
#endif

    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(15) };

    /// <summary>Invia i dati e restituisce previsione + probabilità. Lancia eccezione su errore.</summary>
    public async Task<RisultatoPrevisione> PrevediAsync(Dictionary<string, double> dati)
    {
        var resp = await _http.PostAsJsonAsync($"{BaseUrl}/previsione", dati);
        var risultato = await resp.Content.ReadFromJsonAsync<RisultatoPrevisione>();
        if (risultato is null)
            throw new Exception("Risposta non valida dal server.");
        if (!resp.IsSuccessStatusCode)
            throw new Exception(risultato.Errore ?? "Errore dal server.");
        return risultato;
    }
}
