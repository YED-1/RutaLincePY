import flet as ft

# --- Importamos las pantallas a las que vamos a navegar ---



# ... (cuando existan, importarán las otras pantallas aquí)

# --- Pantallas Temporales (para que la navegación funcione) ---


class JuegosScreen(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__()
        self.controls = [ft.Text("Pantalla de Juegos", size=30)]


class SimuladorScreen(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__()
        self.controls = [ft.Text("Pantalla de Simulador", size=30)]


class AjustesScreen(ft.Column):
    def __init__(self, page: ft.Page, **kwargs):
        super().__init__()
        self.controls = [ft.Text("Pantalla de Ajustes", size=30)]


# --- Fin de Pantallas Temporales ---


def create_nav_bar(page: ft.Page, selected_index: int, id_carrera: str, id_campus: str, id_usuario: str):
    def on_navigation_change(e):
        from src.screens.inicio_screen import InicioScreen
        # El índice seleccionado viene como un string, lo convertimos a entero
        index = int(e.data)

        # Limpiamos la página y la barra de app antes de cargar la nueva vista
        page.clean()
        page.appbar = None

        # Navegación basada en el índice (equivalente al switch de Dart)
        if index == 0:
            page.add(InicioScreen(page, id_carrera=id_carrera, id_campus=id_campus))
        elif index == 1:
            page.add(JuegosScreen(page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))
        elif index == 2:
            page.add(SimuladorScreen(page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))
        elif index == 3:
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