import flet as ft
# 1. Importas la pantalla real de Ajustes
from src.screens.ajustes_screen import AjustesScreen

# --- Pantallas Temporales (para que la navegación funcione) ---
# (Mantenemos estas hasta que construyas las pantallas reales)
class JuegosScreen(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__()
        self.controls = [ft.Text("Pantalla de Juegos", size=30)]

class SimuladorScreen(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__()
        self.controls = [ft.Text("Pantalla de Simulador", size=30)]

# 2. BORRAMOS la clase temporal "AjustesScreen" de aquí porque ya la importamos

# --- Fin de Pantallas Temporales ---

def create_nav_bar(page: ft.Page, selected_index: int, id_carrera: str, id_campus: str, id_usuario: str):
    def on_navigation_change(e):
        from src.screens.inicio_screen import InicioScreen
        index = int(e.data)

        page.clean()
        page.appbar = None

        if index == 0:
            page.add(InicioScreen(page, id_carrera=id_carrera, id_campus=id_campus))
        elif index == 1:
            page.add(JuegosScreen(page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))
        elif index == 2:
            page.add(SimuladorScreen(page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))
        elif index == 3:
            # 3. Esta llamada ahora usará la pantalla real importada
            page.add(AjustesScreen(page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))

        page.update()

    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_navigation_change,
        bgcolor=ft.Colors.BLACK,
        indicator_color=ft.Colors.BLUE_GREY_400,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_ESPORTS, label="Juegos"),
            ft.NavigationBarDestination(icon=ft.Icons.INSERT_DRIVE_FILE, label="Simulador"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
        ]
    )