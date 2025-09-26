import flet as ft
from widgets.button_welcome_widget import WelcomeButton
from screens.welcome_section.seleccion_campus_screen import SeleccionCampusScreen

class WelcomeScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = self.create_view()

    def create_view(self):
        return ft.View(
            route="/welcome",
            controls=[
                # Scaffold equivalente - Contenedor principal
                ft.Container(
                    content=ft.Column(
                        controls=[
                            #Titulo principal
                            ft.Container(
                                content=ft.Text(
                                    "Bienvenido a Ruta Lince",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                padding=20,
                            ),

                            #Subtitulo
                            ft.Container(
                                content=ft.Text(
                                    "Responde dos preguntas rápidas para comenzar.",

                                    size=16,
                                    color=ft.colors.GREY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                padding=ft.padding.symmetric(horizontal=20),
                            ),
                            #Botón de acción
                            ft.Container(
                                content=WelcomeButton(
                                    label="¡Vamos!",
                                    on_click=self.navigate_to_campus_selection).build(),
                                padding=20,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ]
        )

    def navigate_to_campus_selection(self, e):
        """Navega a la pantalla de selección de campus"""
        campus_screen = SeleccionCampusScreen(self.page)
        self.page.views.append(campus_screen.view)
        self.page.update()
