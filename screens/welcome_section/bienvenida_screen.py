import flet as ft
from widgets.button_welcome_widget import WelcomeButton
from screens.seleccion_campus_screen import SeleccionCampusScreen

class WelcomeScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = self.create_view()

    def create_view(self):
        return ft.View(
            route="/welcome",
            controls=[
            ]
        )