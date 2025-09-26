import flet as ft
from database.database import DatabaseHelper
from database.csv_loader import CsvLoader


class DatosScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = self.create_view()

    def create_view(self):
        """Crea la vista principal de selección de datos"""
        return ft.View(
            route="/datos",
            controls=[
                ft.AppBar(title=ft.Text("Seleccionar Datos")),
                ft.ListView(
                    controls=[
                        ft.ListTile(
                            title=ft.Text("Ver Campus"),
                            on_click=lambda e: self.navigate_to_data_screen("Campus")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Carreras"),
                            on_click=lambda e: self.navigate_to_data_screen("Carrera")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Carrera_Campus"),
                            on_click=lambda e: self.navigate_to_data_screen("Carrera_Campus")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Video"),
                            on_click=lambda e: self.navigate_to_data_screen("Video")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Area"),
                            on_click=lambda e: self.navigate_to_data_screen("Area")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Pregunta"),
                            on_click=lambda e: self.navigate_to_data_screen("Pregunta")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Comentario"),
                            on_click=lambda e: self.navigate_to_data_screen("Comentario")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Simulador"),
                            on_click=lambda e: self.navigate_to_data_screen("Simulador")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Crucigramas"),
                            on_click=lambda e: self.navigate_to_data_screen("Crucigrama")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Sopas de letras"),
                            on_click=lambda e: self.navigate_to_data_screen("Sopa")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Palabras"),
                            on_click=lambda e: self.navigate_to_data_screen("Palabra")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Usuarios"),
                            on_click=lambda e: self.navigate_to_data_screen("Usuario")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Temas"),
                            on_click=lambda e: self.navigate_to_data_screen("Tema")
                        ),
                        ft.ListTile(
                            title=ft.Text("Ver Resultados"),
                            on_click=lambda e: self.navigate_to_data_screen("Resultado")
                        ),
                    ],
                    expand=True
                )
            ]
        )

    def navigate_to_data_screen(self, entity):
        """Navega a la pantalla de visualización de datos específica"""
        data_screen = DataScreen(self.page, entity=entity)
        self.page.views.append(data_screen.view)
        self.page.update()


class DataScreen:
    def __init__(self, page: ft.Page, entity: str):
        self.page = page
        self.entity = entity
        self.db = DatabaseHelper()
        self.datos_list = []
        self.view = self.create_view()
        self.load_data()

    def create_view(self):
        """Crea la vista de visualización de datos específicos"""
        self.data_listview = ft.ListView(expand=True)

        return ft.View(
            route=f"/datos/{self.entity}",
            controls=[
                ft.AppBar(title=ft.Text(self.entity)),
                ft.ProgressRing() if not self.datos_list else self.data_listview
            ]
        )

    async def load_data(self):
        """Carga los datos según la entidad seleccionada"""
        try:
            # Obtén los datos según la entidad seleccionada
            if self.entity == 'Campus':
                self.datos_list = await self.db.get_campus()
            elif self.entity == 'Carrera':
                self.datos_list = await self.db.get_carrera()
            elif self.entity == 'Carrera_Campus':
                self.datos_list = await self.db.get_carrera_campus()
            elif self.entity == 'Video':
                self.datos_list = await self.db.get_video()
            elif self.entity == 'Area':
                self.datos_list = await self.db.get_area()
            elif self.entity == 'Pregunta':
                self.datos_list = await self.db.get_pregunta()
            elif self.entity == 'Comentario':
                self.datos_list = await self.db.get_comentario()
            elif self.entity == 'Simulador':
                self.datos_list = await self.db.get_simulador()
            elif self.entity == 'Crucigrama':
                self.datos_list = await self.db.get_crucigrama()
            elif self.entity == 'Sopa':
                self.datos_list = await self.db.get_sopa()
            elif self.entity == 'Palabra':
                self.datos_list = await self.db.get_palabra()
            elif self.entity == 'Usuario':
                self.datos_list = await self.db.get_usuario()
            elif self.entity == 'Tema':
                self.datos_list = await self.db.get_tema()
            elif self.entity == 'Resultado':
                self.datos_list = await self.db.get_resultado()
            else:
                self.datos_list = []

            self.update_data_display()

        except Exception as e:
            print(f"Error cargando datos de {self.entity}: {e}")
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error cargando datos: {str(e)}")))

    def update_data_display(self):
        """Actualiza la visualización de datos"""
        self.data_listview.controls.clear()

        for item in self.datos_list:
            list_tile = self.create_data_list_tile(item)
            self.data_listview.controls.append(list_tile)

        # Reemplazar el progress ring con la lista de datos
        if self.page.views and len(self.page.views) > 0:
            current_view = self.page.views[-1]
            if len(current_view.controls) > 1:
                current_view.controls[1] = self.data_listview
                self.page.update()

    def create_data_list_tile(self, item):
        """Crea un ListTile para mostrar los datos"""
        # Crear contenido dinámico basado en los campos disponibles
        content_controls = []

        # Mapear campos según la entidad (similar a tu código Dart)
        for key, value in item.items():
            if value is not None:
                content_controls.append(
                    ft.Text(f"{key}: {value}", size=12)
                )

        return ft.ListTile(
            title=ft.Column(
                cross_axis_alignment=ft.CrossAxisAlignment.START,
                controls=content_controls
            )
        )