import flet as ft
from src.database.database import DatabaseHelper


class SeleccionarCrucigramaScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str):
        super().__init__(expand=True)
        self.page = page
        self.id_carrera = id_carrera
        self.db_helper = DatabaseHelper()

        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando palabretas...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.content_area = ft.Container(content=self.loading_view, expand=True)

        self.controls = [self.content_area]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Seleccionar Palabreta"))
        self.page.update()
        self._fetch_data()

    def _fetch_data(self):
        crucigramas = self.db_helper.get_crucigramas_con_area_by_id_carrera(self.id_carrera)

        if not crucigramas:
            self.content_area.content = ft.Text("No hay palabretas disponibles para esta carrera.",
                                                text_align=ft.TextAlign.CENTER)
        else:
            list_view = ft.ListView(expand=True, spacing=10, padding=16)
            for c in crucigramas:
                list_view.controls.append(self.create_card(c))
            self.content_area.content = list_view

        self.update()

    def create_card(self, crucigrama: dict):
        return ft.Card(
            data=crucigrama['ID_Crucigrama'],
            on_click=self._on_card_click,
            elevation=6,
            content=ft.Container(
                padding=16,
                border_radius=12,
                border=ft.border.all(2, ft.colors.BLUE_900),
                content=ft.Column(
                    cross_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            f"{crucigrama['NombreArea']} - {crucigrama['ID_Area']}",
                            size=23,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_900
                        ),
                        ft.Divider(height=4, color=ft.colors.TEAL_100, thickness=2),
                        ft.Text(
                            f"Palabreta: {crucigrama['ID_Crucigrama']}",
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(f"Palabras posibles: {crucigrama['Cantidad_Palabras']}", size=16),
                    ]
                )
            )
        )

    def _on_card_click(self, e):
        # Importamos la pantalla del juego aquí para evitar importaciones circulares
        from src.screens.crucigrama_screen import CrucigramaScreen

        id_crucigrama = e.control.data
        self.page.clean()
        self.page.add(CrucigramaScreen(self.page, id_crucigrama=id_crucigrama))