import flet as ft
from database.database import DatabaseHelper
from widgets.button_campus_widget import CampusButton


class SeleccionCarreraControl(ft.UserControl):
    def __init__(self, campus_id: str, on_next):
        super().__init__()
        self.on_next_callback = on_next
        self.campus_id = campus_id
        self.db_helper = DatabaseHelper()

        # Estado del control
        self.campus_name = ""
        self.carreras_list = []
        self.selected_carrera_name = None
        self.loading = True
        self.error_message = None

    def did_mount(self):
        self.page.run_task(self._fetch_data)

    async def _fetch_data(self):
        """
        Carga tanto el nombre del campus como la lista de carreras.
        Esto reemplaza la lógica del FutureBuilder.
        """
        try:
            campus_data = self.db_helper.get_campus_by_id(self.campus_id)
            self.campus_name = campus_data['Nombre'] if campus_data else "Desconocido"

            carrera_names = self.db_helper.get_nombres_carrera_por_id_campus(self.campus_id)
            self.carreras_list = carrera_names

        except Exception as e:
            self.error_message = f"Error al cargar datos: {e}"

        self.loading = False
        self.update()  # Redibuja el control con los datos o el error.

    def _on_carrera_tapped(self, e):
        self.selected_carrera_name = e.control.data
        self.update()

    def build(self):
        if self.loading:
            return ft.Column([ft.ProgressRing()], alignment="center", horizontal_alignment="center", expand=True)

        if self.error_message:
            return ft.Column([ft.Text(self.error_message)], alignment="center", horizontal_alignment="center",
                             expand=True)

        if not self.carreras_list:
            return ft.Column([ft.Text("No hay carreras asociadas a este campus.")], alignment="center",
                             horizontal_alignment="center", expand=True)

        # Recreamos el RichText de Flutter usando Text con TextSpans
        title = ft.Text(
            text_align=ft.TextAlign.CENTER,
            spans=[
                ft.TextSpan("¿Qué carrera estudias en el campus "),
                ft.TextSpan(
                    self.campus_name,
                    ft.TextStyle(color=ft.colors.BLUE_900, weight=ft.FontWeight.BOLD)
                ),
                ft.TextSpan("?"),
            ],
            size=24,
            weight=ft.FontWeight.BOLD,
        )

        # Creamos la grilla de carreras
        carreras_grid = ft.GridView(
            expand=1, runs_count=2, max_extent=250, child_aspect_ratio=2.0, spacing=10, run_spacing=10
        )
        for nombre in self.carreras_list:
            is_selected = (nombre == self.selected_carrera_name)
            carreras_grid.controls.append(
                ft.Container(
                    data=nombre,
                    on_click=self._on_carrera_tapped,
                    bgcolor=ft.colors.BLUE_900 if is_selected else ft.colors.WHITE,
                    border_radius=ft.border_radius.all(10),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(8),
                    content=ft.Text(
                        value=nombre,
                        color=ft.colors.WHITE if is_selected else ft.colors.BLACK,
                        size=18,
                        text_align=ft.TextAlign.CENTER,
                    )
                )
            )

        return ft.Column(
            controls=[
                ft.Container(content=title, padding=16),
                carreras_grid,
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=20),
                    content=CampusButton(
                        label="Siguiente",
                        on_click=lambda e: self.on_next_callback(self.selected_carrera_name),
                        is_selected=(self.selected_carrera_name is not None),
                    ),
                ),
            ]
        )


# --- Función principal de la Vista ---
def SeleccionCarreraScreenView(page: ft.Page):
    db_helper = DatabaseHelper()
    campus_id = page.route.split("/")[-1]

    async def on_next_pressed(selected_carrera):
        if selected_carrera is None:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor selecciona una carrera."))
            page.snack_bar.open = True
            page.update()
            return

        # Obtenemos el ID de la carrera a partir de su nombre
        id_carrera = db_helper.get_id_carrera_by_nombre(selected_carrera)
        page.client_storage.set("idCarrera", id_carrera)

        # Navegamos a la pantalla de inicio, reemplazando la vista actual
        page.go(f"/inicio/{campus_id}/{id_carrera}")

    carrera_control = SeleccionCarreraControl(campus_id=campus_id, on_next=on_next_pressed)

    return ft.View(
        route=page.route,
        appbar=ft.AppBar(title=ft.Text("Selecciona tu Carrera")),
        controls=[carrera_control]
    )