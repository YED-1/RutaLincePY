import flet as ft
from src.database.database import DatabaseHelper
from src.screens.sopa_de_letras_screen import SopaDeLetrasScreen


class SeleccionarSopaScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str):
        super().__init__(expand=True)
        self.page = page
        self.id_carrera = id_carrera
        self.db_helper = DatabaseHelper()

        # Contenedor para manejar el estado de carga
        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando sopas de letras...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.content_area = ft.Container(content=self.loading_view, expand=True)

        self.controls = [self.content_area]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Seleccionar Sopa de Letras"))
        self.page.update()
        self._fetch_data()

    def _fetch_data(self):
        print(f"--- DEBUG (SeleccionarSopa): Buscando sopas para id_carrera='{self.id_carrera}' ---")
        sopas = self.db_helper.get_sopas_con_area_by_id_carrera(self.id_carrera)
        print(f"--- DEBUG (SeleccionarSopa): {len(sopas)} sopas encontradas ---")

        if not sopas:
            self.content_area.content = ft.Column(
                [
                    ft.Icon(ft.Icons.GAMES_OUTLINED, size=48, color=ft.Colors.BLUE_900),
                    ft.Text(
                        "No hay sopas de letras disponibles para esta carrera.",
                        text_align=ft.TextAlign.CENTER,
                        size=16
                    ),
                    ft.Text(
                        "Vuelve más tarde o contacta con tu administrador.",
                        text_align=ft.TextAlign.CENTER,
                        size=14,
                        color=ft.Colors.GREY_600
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        else:
            list_view = ft.ListView(expand=True, spacing=10, padding=16)
            for s in sopas:
                list_view.controls.append(self.create_card(s))
            self.content_area.content = list_view

        self.update()

    def create_card(self, sopa: dict):
        print(f"--- DEBUG (SeleccionarSopa): Creando tarjeta para sopa {sopa['ID_Sopa']} ---")

        card_data = {
            'id': sopa['ID_Sopa'],
            'nombre': sopa.get('NombreArea', 'Área Desconocida')
        }

        # CORRECCIÓN: Envolver el Card en un GestureDetector para hacerlo clickeable
        return ft.GestureDetector(
            on_tap=lambda e, data=card_data: self._on_card_click(data),
            mouse_cursor=ft.MouseCursor.CLICK,
            content=ft.Card(
                elevation=6,
                content=ft.Container(
                    padding=16,
                    border_radius=12,
                    border=ft.border.all(2, ft.Colors.BLUE_900),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.GAMES, color=ft.Colors.BLUE_900),
                                    ft.Text(
                                        f"{sopa.get('NombreArea', 'Área Desconocida')}",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_900,
                                        expand=True
                                    ),
                                ]
                            ),
                            ft.Divider(height=4, color=ft.Colors.BLUE_GREY_100, thickness=2),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.TAG, size=16, color=ft.Colors.BLUE_700),
                                    ft.Text(f"ID Sopa: {sopa['ID_Sopa']}", size=16),
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SPELLCHECK, size=16, color=ft.Colors.BLUE_700),
                                    ft.Text(f"Palabras: {sopa.get('Cantidad_Palabras', 'N/A')}", size=16),
                                ]
                            ),
                            ft.Container(
                                padding=ft.padding.only(top=10),
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Jugar ahora →",
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

    def _on_card_click(self, card_data):
        try:
            id_sopa = card_data['id']
            nombre_area = card_data['nombre']

            print(f"--- DEBUG (SeleccionarSopa): Navegando a SopaDeLetrasScreen con id_sopa='{id_sopa}' ---")

            # Mostrar loading mientras se carga
            self.content_area.content = ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Cargando sopa de letras...", size=16),
                    ft.Text(f"Sopa: {id_sopa}", size=14, color=ft.Colors.GREY_600)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
            self.update()

            # Navegar a la pantalla de sopa de letras
            self.page.clean()
            nueva_pantalla = SopaDeLetrasScreen(
                page=self.page,
                id_sopa=id_sopa,
                nombre_area=nombre_area
            )
            self.page.add(nueva_pantalla)
            print("--- DEBUG (SeleccionarSopa): Navegación completada ---")

        except Exception as ex:
            print(f"--- DEBUG (SeleccionarSopa): ERROR en _on_card_click: {ex} ---")
            import traceback
            traceback.print_exc()

            # Mostrar error al usuario
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Error al cargar la sopa de letras: {str(ex)}"),
                    action="OK"
                )
            )