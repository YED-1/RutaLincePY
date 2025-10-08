import flet as ft
import time


# --- Simulación de tu clase DatabaseHelper ---
# Reemplaza esto con la importación de tu propia clase de base de datos
class DatabaseHelper:
    def get_nombres_carrera_por_id_campus(self, id_campus):
        print(f"Buscando carreras para el campus: {id_campus}")
        time.sleep(1)  # Simula una pequeña demora de la red o base de datos
        if id_campus == "C1":
            return ["Ingeniería de Software", "Diseño Gráfico", "Administración", "Gastronomía"]
        elif id_campus == "C2":
            return ["Medicina", "Enfermería", "Derecho"]
        else:
            return []

    def get_id_carrera_by_nombre(self, nombre_carrera):
        ids = {
            "Ingeniería de Software": "ISC-01",
            "Diseño Gráfico": "DG-01",
            "Administración": "ADM-01",
            "Gastronomía": "GAST-01",
            "Medicina": "MED-01",
            "Enfermería": "ENF-01",
            "Derecho": "DER-01",
        }
        return ids.get(nombre_carrera, "ID-GENERICO")


# --- Fin de la simulación ---


class SeleccionCarreraScreen(ft.Column):
    def __init__(self, page: ft.Page, id_campus: str, campus_nombre: str):
        super().__init__(expand=True)
        self.page = page
        self.id_campus = id_campus
        self.campus_nombre = campus_nombre

        self.db_helper = DatabaseHelper()
        self.selected_carrera_nombre = None

        # --- Controles de la UI ---
        # Equivalente a RichText con TextSpan
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

        # Contenedor para manejar el estado de carga (como un FutureBuilder)
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

        # Estructura principal de la pantalla
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
            text_widget = card.content.content
            text_widget.color = ft.Colors.WHITE if is_selected else ft.Colors.BLACK
        self.next_button.disabled = False
        self.update()

    def _on_next_pressed(self, e):
        if self.selected_carrera_nombre:
            id_carrera = self.db_helper.get_id_carrera_by_nombre(self.selected_carrera_nombre)

            # Guardamos en el almacenamiento del cliente (equivalente a SharedPreferences)
            self.page.client_storage.set("idCarrera", id_carrera)
            print(f"ID de Carrera guardado: {id_carrera}")

            # Navegamos a la pantalla de inicio
            self.page.appbar = None
            self.page.clean()
            # self.page.add(InicioScreen(self.page, self.id_campus, id_carrera))
            self.page.update()