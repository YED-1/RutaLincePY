import flet as ft
from src.database.database import DatabaseHelper



class SimuladorScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str, id_usuario: str):
        super().__init__(expand=True)
        print(f"\n--- DEBUG (Simulador): Received id_carrera='{id_carrera}' ---")  # Debug print
        self.page = page
        self.id_carrera = id_carrera
        self.id_campus = id_campus
        self.id_usuario = id_usuario
        self.db_helper = DatabaseHelper()

        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando simuladores...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.content_area = ft.Container(content=self.loading_view, expand=True)

        self.controls = [self.content_area]

    def did_mount(self):
        # AÑADIMOS la importación aquí, justo antes de usarla
        from src.widgets.nav_bar_widget import create_nav_bar

        self.page.appbar = None
        self.page.navigation_bar = create_nav_bar(
            page=self.page,
            selected_index=2,  # Índice 2 para Simulador
            id_carrera=self.id_carrera,
            id_campus=self.id_campus,
            id_usuario=self.id_usuario
        )
        self.page.update()
        self._fetch_data()

    def _fetch_data(self):
        print(
            f"--- DEBUG (Simulador): Querying DB for Simuladores with id_carrera='{self.id_carrera}' ---")  # Debug print
        simuladores = self.db_helper.get_simuladores_con_area_by_id_carrera(self.id_carrera)
        print(f"--- DEBUG (Simulador): Found {len(simuladores)} Simuladores. Data: {simuladores} ---")  # Debug print

        if not simuladores:
            print("--- DEBUG (Simulador): No Simuladores found. Displaying message. ---")  # Debug print
            self.content_area.content = ft.Text("No hay simuladores disponibles para esta carrera.",
                                                text_align=ft.TextAlign.CENTER)
        else:
            print("--- DEBUG (Simulador): Building ListView for Simuladores. ---")  # Debug print
            list_view = ft.ListView(expand=True, spacing=10, padding=50)
            for sim in simuladores:
                list_view.controls.append(self.create_card(sim))
            self.content_area.content = list_view

        self.update()

    def create_card(self, simulador: dict):
        card_data = {
            'id_area': simulador['ID_Area'],
            'longitud': simulador['Longitud'],
            'id_simulador': simulador['ID_Simulador']
        }

        return ft.Card(
            data=card_data,
            on_click=self._on_card_click,
            elevation=6,
            content=ft.Container(
                padding=16,
                border_radius=12,
                border=ft.border.all(2, ft.Colors.BLUE_900),
                content=ft.Column(
                    cross_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            f"{simulador.get('NombreArea', 'Área Desconocida')} - {simulador['ID_Area']}",
                            # Use .get for safety
                            size=23, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900
                        ),
                        ft.Divider(height=4, color=ft.Colors.BLUE_GREY_100, thickness=2),
                        ft.Text(f"ID Simulador: {simulador['ID_Simulador']}", size=16, ),
                    ]
                )
            )
        )

    def _on_card_click(self, e):
        from src.screens.preguntas_screen import PreguntasScreen  # Importación local
        sim_data = e.control.data
        print(
            f"--- DEBUG (Simulador): Card clicked. Navigating to PreguntasScreen with data: {sim_data} ---")  # Debug print
        self.page.clean()
        self.page.add(
            PreguntasScreen(
                page=self.page,
                id_area=sim_data['id_area'],
                longitud=sim_data['longitud'],
                id_usuario=self.id_usuario,
                id_simulador=sim_data['id_simulador']
            )
        )

