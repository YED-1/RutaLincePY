import flet as ft
from widgets.button_campus_widget import CampusButton
from database.database import DatabaseHelper
from screens.welcome_section.seleccion_carrera_screen import DetallesCampusScreen


class SeleccionCampusScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseHelper()
        self.campus = []
        self.selected_campus_index = None
        self.view = self.create_view()
        self.load_campus()

    def create_view(self):
        """Crea la vista de selección de campus"""
        self.title_text = ft.Text(
            "¿A qué campus perteneces?",
            size=24,
            weight=ft.FontWeight.BOLD,
        )

        self.loading_indicator = ft.ProgressRing()
        self.campus_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=2.0,
            spacing=10,
            run_spacing=10,
        )

        self.next_button = CampusButton(
            label="Siguiente",
            on_click=self.on_next_pressed,
            is_selected=False
        ).build()

        return ft.View(
            route="/campus",
            controls=[
                ft.AppBar(title=ft.Text("Selecciona tu Campus")),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=self.title_text,
                            padding=16
                        ),
                        ft.Container(
                            content=self.loading_indicator,
                            expand=True,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            content=self.next_button,
                            padding=ft.padding.symmetric(horizontal=16, vertical=20),
                            alignment=ft.alignment.center
                        )
                    ]),
                    expand=True
                )
            ]
        )

    async def load_campus(self):
        """Carga la lista de campus desde la base de datos"""
        try:
            self.campus = await self.db.get_campus()
            self.update_campus_grid()
        except Exception as e:
            print(f"Error cargando campus: {e}")
            error_text = ft.Text("Error cargando campus", color=ft.colors.RED)
            self.page.controls[0].controls[1].content = error_text
        self.page.update()

    def update_campus_grid(self):
        """Actualiza el grid de campus con los datos cargados"""
        self.campus_grid.controls.clear()

        for i, campus in enumerate(self.campus):
            card = self.create_campus_card(campus, i)
            self.campus_grid.controls.append(card)

        self.page.controls[0].controls[1].content = self.campus_grid
        self.page.update()

    def create_campus_card(self, campus, index):
        """Crea una tarjeta de campus"""
        is_selected = index == self.selected_campus_index
        bg_color = ft.colors.BLUE_900 if is_selected else ft.colors.WHITE
        text_color = ft.colors.WHITE if is_selected else ft.colors.BLACK

        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Text(
                        campus["Nombre"],
                        size=18,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                ),
                color=bg_color,
            ),
            on_click=lambda e, idx=index: self.on_campus_selected(idx)
        )

    def on_campus_selected(self, index):
        """Maneja la selección de un campus"""
        self.selected_campus_index = index

        # Actualizar estado del botón
        self.next_button = CampusButton(
            label="Siguiente",
            on_click=self.on_next_pressed,
            is_selected=True
        ).build()

        # Actualizar vista
        self.update_campus_grid()

    async def on_next_pressed(self, e):
        """Maneja el clic en el botón Siguiente"""
        if self.selected_campus_index is None:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor selecciona un campus antes de continuar."))
            )
            return

        # Guardar selección en almacenamiento local
        selected_campus = self.campus[self.selected_campus_index]
        self.page.client_storage.set("idCampus", selected_campus["ID_Campus"])
        self.page.client_storage.set("campusNombre", selected_campus["Nombre"])

        # Navegar a la pantalla de selección de carrera (IMPORTACIÓN DIRECTA)
        carrera_screen = DetallesCampusScreen(  # ← SIN importación dentro del método
            self.page,
            nombre=selected_campus["Nombre"],
            idCampus=selected_campus["ID_Campus"]
        )

        self.page.views.append(carrera_screen.view)
        self.page.update()