import flet as ft
from widgets.button_campus_widget import CampusButton
from database.database import DatabaseHelper
from screens.inicio_screen import InicioScreen


class DetallesCampusScreen:
    def __init__(self, page: ft.Page, nombre: str, idCampus: str):
        self.page = page
        self.nombre = nombre
        self.idCampus = idCampus
        self.db = DatabaseHelper()
        self.carreras = []
        self.selected_carrera = None
        self.is_loading = True
        self.view = self.create_view()
        self.load_carreras()

    def create_view(self):
        """Crea la vista de selección de carrera"""
        self.title_text = ft.RichText(
            text_span=[
                ft.TextSpan("¿Qué carrera estudias en el campus "),
                ft.TextSpan(
                    self.nombre,
                    style=ft.TextStyle(color=ft.colors.BLUE_900, weight=ft.FontWeight.BOLD)
                ),
                ft.TextSpan("?"),
            ],
            text_align=ft.TextAlign.CENTER,
            size=24,
            weight=ft.FontWeight.BOLD
        )

        self.loading_indicator = ft.ProgressRing()
        self.error_text = ft.Text("Error cargando carreras", color=ft.colors.RED)
        self.empty_text = ft.Text("No hay carreras asociadas a este campus", color=ft.colors.GREY)

        self.carreras_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=150,
            child_aspect_ratio=1.5,
            spacing=10,
            run_spacing=10,
        )

        self.next_button = CampusButton(
            label="Siguiente",
            on_click=self.on_next_pressed,
            is_selected=False
        ).build()

        # Contenedor principal del contenido
        self.content_container = ft.Container(
            content=self.loading_indicator,
            expand=True,
            alignment=ft.alignment.center
        )

        return ft.View(
            route="/carrera",
            controls=[
                ft.AppBar(title=ft.Text("Detalles del Campus")),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=self.title_text,
                            padding=16,
                            alignment=ft.alignment.center
                        ),
                        self.content_container,
                        ft.Container(
                            content=self.next_button,
                            padding=ft.padding.symmetric(vertical=20),
                            alignment=ft.alignment.center
                        )
                    ]),
                    padding=16,
                    expand=True
                )
            ]
        )

    async def load_carreras(self):
        """Carga las carreras del campus desde la base de datos"""
        try:
            self.carreras = await self.db.get_nombres_carrera_por_id_campus(self.idCampus)
            self.is_loading = False
            self.update_content()

        except Exception as e:
            print(f"Error cargando carreras: {e}")
            self.is_loading = False
            self.content_container.content = self.error_text
            self.page.update()

    def update_content(self):
        """Actualiza el contenido basado en el estado de carga"""
        if self.is_loading:
            self.content_container.content = self.loading_indicator
        elif not self.carreras:
            self.content_container.content = ft.Container(
                content=self.empty_text,
                alignment=ft.alignment.center,
                expand=True
            )
        else:
            self.update_carreras_grid()
            self.content_container.content = self.carreras_grid

        self.page.update()

    def update_carreras_grid(self):
        """Actualiza el grid de carreras"""
        self.carreras_grid.controls.clear()

        for carrera in self.carreras:
            card = self.create_carrera_card(carrera)
            self.carreras_grid.controls.append(card)

    def create_carrera_card(self, carrera):
        """Crea una tarjeta de carrera"""
        is_selected = carrera == self.selected_carrera
        bg_color = ft.colors.BLUE_900 if is_selected else ft.colors.WHITE
        text_color = ft.colors.WHITE if is_selected else ft.colors.BLACK

        return ft.Container(
            content=ft.Card(
                elevation=4,
                content=ft.Container(
                    content=ft.Text(
                        carrera,
                        size=18,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                    width=150,
                    height=100,
                ),
                color=bg_color,
            ),
            on_click=lambda e, carr=carrera: self.on_carrera_selected(carr)
        )

    def on_carrera_selected(self, carrera):
        """Maneja la selección de una carrera"""
        self.selected_carrera = carrera

        # Actualizar botón
        self.next_button = CampusButton(
            label="Siguiente",
            on_click=self.on_next_pressed,
            is_selected=True
        ).build()

        # Actualizar todas las tarjetas
        self.update_carreras_grid()
        self.page.update()

    async def on_next_pressed(self, e):
        """Maneja el clic en el botón Siguiente"""
        if self.selected_carrera is None:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor selecciona una carrera antes de continuar."))
            )
            return

        try:
            # Obtener el ID real de la carrera seleccionada
            id_carrera = await self.db.get_id_carrera_by_nombre(self.selected_carrera)

            # Guardar en almacenamiento local (equivalente a SharedPreferences)
            self.page.client_storage.set("idCarrera", id_carrera)
            self.page.client_storage.set("carreraNombre", self.selected_carrera)
            self.page.client_storage.set("idCampus", self.idCampus)
            self.page.client_storage.set("campusNombre", self.nombre)

            # Guardar también en la base de datos (usuario)
            await self.db.insert_or_update_usuario(
                id_usuario="usuario_actual",  # Puedes cambiar esto por un ID real
                id_campus=self.idCampus,
                id_carrera=id_carrera
            )

            # Navegar a la pantalla de inicio (equivalente a pushReplacement)


            inicio_screen = InicioScreen(
                self.page,
                idCarrera=id_carrera,
                idCampus=self.idCampus
            )

            # Limpiar el stack de vistas y agregar la nueva (pushReplacement)
            self.page.views.clear()
            self.page.views.append(inicio_screen.view)
            self.page.update()

        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error: {str(e)}"))
            )