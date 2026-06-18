using PolidramniosMobile.Services;

namespace PolidramniosMobile;

public partial class MainPage : ContentPage
{
    private readonly PrevisioneService _service = new();

    public MainPage()
    {
        InitializeComponent();
    }

    // Ricalcola il BMI ogni volta che cambiano altezza o peso.
    private void OnDatiCambiati(object? sender, TextChangedEventArgs e) => AggiornaBmi();

    private double? AggiornaBmi()
    {
        if (double.TryParse(AltezzaEntry.Text, out var h) && double.TryParse(PesoEntry.Text, out var w)
            && h > 0 && w > 0)
        {
            var bmi = w / Math.Pow(h / 100.0, 2);
            BmiLabel.Text = bmi.ToString("F1");
            return bmi;
        }
        BmiLabel.Text = "—";
        return null;
    }

    private async void OnCalcolaClicked(object? sender, EventArgs e)
    {
        var errori = new List<string>();
        var dati = new Dictionary<string, double>();

        // Legge un campo: obbligatorio, numerico, dentro il range.
        void Leggi(string nome, Entry entry, double min, double max, string etichetta)
        {
            var t = entry.Text?.Trim() ?? "";
            if (t.Length == 0) { errori.Add($"{etichetta}: obbligatorio"); return; }
            if (!double.TryParse(t, out var n)) { errori.Add($"{etichetta}: valore non numerico"); return; }
            if (n < min || n > max) { errori.Add($"{etichetta}: fuori range ({min}–{max})"); return; }
            dati[nome] = n;
        }

        Leggi("Eta_anni", EtaEntry, 14, 55, "Età");
        Leggi("Numero_Gravidanze_Pregresse", GravidanzeEntry, 0, 20, "Gravidanze");
        Leggi("Numero_Tagli_Cesarei_Pregressi", CesareiEntry, 0, 12, "Tagli cesarei");
        Leggi("Pressione_Diastolica_mmHg", PressioneEntry, 40, 130, "Pressione diastolica");
        Leggi("Insulina_Sierica_2ore", InsulinaEntry, 0, 400, "Insulina");

        // Altezza e peso servono solo per il BMI.
        bool altezzaOk = double.TryParse(AltezzaEntry.Text, out var h) && h >= 120 && h <= 220;
        bool pesoOk = double.TryParse(PesoEntry.Text, out var w) && w >= 30 && w <= 250;
        if (!altezzaOk) errori.Add("Altezza: 120–220 cm");
        if (!pesoOk) errori.Add("Peso: 30–250 kg");

        var bmi = AggiornaBmi();
        if (altezzaOk && pesoOk)
        {
            if (bmi is null || bmi < 14 || bmi > 60)
                errori.Add("BMI fuori range (14–60): controlla altezza e peso");
            else
                dati["Indice_Massa_Corporea"] = Math.Round(bmi.Value, 1);
        }

        // Coerenza: i cesarei non possono superare le gravidanze.
        if (dati.TryGetValue("Numero_Tagli_Cesarei_Pregressi", out var ces)
            && dati.TryGetValue("Numero_Gravidanze_Pregresse", out var grav) && ces > grav)
            errori.Add("I tagli cesarei non possono superare le gravidanze pregresse");

        dati["Diabete_Gestazionale"] = DiabeteGestSwitch.IsToggled ? 1 : 0;
        dati["Diabete_Pregravidico"] = DiabetePregSwitch.IsToggled ? 1 : 0;

        if (errori.Count > 0)
        {
            MostraErrore(string.Join("\n• ", errori));
            return;
        }

        CalcolaBtn.IsEnabled = false;
        try
        {
            var r = await _service.PrevediAsync(dati);
            MostraRisultato(r);
        }
        catch (Exception ex)
        {
            MostraErrore($"{ex.Message}\nVerifica che il backend sia attivo (porta 5000).");
        }
        finally
        {
            CalcolaBtn.IsEnabled = true;
        }
    }

    private void MostraErrore(string msg)
    {
        RisultatoFrame.IsVisible = false;
        ErroreLabel.Text = "• " + msg;
        ErroreLabel.IsVisible = true;
    }

    private void MostraRisultato(RisultatoPrevisione r)
    {
        ErroreLabel.IsVisible = false;
        var perc = (int)Math.Round(r.Probabilita * 100);
        bool positivo = r.Previsione == 1;
        EsitoLabel.Text = positivo ? "Rischio di Polidramnios" : "Nessun rischio rilevato";
        EsitoLabel.TextColor = positivo ? Colors.Firebrick : Color.FromArgb("#1c7a86");
        ProbLabel.Text = $"{perc}% di probabilità stimata di Polidramnios";
        RisultatoFrame.IsVisible = true;
    }
}
