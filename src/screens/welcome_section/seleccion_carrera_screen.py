import flet as ft
from src.database.database import DatabaseHelper
from src.screens.inicio_screen import InicioScreen


class SeleccionCarreraScreen(ft.Column):
    def __init__(self, page: ft.Page, id_campus: str, campus_nombre: str):
        super().__init__(expand=True)
        self.page = page
        self.id_campus = id_campus
        self.campus_nombre = campus_nombre

        self.db_helper = DatabaseHelper()
        self.selected_carrera_nombre = None

        # --- Controles de la UI ---
        self.title = ft.Text(
            spans=[
                ft.TextSpan("¿Qué carrera estudias en el campus "),
                ft.TextSpan(
                    self.campus_nombre,
                    ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ),
                ft.TextSpan("?"),
            ],
            size=24,
            text_align=ft.TextAlign.CENTER,
        )

        self.carreras_grid = ft.GridView(
            expand=True, runs_count=2, spacing=10, run_spacing=10, child_aspect_ratio=2.0
        )
        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando carreras...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.content_area = ft.Container(content=self.loading_view, expand=True)

        self.next_button = ft.ElevatedButton(
            text="Siguiente", disabled=True, on_click=self._on_next_pressed
        )

        # Estructura principal
        self.controls = [
            ft.Container(content=self.title, padding=16),
            self.content_area,
            ft.Container(
                content=self.next_button,
                padding=ft.padding.symmetric(horizontal=16, vertical=20),
                alignment=ft.alignment.center,
            ),
        ]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Selecciona tu Carrera"), bgcolor=ft.Colors.GREY_200)
        self._fetch_carreras()
        self.page.update()

    def _fetch_carreras(self):
        carreras_list = self.db_helper.get_nombres_carrera_por_id_campus(self.id_campus)

        if not carreras_list:
            self.content_area.content = ft.Text("No se encontraron carreras para este campus.",
                                                text_align=ft.TextAlign.CENTER)
        else:
            self.carreras_grid.controls.clear()
            for nombre in carreras_list:
                self.carreras_grid.controls.append(self.create_carrera_card(nombre))
            self.content_area.content = self.carreras_grid

        self.update()

    def create_carrera_card(self, nombre_carrera: str):
        return ft.GestureDetector(
            on_tap=lambda e: self._on_carrera_selected(nombre_carrera),
            content=ft.Card(
                data=nombre_carrera,
                content=ft.Container(
                    content=ft.Text(nombre_carrera, size=16, text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                    padding=8,
                ),
            ),
        )

    def _on_carrera_selected(self, nombre_carrera: str):
        self.selected_carrera_nombre = nombre_carrera
        for card_detector in self.carreras_grid.controls:
            card = card_detector.content
            is_selected = card.data == nombre_carrera
            card.color = ft.Colors.BLUE_900 if is_selected else ft.Colors.WHITE
            text_widget = card.content.content  # Asumiendo que content es Container(content=Text)
            text_widget.color = ft.Colors.WHITE if is_selected else ft.Colors.BLACK
        self.next_button.disabled = False
        self.update()

    def _on_next_pressed(self, e):
        if self.selected_carrera_nombre:
            # Obtenemos el ID de la carrera desde la BD
            id_carrera = self.db_helper.get_id_carrera_by_nombre(self.selected_carrera_nombre)

            # --- AÑADIDA LÍNEA PARA DEPURAR ---
            print(
                f"\n--- DEBUG (Carrera): Obtenido id_carrera='{id_carrera}' para el nombre '{self.selected_carrera_nombre}' ---")
            # --- FIN DE LA LÍNEA DE DEPURACIÓN ---

            # Verificamos si el ID es válido antes de continuar
            if not id_carrera:
                print(
                    f"--- DEBUG ERROR (Carrera): No se encontró ID para la carrera '{self.selected_carrera_nombre}' ---")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error: No se pudo encontrar el ID para {self.selected_carrera_nombre}"))
                self.page.snack_bar.open = True
                self.page.update()
                return  # Detenemos la navegación

            # Guarda el ID en el almacenamiento del cliente
            self.page.client_storage.set("idCarrera", id_carrera)
            print(f"ID de Carrera guardado: {id_carrera}")

            # Navegamos a la pantalla de inicio
            self.page.appbar = None
            self.page.clean()
            self.page.add(InicioScreen(self.page, id_campus=self.id_campus, id_carrera=id_carrera))
            self.page.update()
        else:
            print("--- DEBUG WARNING (Carrera): Se presionó Siguiente sin seleccionar carrera ---")