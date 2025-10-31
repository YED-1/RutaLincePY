import flet as ft
from src.screens.juegos_screen import JuegosScreen
from src.screens.simulador_screen import SimuladorScreen
from src.screens.ajustes_screen import AjustesScreen


def create_nav_bar(page: ft.Page, selected_index: int, id_carrera: str, id_campus: str, id_usuario: str):
    def on_navigation_change(e):
        # Importamos InicioScreen aquí para evitar importaciones circulares
        from src.screens.inicio_screen import InicioScreen

        index = int(e.data)

        # Evita recargar la página si ya estamos en ella
        if index == selected_index:
            return

        # --- INICIO DE LA CORRECCIÓN ---
        # page.clean() # <-- ESTO ROMPE LA APP
        page.controls.clear()  # <-- Esta es la forma segura
        # --- FIN DE LA CORRECCIÓN ---

        page.appbar = None

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