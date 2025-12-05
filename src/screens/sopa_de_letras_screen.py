import flet as ft
from word_search_generator import WordSearch
from src.database.database import DatabaseHelper
import math


# Clase auxiliar para coordenadas
#
class Coord:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return isinstance(other, Coord) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

#Clase que crea la sopa de letras
class SopaDeLetrasScreen(ft.Column):
    def __init__(self, page: ft.Page, id_sopa: str, nombre_area: str):
        super().__init__(expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page = page
        self.id_sopa = id_sopa
        self.nombre_area = nombre_area
        self.db_helper = DatabaseHelper()

        self.words = []
        self.puzzle_obj = None
        self.grid_data = []
        self.grid_size = 12
        self.cell_size = 35
        self.start_coord = None
        self.current_coord = None
        self.current_path = set()
        self.found_words = set()
        self.found_cells = set()

        self.grid_view = ft.GridView(
            runs_count=self.grid_size,
            spacing=0,
            run_spacing=0,
            width=self.cell_size * self.grid_size,
            height=self.cell_size * self.grid_size,
        )
        self.words_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER)

        self.controls = [
            ft.Text(self.nombre_area.upper(), size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.GestureDetector(
                    on_pan_start=self._on_pan_start,
                    on_pan_update=self._on_pan_update,
                    on_pan_end=self._on_pan_end,
                    content=self.grid_view,
                ),
                alignment=ft.alignment.center
            ),
            ft.Container(height=20),
            ft.Text("Palabras", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.words_row,
                padding=8,
                bgcolor=ft.Colors.GREY_300,
                border_radius=8
            )
        ]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Sopa de Letras"))
        self._init_sopa()
        self.page.update()

    def _init_sopa(self):
        try:
            self.words = self.db_helper.get_palabras_por_sopa(self.id_sopa)
            print(f"--- DEBUG (Sopa): Palabras encontradas: {self.words} ---")

            if not self.words:
                self.controls.clear()
                self.controls.append(
                    ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED),
                        ft.Text("No se encontraron palabras para este juego.", text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
                self.update()
                return

            # Crear el puzzle de sopa de letras
            self.puzzle_obj = WordSearch(",".join(self.words), size=self.grid_size)
            self.grid_data = [list(row) for row in str(self.puzzle_obj).split('\n') if row.strip()]

            # se Asegura de que el grid tenga el tamaño correcto
            if len(self.grid_data) < self.grid_size:
                for _ in range(self.grid_size - len(self.grid_data)):
                    self.grid_data.append([' '] * self.grid_size)

            print(
                f"--- DEBUG (Sopa): Grid creado, tamaño: {len(self.grid_data)}x{len(self.grid_data[0]) if self.grid_data else 0} ---")

            self.grid_view.controls.clear()
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if r < len(self.grid_data) and c < len(self.grid_data[r]):
                        letter = self.grid_data[r][c].upper()
                    else:
                        letter = ' '  # Rellenar con espacios si es necesario

                    self.grid_view.controls.append(
                        ft.Container(
                            width=self.cell_size,
                            height=self.cell_size,
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, ft.Colors.BLACK12),
                            content=ft.Text(letter, size=18, weight=ft.FontWeight.BOLD),
                        )
                    )

            self.words_row.controls.clear()
            for word in self.words:
                self.words_row.controls.append(
                    ft.Chip(
                        label=ft.Text(word.upper()),  # Usar 'label' en lugar de 'content' esto causa errores
                        bgcolor=ft.Colors.WHITE,
                        check_color=ft.Colors.WHITE,
                        selected_color=ft.Colors.BLUE_900,
                    )
                )
            self.update()

        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _init_sopa: {e} ---")
            import traceback
            traceback.print_exc()
            self.controls.clear()
            self.controls.append(
                ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED),
                    ft.Text(f"Error al cargar la sopa de letras: {str(e)}", text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
            self.update()

    def _coord_from_position(self, x, y):
        try:
            col = math.floor(x / self.cell_size)
            row = math.floor(y / self.cell_size)
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                return Coord(row, col)
            return None
        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _coord_from_position: {e} ---")
            return None

    def _update_path(self):
        try:
            path = set()
            if self.start_coord and self.current_coord:
                dr = self.current_coord.row - self.start_coord.row
                dc = self.current_coord.col - self.start_coord.col
                steps = max(abs(dr), abs(dc))

                # Solo permitir líneas rectas (horizontal, vertical, diagonal)
                is_straight_line = abs(dr) == abs(dc) or dr == 0 or dc == 0
                if not is_straight_line:
                    return

                if steps == 0:
                    path.add(self.start_coord)
                else:
                    step_row = dr / steps
                    step_col = dc / steps
                    for i in range(steps + 1):
                        row = round(self.start_coord.row + step_row * i)
                        col = round(self.start_coord.col + step_col * i)
                        path.add(Coord(row, col))

            self.current_path = path
            self._update_grid_colors()

        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _update_path: {e} ---")

    def _check_path(self):
        try:
            if not self.current_path or len(self.current_path) < 2:
                self.current_path = set()
                self._update_grid_colors()
                return

            # Ordenar las coordenadas del path
            path_list = sorted(list(self.current_path),
                               key=lambda c: (c.row, c.col))

            # Obtener el texto del path
            text = "".join([self.grid_data[c.row][c.col] for c in path_list])
            rev_text = text[::-1]

            found_word = None
            if text.lower() in self.words:
                found_word = text.lower()
            elif rev_text.lower() in self.words:
                found_word = rev_text.lower()

            if found_word and found_word not in self.found_words:
                self.found_words.add(found_word)
                self.found_cells.update(self.current_path)
                print(f"--- DEBUG (Sopa): Palabra encontrada: {found_word} ---")

            self.start_coord = None
            self.current_coord = None
            self.current_path = set()
            self._update_grid_colors()
            self._update_words_chips()

            if len(self.found_words) == len(self.words):
                self._show_congrats_dialog()

        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _check_path: {e} ---")

    def _update_grid_colors(self):
        try:
            for i, cell_container in enumerate(self.grid_view.controls):
                row, col = divmod(i, self.grid_size)
                coord = Coord(row, col)


                if coord in self.found_cells:
                    cell_container.bgcolor = ft.Colors.GREEN_200  # Verde claro para palabras encontradas
                elif coord in self.current_path:
                    cell_container.bgcolor = ft.Colors.BLUE_200  # Azul claro para selección actual
                else:
                    cell_container.bgcolor = ft.Colors.WHITE  # Blanco por defecto

                # Asegurar que el texto sea visible
                if hasattr(cell_container.content, 'color'):
                    if coord in self.found_cells or coord in self.current_path:
                        cell_container.content.color = ft.Colors.BLACK  # Texto negro sobre fondo claro
                    else:
                        cell_container.content.color = ft.Colors.BLACK  # Texto negro por defecto

            self.grid_view.update()

        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _update_grid_colors: {e} ---")

    def _update_words_chips(self):
        try:
            for chip in self.words_row.controls:
                # CORREGIDO: Acceder al texto correctamente
                word = chip.label.value.lower()
                if word in self.found_words:
                    chip.bgcolor = ft.Colors.GREEN_500  # Verde para palabras encontradas
                    chip.label.color = ft.Colors.WHITE  # Texto blanco
                else:
                    chip.bgcolor = ft.Colors.WHITE  # Blanco para palabras no encontradas
                    chip.label.color = ft.Colors.BLACK  # Texto negro

            self.words_row.update()

        except Exception as e:
            print(f"--- DEBUG (Sopa): ERROR en _update_words_chips: {e} ---")

    def _show_congrats_dialog(self):
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            # Navegar de vuelta
            from src.screens.seleccionar_sopa_screen import SeleccionarSopaScreen
            self.page.clean()
            id_carrera = self.page.client_storage.get("idCarrera")
            if id_carrera:
                self.page.add(SeleccionarSopaScreen(self.page, id_carrera=id_carrera))

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Text("¡Felicidades!")
            ]),
            content=ft.Text("¡Has encontrado todas las palabras!"),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _on_pan_start(self, e: ft.DragStartEvent):
        try:
            self.start_coord = self._coord_from_position(e.local_x, e.local_y)
            self.current_coord = self.start_coord
            self._update_path()
        except Exception as ex:
            print(f"--- DEBUG (Sopa): ERROR en _on_pan_start: {ex} ---")

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        try:
            coord = self._coord_from_position(e.local_x, e.local_y)
            if coord:
                self.current_coord = coord
                self._update_path()
        except Exception as ex:
            print(f"--- DEBUG (Sopa): ERROR en _on_pan_update: {ex} ---")

    def _on_pan_end(self, e: ft.DragEndEvent):
        try:
            self._check_path()
        except Exception as ex:
            print(f"--- DEBUG (Sopa): ERROR en _on_pan_end: {ex} ---")