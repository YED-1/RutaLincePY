import flet as ft
from screens.welcome_section.bienvenida_screen import WelcomeScreen


def main(page: ft.Page):
    page.title = "Ruta Lince"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(WelcomeScreen(page))

ft.app(target=main)
