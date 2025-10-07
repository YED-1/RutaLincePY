import flet as ft


class SeleccionCampusScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)  # Inicializamos la columna base
        self.page = page

        # Definimos las variables y controles, pero aún no los mostramos
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
            title=ft.Text("Selecciona tu Campus"), bgcolor=ft.Colors.WHITE30
        )
        # Ahora sí, cargamos los datos
        self._fetch_campus()
        self.page.update()

    def _fetch_campus(self):
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
        # Ya no se necesita self.update() aquí, porque se llama en did_mount

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
            print(f"ID de Campus guardado: {self.selected_campus_id}")
            self.page.appbar = None
            self.page.clean()
            # self.page.add(SeleccionCarreraScreen(self.page))
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor selecciona un campus.")
            )
            self.page.snack_bar.open = True
            self.page.update()