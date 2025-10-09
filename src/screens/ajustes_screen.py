import flet as ft
from database.database import DatabaseHelper
from src.widgets.nav_bar_widget import create_nav_bar
# Importamos las pantallas a las que vamos a navegar
from src.screens.welcome_section.seleccion_campus_screen import SeleccionCampusScreen
from src.screens.welcome_section.seleccion_carrera_screen import SeleccionCarreraScreen
from src.screens.creditos_screen import CreditosScreen


class AjustesScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str, id_usuario: str):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.page = page
        self.id_carrera = id_carrera
        self.id_campus = id_campus
        self.id_usuario = id_usuario

        self.db_helper = DatabaseHelper()
        self.nombre_campus = ""
        self.nombre_carrera = ""

        # Título dinámico para la AppBar
        self.appbar_title = ft.Text("Cargando...", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD)

        # --- Botones de Opciones ---
        self.controls = [
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.SCHOOL), ft.Text("Cambiar carrera")]),
                on_click=self._cambiar_carrera,
                width=250
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.BOOK), ft.Text("Cambiar campus")]),
                on_click=self._cambiar_campus,
                width=250
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.GROUP), ft.Text("Créditos del proyecto")]),
                on_click=self._ver_creditos,
                width=250
            ),
        ]

    def did_mount(self):
        # Creamos una AppBar personalizada
        self.page.appbar = ft.AppBar(
            automatically_imply_leading=False,
            title=ft.Container(
                content=self.appbar_title,
                bgcolor=ft.Colors.BLACK,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=8
            ),
            center_title=True
        )
        self.page.navigation_bar = create_nav_bar(
            page=self.page, selected_index=3, id_carrera=self.id_carrera, id_campus=self.id_campus,
            id_usuario=self.id_usuario
        )
        self._cargar_datos()
        self.page.update()

    def _cargar_datos(self):
        campus = self.db_helper.get_campus_by_id(self.id_campus)
        carrera = self.db_helper.get_carrera_by_id(self.id_carrera)
        if campus and carrera:
            self.nombre_campus = campus['Nombre']
            self.nombre_carrera = carrera['Nombre']
            # Actualizamos el texto del título en la AppBar
            self.appbar_title.value = f"{self.nombre_campus} - {self.nombre_carrera}"
            self.update()  # Actualizamos la pantalla para que se vea el cambio

    def _cambiar_carrera(self, e):
        self.page.client_storage.remove("idCarrera")
        self.page.clean()
        self.page.appbar = None
        self.page.navigation_bar = None
        self.page.add(SeleccionCarreraScreen(
            self.page, id_campus=self.id_campus, campus_nombre=self.nombre_campus
        ))

    def _cambiar_campus(self, e):
        self.page.client_storage.remove("idCarrera")
        self.page.client_storage.remove("idCampus")
        self.page.clean()
        self.page.appbar = None
        self.page.navigation_bar = None
        self.page.add(SeleccionCampusScreen(self.page))

    def _ver_creditos(self, e):
        self.page.clean()
        self.page.add(CreditosScreen(self.page))