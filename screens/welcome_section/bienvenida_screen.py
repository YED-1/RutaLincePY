import flet as ft
from screens.welcome_section.seleccion_campus_screen import SeleccionCampusScreen

class WelcomeScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self.page = page

        titulo = ft.Text(
            "Bienvenido a Ruta Lince",
            size=32,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        subtitulo = ft.Text(
            "Responde dos preguntas rápidas para comenzar.",
            size=16,
            color=ft.Colors.GREY,
            text_align=ft.TextAlign.CENTER,
        )

        boton = ft.ElevatedButton(
            "¡Vamos!",
            on_click=self.ir_a_seleccion_campus
        )

        self.controls = [
            ft.Container(content=titulo, padding=20),
            ft.Container(content=subtitulo, padding=ft.padding.symmetric(horizontal=20)),
            ft.Container(content=boton, padding=20)
        ]

    def ir_a_seleccion_campus(self, e):
        self.page.clean()
        self.page.add(SeleccionCampusScreen(self.page))
