import flet as ft
from src.screens.seleccionar_sopa_screen import SeleccionarSopaScreen
#from src.screens.seleccionar_crucigrama_screen import SeleccionarCrucigramaScreen #No quitar comentario, futura implementación
# Pendiente por ahora
class JuegosScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str, id_usuario: str):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            spacing=40 # Equivalente al SizedBox(height: 40)
        )
        self.page = page
        self.id_carrera = id_carrera
        self.id_campus = id_campus
        self.id_usuario = id_usuario

        # Creamos los botones directamente aquí
        self.controls = [
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.GRID_ON), ft.Text("Sopa de Letras")]),
                on_click=self.go_to_sopa,
                width=250,
                height=60
            ),
            # No quitar comentario
            #ft.ElevatedButton(
                #content=ft.Row([ft.Icon(ft.Icons.FORMAT_SHAPES), ft.Text("Palabreta")]),
                #on_click=self.go_to_palabreta,
                #width=250,
                #height=60
            #),
        ]

    def did_mount(self):
        from src.widgets.nav_bar_widget import create_nav_bar
        self.page.appbar = None
        self.page.navigation_bar = create_nav_bar(
            page=self.page,
            selected_index=1, # 1 porque estamos en la pantalla de "Juegos"
            id_carrera=self.id_carrera,
            id_campus=self.id_campus,
            id_usuario=self.id_usuario
        )
        self.page.update()

    def go_to_sopa(self, e):
        self.page.clean()
        self.page.add(SeleccionarSopaScreen(self.page, id_carrera=self.id_carrera))

    #def go_to_palabreta(self, e): Palabreta de añadirá en un futuro junto a otros juegos
        #self.page.clean()
        #self.page.add(SeleccionarCrucigramaScreen(self.page, id_carrera=self.id_carrera))