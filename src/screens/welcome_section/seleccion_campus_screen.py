import flet as ft
# CORRECCIÓN: Ajustamos al nombre real del archivo
from src.database.database import DatabaseHelper
from src.screens.welcome_section.seleccion_carrera_screen import SeleccionCarreraScreen


class SeleccionCampusScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page

        # Instanciamos el helper que ahora conecta a Firebase
        self.db_helper = DatabaseHelper()
        self.campus_list = []
        self.selected_campus_id = None

        self.title = ft.Text(
            "¿A qué campus perteneces?", size=24, weight=ft.FontWeight.BOLD
        )
        # runs_count=2 significa 2 columnas en la cuadrícula
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
        # did_mount es el lugar ideal para cargar datos al iniciar la pantalla
        self.page.appbar = ft.AppBar(
            title=ft.Text("Selecciona tu Campus"), bgcolor=ft.Colors.GREY_200
        )
        self._fetch_campus()
        self.page.update()

    def _fetch_campus(self):
        # Obtenemos la lista de diccionarios desde Firestore
        self.campus_list = self.db_helper.get_campus()

        self.campus_grid.controls.clear()

        # Verificamos si la lista vino vacía (útil para depurar)
        if not self.campus_list:
            print("ADVERTENCIA: No se encontraron campus en Firebase.")
            self.campus_grid.controls.append(ft.Text("No hay campus disponibles"))

        for campus in self.campus_list:
            card = self.create_campus_card(campus)
            self.campus_grid.controls.append(card)

        self.update()

    def create_campus_card(self, campus):
        # Accedemos a las claves que definimos en el DatabaseHelper
        campus_id = campus.get('ID_Campus')
        # .get(..., "Texto default") evita errores si el campo falta en la BD
        campus_nombre = campus.get('Nombre', "Campus Sin Nombre")

        return ft.GestureDetector(
            on_tap=lambda e: self._on_campus_selected(campus_id),
            content=ft.Card(
                data=campus_id,  # Guardamos el ID en la data de la tarjeta para identificarla
                content=ft.Container(
                    content=ft.Text(campus_nombre, size=18, text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                    padding=10,
                ),
            ),
        )

    def _on_campus_selected(self, campus_id):
        self.selected_campus_id = campus_id
        # Recorremos la grilla para pintar de azul la seleccionada y blanco las demás
        for card_detector in self.campus_grid.controls:
            # card_detector es el GestureDetector, su contenido es la Card
            card = card_detector.content
            is_selected = card.data == campus_id

            # Cambio visual
            card.color = ft.Colors.BLUE_900 if is_selected else ft.Colors.WHITE
            text_widget = card.content.content
            text_widget.color = ft.Colors.WHITE if is_selected else ft.Colors.BLACK

        self.next_button.disabled = False
        self.update()

    def _on_next_pressed(self, e):
        if self.selected_campus_id:
            # Buscamos el nombre del campus seleccionado para pasarlo a la siguiente pantalla
            campus_nombre_seleccionado = ""
            for campus in self.campus_list:
                if campus['ID_Campus'] == self.selected_campus_id:
                    campus_nombre_seleccionado = campus.get('Nombre', "")
                    break

            # Guardamos en almacenamiento local del cel para recordar la sesión
            self.page.client_storage.set("idCampus", self.selected_campus_id)

            # Navegación
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