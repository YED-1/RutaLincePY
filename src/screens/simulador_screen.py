import flet as ft
# CORRECCIÓN 1: Importar del archivo correcto
from src.database.database import DatabaseHelper


class SimuladorScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str, id_usuario: str):
        super().__init__(expand=True)
        print(f"\n--- DEBUG (Simulador): Received id_carrera='{id_carrera}' ---")
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
        # Importación diferida para evitar ciclos
        from src.widgets.nav_bar_widget import create_nav_bar

        self.page.appbar = None
        self.page.navigation_bar = create_nav_bar(
            page=self.page,
            selected_index=2,
            id_carrera=self.id_carrera,
            id_campus=self.id_campus,
            id_usuario=self.id_usuario
        )
        self.page.update()
        self._fetch_data()

    def _fetch_data(self):
        print(f"--- DEBUG (Simulador): Querying DB for Simuladores with id_carrera='{self.id_carrera}' ---")

        # Esto llama al método de FirebaseHelper que ya mapea 'NombreArea'
        simuladores = self.db_helper.get_simuladores_con_area_by_id_carrera(self.id_carrera)
        print(f"--- DEBUG (Simulador): Found {len(simuladores)} Simuladores. ---")

        if not simuladores:
            print("--- DEBUG (Simulador): No Simuladores found. Displaying message. ---")
            self.content_area.content = ft.Column(
                [
                    ft.Icon(ft.Icons.QUIZ_OUTLINED, size=64, color=ft.Colors.BLUE_900),
                    ft.Text("No hay simuladores disponibles para esta carrera.",
                            text_align=ft.TextAlign.CENTER, size=18),
                    ft.Text("Vuelve más tarde o contacta con tu administrador.",
                            text_align=ft.TextAlign.CENTER, size=14, color=ft.Colors.GREY_600)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        else:
            print("--- DEBUG (Simulador): Building ListView for Simuladores. ---")
            list_view = ft.ListView(expand=True, spacing=20, padding=20)
            for sim in simuladores:
                list_view.controls.append(self.create_card(sim))
            self.content_area.content = list_view

        self.update()

    def create_card(self, simulador: dict):
        # CORRECCIÓN 2: Uso de .get() y manejo de minúsculas
        # En Firebase guardamos 'id_area', 'longitud', etc.
        # El helper agrega 'ID_Simulador' y 'NombreArea' manualmente.

        card_data = {
            'id_area': simulador.get('id_area'),  # Clave en minúscula desde Firebase
            'longitud': simulador.get('Longitud', 0),  # Helper lo pone en Mayúscula o Minúscula según la función
            'id_simulador': simulador.get('ID_Simulador'),
            'nombre_area': simulador.get('NombreArea', 'Área General')
        }

        # Validar longitud por si viene None
        texto_preguntas = str(card_data['longitud']) if card_data['longitud'] else "N/A"

        # Crear tarjeta con efecto hover
        return ft.Container(
            margin=ft.margin.symmetric(vertical=5),
            content=ft.Card(
                elevation=4,
                content=ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.CLICK,
                    on_tap=lambda e, data=card_data: self._on_card_click(data),
                    on_hover=lambda e: self._on_card_hover(e),
                    content=ft.Container(
                        padding=20,
                        border_radius=12,
                        border=ft.border.all(2, ft.Colors.BLUE_900),
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            spacing=10,
                            controls=[
                                # Header con ícono y título
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.QUIZ,
                                            color=ft.Colors.BLUE_900,
                                            size=28
                                        ),
                                        ft.Text(
                                            card_data['nombre_area'],
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_900,
                                            expand=True
                                        ),
                                    ]
                                ),

                                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_200),

                                # Información del simulador
                                ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.FACT_CHECK, size=16, color=ft.Colors.BLUE_700),
                                                ft.Text(f"Simulador: {card_data['id_simulador']}",
                                                        size=14, color=ft.Colors.GREY_700),
                                            ]
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.QUESTION_ANSWER, size=16, color=ft.Colors.BLUE_700),
                                                ft.Text(f"Preguntas: {texto_preguntas}",
                                                        size=14, color=ft.Colors.GREY_700),
                                            ]
                                        ),
                                    ]
                                ),

                                # Botón de acción
                                ft.Container(
                                    padding=ft.padding.only(top=10),
                                    content=ft.Row(
                                        controls=[
                                            ft.Text(
                                                "Comenzar simulador →",
                                                color=ft.Colors.BLUE_900,
                                                weight=ft.FontWeight.BOLD,
                                                size=14
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END
                                    )
                                )
                            ]
                        )
                    )
                )
            )
        )

    def _on_card_hover(self, e):
        """Efecto hover para las tarjetas"""
        if e.data == "true":
            e.control.content.bgcolor = ft.Colors.BLUE_50
        else:
            e.control.content.bgcolor = ft.Colors.WHITE
        e.control.update()

    def _on_card_click(self, card_data):
        """Maneja el clic en la tarjeta"""
        try:
            print(f"--- DEBUG (Simulador): Card clicked. Data: {card_data} ---")

            from src.screens.preguntas_screen import PreguntasScreen

            # Mostrar loading mientras se carga
            self.content_area.content = ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Cargando preguntas...", size=16),
                    ft.Text(f"Simulador: {card_data['id_simulador']}",
                            size=14, color=ft.Colors.GREY_600)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
            self.update()

            # Navegar a la pantalla de preguntas
            self.page.clean()

            # Pasamos los datos necesarios
            nueva_pantalla = PreguntasScreen(
                page=self.page,
                id_area=card_data['id_area'],
                longitud=card_data['longitud'],
                id_usuario=self.id_usuario,
                id_simulador=card_data['id_simulador']
            )
            self.page.add(nueva_pantalla)
            print("--- DEBUG (Simulador): Navigation to PreguntasScreen completed ---")

        except Exception as ex:
            print(f"--- DEBUG (Simulador): ERROR in _on_card_click: {ex} ---")
            import traceback
            traceback.print_exc()

            # Restaurar la vista si falla
            self._fetch_data()

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al abrir el simulador: Verifique conexión."),
                action="OK"
            )
            self.page.snack_bar.open = True
            self.page.update()