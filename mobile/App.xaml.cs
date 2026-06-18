using Microsoft.Extensions.DependencyInjection;

namespace PolidramniosMobile;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();
		// Forza il tema chiaro: l'app è pensata su sfondo chiaro, evita il dark mode di sistema.
		UserAppTheme = AppTheme.Light;
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		return new Window(new AppShell());
	}
}