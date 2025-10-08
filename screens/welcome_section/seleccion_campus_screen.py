import flet as ft

# 1. IMPORTAMOS LA PANTALLA A LA QUE VAMOS A NAVEGAR
from screens.welcome_section.seleccion_carrera_screen import SeleccionCarreraScreen


class SeleccionCampusScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page

        # Definimos las variables y controles
        self.db_helper = None
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

        # Asignamos los controles a la propiedad 'controls' de la columna
        self.controls = [
            ft.Container(content=self.title, padding=16),
            self.campus_grid,
            ft.Container(
                content=self.next_button,
                padding=ft.padding.symmetric(horizontal=16, vertical=20),
                alignment=ft.alignment.center,
            ),
        ]

    # did_mount se ejecuta DESPUÉS de que el control se añade a la página
    def did_mount(self):
        self.page.appbar = ft.AppBar(
            title=ft.Text("Selecciona tu Campus"), bgcolor=ft.Colors.GREY_200
        )
        self._fetch_campus()
        self.page.update()

    def _fetch_campus(self):
        # Simulación de la llamada a la base de datos
        self.campus_list = [
            {'ID_Campus': 'C1', 'Nombre': 'Campus Central'},
            {'ID_Campus': 'C2', 'Nombre': 'Campus Norte'},
            {'ID_Campus': 'C3', 'Nombre': 'Campus Sur'},
            {'ID_Campus': 'C4', 'Nombre': 'Campus Poniente'},
        ]
        self.campus_grid.controls.clear()
        for campus in self.campus_list:
            card = self.create_campus_card(campus)
            self.campus_grid.controls.append(card)

    def create_campus_card(self, campus):
        return ft.GestureDetector(
            on_tap=lambda e: self._on_campus_selected(campus['ID_Campus']),
            content=ft.Card(
                data=campus['ID_Campus'],
                content=ft.Container(
                    content=ft.Text(campus['Nombre'], size=18),
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
            # 2. LÓGICA DE NAVEGACIÓN ACTUALIZADA

            # Buscamos el nombre del campus para pasarlo a la siguiente pantalla
            campus_nombre_seleccionado = ""
            for campus in self.campus_list:
                if campus['ID_Campus'] == self.selected_campus_id:
                    campus_nombre_seleccionado = campus['Nombre']
                    break

            self.page.appbar = None
            self.page.clean()

            # Llamamos a la pantalla de selección de carrera con los datos necesarios
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