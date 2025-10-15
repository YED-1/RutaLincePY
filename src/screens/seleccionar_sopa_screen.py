import flet as ft
from database.database import DatabaseHelper
from src.screens.sopa_de_letras_screen import SopaDeLetrasScreen


class SeleccionarSopaScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str):
        super().__init__(expand=True)
        self.page = page
        self.id_carrera = id_carrera
        self.db_helper = DatabaseHelper()

        # Contenedor para manejar el estado de carga (como un FutureBuilder)
        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando sopas de letras...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.content_area = ft.Container(content=self.loading_view, expand=True)

        self.controls = [self.content_area]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Seleccionar Sopa de Letras"))
        self.page.update()
        self._fetch_data()

    def _fetch_data(self):
        sopas = self.db_helper.get_sopas_con_area_by_id_carrera(self.id_carrera)

        if not sopas:
            self.content_area.content = ft.Text("No hay sopas de letras disponibles para esta carrera.",
                                                text_align=ft.TextAlign.CENTER)
        else:
            list_view = ft.ListView(expand=True, spacing=10, padding=16)
            for s in sopas:
                list_view.controls.append(self.create_card(s))
            self.content_area.content = list_view

        self.update()

    def create_card(self, sopa: dict):
        return ft.Card(
            # Guardamos los datos que necesitamos en el evento click
            data={'id': sopa['ID_Sopa'], 'nombre': sopa['NombreArea']},
            on_click=self._on_card_click,
            elevation=6,
            content=ft.Container(
                padding=16,
                border_radius=12,
                border=ft.border.all(2, ft.Colors.BLUE_900),
                content=ft.Column(
                    cross_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            f"{sopa['NombreArea']} - {sopa['ID_Area']}",
                            size=23,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900
                        ),
                        ft.Divider(height=4, color=ft.Colors.TEAL_100, thickness=2),
                        ft.Text(
                            f"Sopa: {sopa['ID_Sopa']}",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(f"Palabras: {sopa['Cantidad_Palabras']}", size=16),
                    ]
                )
            )
        )

    def _on_card_click(self, e):
        id_sopa = e.control.data['id']
        nombre_area = e.control.data['nombre']
        self.page.clean()
        self.page.add(SopaDeLetrasScreen(self.page, id_sopa=id_sopa, nombre_area=nombre_area))