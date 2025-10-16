import flet as ft
# 1. IMPORTAMOS LA PANTALLA A LA QUE VAMOS A NAVEGAR
from src.screens.welcome_section.seleccion_carrera_screen import SeleccionCarreraScreen
# 2. IMPORTAMOS NUESTRA CLASE DE BASE DE DATOS
from src.database.database import DatabaseHelper


class SeleccionCampusScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page

        # 3. CREAMOS UNA INSTANCIA DEL DATABASE HELPER
        self.db_helper = DatabaseHelper()
        self.campus_list = []
        self.selected_campus_id = None

        self.title = ft.Text(
            "¿A qué campus perteneces?", size=24, weight=ft.FontWeight.BOLD
        )
        self.campus_grid = ft.GridView(
            expand=True, runs_count=2, child_aspect_ratio=2.0, spacing=10, run_spacing=10
        )
        self.next_button = ft.ElevatedButton(
            text="Siguiente", disabled=True, on_click=self._on_next_pressed
        )

        self.controls = [
            ft.Container(content=self.title, padding=16),
            self.campus_grid,
            ft.Container(
                content=self.next_button,
                padding=ft.padding.symmetric(horizontal=16, vertical=20),
                alignment=ft.alignment.center,
            ),
        ]

    def did_mount(self):
        self.page.appbar = ft.AppBar(
            title=ft.Text("Selecciona tu Campus"), bgcolor=ft.Colors.GREY_200
        )
        self._fetch_campus()
        self.page.update()

    def _fetch_campus(self):
        # 4. OBTENEMOS LOS DATOS DESDE LA BASE DE DATOS REAL
        self.campus_list = self.db_helper.get_campus()

        self.campus_grid.controls.clear()
        for campus in self.campus_list:
            card = self.create_campus_card(campus)
            self.campus_grid.controls.append(card)

    def create_campus_card(self, campus):
        # Usamos los nombres de columna de la base de datos
        campus_id = campus['ID_Campus']
        campus_nombre = campus['Nombre']

        return ft.GestureDetector(
            on_tap=lambda e: self._on_campus_selected(campus_id),
            content=ft.Card(
                data=campus_id,
                content=ft.Container(
                    content=ft.Text(campus_nombre, size=18),
                    alignment=ft.alignment.center,
                    padding=10,
                ),
            ),
        )

    def _on_campus_selected(self, campus_id):
        self.selected_campus_id = campus_id
        for card_detector in self.campus_grid.controls:
            card = card_detector.content
            is_selected = card.data == campus_id
            card.color = ft.Colors.BLUE_900 if is_selected else ft.Colors.WHITE
            text_widget = card.content.content
            text_widget.color = ft.Colors.WHITE if is_selected else ft.Colors.BLACK
        self.next_button.disabled = False
        self.update()

    def _on_next_pressed(self, e):
        if self.selected_campus_id:
            campus_nombre_seleccionado = ""
            for campus in self.campus_list:
                if campus['ID_Campus'] == self.selected_campus_id:
                    campus_nombre_seleccionado = campus['Nombre']
                    break

            self.page.appbar = None
            self.page.clean()

            self.page.add(SeleccionCarreraScreen(
                self.page,
                id_campus=self.selected_campus_id,
                campus_nombre=campus_nombre_seleccionado
            ))
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor selecciona un campus.")
            )
            self.page.snack_bar.open = True
            self.page.update()