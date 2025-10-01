import flet as ft
from database.database import DatabaseHelper
from widgets.button_campus_widget import CampusButton


# UserControl es el equivalente a un StatefulWidget en Flet.
# Nos permite crear componentes con estado interno y ciclo de vida.
class SeleccionCampusControl(ft.UserControl):
    def __init__(self, on_next):
        super().__init__()
        self.on_next_callback = on_next
        self.db_helper = DatabaseHelper()
        self.campus_list = []
        self.selected_campus_index = None

    # did_mount se llama una vez cuando el control se añade a la página.
    # Es el equivalente a initState en Flutter.
    def did_mount(self):
        self.page.run_task(self._fetch_campus)

    async def _fetch_campus(self):
        # Obtenemos los campus de la BD
        data = self.db_helper.get_all_data('Campus')
        if data:
            self.campus_list = data

        # self.update() es el setState() de Flet.
        # Le dice a Flet que vuelva a dibujar este control.
        self.update()

    def _on_campus_tapped(self, e):
        # e.control.data contiene el índice que le asignamos a cada tarjeta.
        self.selected_campus_index = e.control.data
        self.update()

    # build es el método que dibuja la UI del control.
    def build(self):
        if not self.campus_list:
            # Mostramos un indicador de carga mientras se obtienen los datos.
            return ft.Column(
                [ft.ProgressRing()],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )

        # Creamos la grilla de campus
        campus_grid = ft.GridView(
            expand=1,
            runs_count=2,  # Equivalente a crossAxisCount: 2
            max_extent=250,
            child_aspect_ratio=2.0,
            spacing=10,
            run_spacing=10,
        )

        # Llenamos la grilla con los datos
        for i, campus in enumerate(self.campus_list):
            is_selected = (i == self.selected_campus_index)
            campus_grid.controls.append(
                ft.Container(
                    data=i,  # Guardamos el índice para saber cuál se seleccionó
                    on_click=self._on_campus_tapped,
                    bgcolor=ft.colors.BLUE_900 if is_selected else ft.colors.WHITE,
                    border_radius=ft.border_radius.all(10),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        value=campus['Nombre'],
                        color=ft.colors.WHITE if is_selected else ft.colors.BLACK,
                        size=18,
                    )
                )
            )

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "¿A qué campus perteneces?",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=ft.padding.all(16)
                ),
                campus_grid,
                ft.Container(
                    content=CampusButton(
                        label="Siguiente",
                        on_click=lambda e: self.on_next_callback(self.selected_campus_index, self.campus_list),
                        is_selected=(self.selected_campus_index is not None)
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=20, horizontal=16)
                )
            ]
        )


# --- Función principal de la Vista ---
def SeleccionCampusScreenView(page: ft.Page):
    async def on_next_pressed(selected_index, campus_list):
        if selected_index is None:
            return

        selected_campus = campus_list[selected_index]
        campus_id = selected_campus['ID_Campus']

        # Guardamos el ID del campus en el almacenamiento del cliente
        page.client_storage.set("idCampus", campus_id)

        # Navegamos a la siguiente pantalla usando el enrutamiento
        page.go(f"/seleccion-carrera/{campus_id}")

    campus_control = SeleccionCampusControl(on_next=on_next_pressed)

    return ft.View(
        route="/seleccion-campus",
        appbar=ft.AppBar(
            title=ft.Text("Selecciona tu Campus")
        ),
        controls=[
            campus_control
        ]
    )