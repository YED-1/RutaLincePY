import flet as ft
from word_search_generator import WordSearch
from src.database.database import DatabaseHelper
import math


class Coord:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return isinstance(other, Coord) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"({self.row}, {self.col})"


class SopaDeLetrasScreen(ft.Column):
    def __init__(self, page: ft.Page, id_sopa: str, nombre_area: str):
        # 1. ACTIVAR SCROLL: Es vital para ver el contenido que se desborda
        super().__init__(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )
        self.page = page
        self.id_sopa = id_sopa
        self.nombre_area = nombre_area
        self.db_helper = DatabaseHelper()

        # Variables de estado
        self.words = []
        self.grid_data = []
        self.grid_size = 12
        self.cell_size = 30  # Se recalcula en did_mount
        self.start_coord = None
        self.current_coord = None
        self.current_path = set()
        self.found_words = set()
        self.found_cells = set()

        # Controles UI
        self.grid_view = ft.GridView(
            runs_count=self.grid_size,
            spacing=2,
            run_spacing=2,
            padding=0,
        )

        self.words_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=5)

        self.header = ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self._go_back()),
                ft.Text(self.nombre_area.upper(), size=16, weight=ft.FontWeight.BOLD, expand=True,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(width=40)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.controls = [
            ft.Container(padding=10, content=self.header),
            # Contenedor del Tablero con GestureDetector
            ft.Container(
                content=ft.GestureDetector(
                    on_pan_start=self._on_pan_start,
                    on_pan_update=self._on_pan_update,
                    on_pan_end=self._on_pan_end,
                    content=self.grid_view,
                ),
                alignment=ft.alignment.center,
                border_radius=10,
                padding=10,
                bgcolor=ft.Colors.BLUE_50,
            ),
            ft.Container(height=20),
            ft.Text("Palabras a encontrar:", size=16, weight=ft.FontWeight.BOLD),
            # Contenedor de las palabras a buscar
            ft.Container(
                content=self.words_row,
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_300)
            ),
            # Espacio extra al final para asegurar que el scroll llegue hasta abajo
            ft.Container(height=50)
        ]

    def did_mount(self):
        # 2. RESPONSIVO: Calculamos el tamaño de celda según el ancho de pantalla
        screen_width = self.page.window_width if self.page.window_width else 400
        # Restamos margenes (aprox 60px) y dividimos por columnas
        self.cell_size = (screen_width - 60) / self.grid_size

        # Fijamos dimensiones al GridView para que funcione dentro del scroll
        total_size = (self.cell_size * self.grid_size) + (self.grid_size * 2)
        self.grid_view.width = total_size
        self.grid_view.height = total_size

        self._init_sopa()
        self.page.update()

    def _init_sopa(self):
        try:
            self.words = self.db_helper.get_palabras_por_sopa(self.id_sopa)

            if not self.words:
                self.words = ["PRUEBA", "SOPA", "FLET", "LINCE"]

            # Generar sopa con la librería
            clean_words = [w.strip().upper() for w in self.words if w.strip()]
            puzzle = WordSearch(",".join(clean_words), size=self.grid_size)

            # Convertir string a matriz
            puzzle_str = str(puzzle).replace(' ', '')
            lines = puzzle_str.split('\n')

            self.grid_data = []
            for line in lines:
                if line.strip():
                    row_chars = list(line.strip().replace(' ', ''))
                    # Rellenar si falta longitud
                    if len(row_chars) < self.grid_size:
                        row_chars.extend(['X'] * (self.grid_size - len(row_chars)))
                    self.grid_data.append(row_chars[:self.grid_size])

            # Rellenar filas si faltan
            while len(self.grid_data) < self.grid_size:
                self.grid_data.append(['X'] * self.grid_size)

            self._draw_grid()
            self._draw_word_chips()
            self.update()

        except Exception as e:
            print(f"Error sopa: {e}")

    def _draw_grid(self):
        self.grid_view.controls.clear()
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                letter = self.grid_data[r][c]
                cell = ft.Container(
                    content=ft.Text(letter, size=self.cell_size * 0.5, weight=ft.FontWeight.BOLD),
                    width=self.cell_size,
                    height=self.cell_size,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.BLUE_100),
                    data=Coord(r, c)
                )
                self.grid_view.controls.append(cell)

    def _draw_word_chips(self):
        self.words_row.controls.clear()
        for word in self.words:
            is_found = word.upper() in self.found_words
            self.words_row.controls.append(
                ft.Container(
                    content=ft.Text(
                        word.upper(),
                        color=ft.Colors.WHITE if is_found else ft.Colors.BLACK,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=ft.Colors.GREEN if is_found else ft.Colors.GREY_200,
                    border_radius=20,
                    opacity=0.5 if is_found else 1.0
                )
            )

    # --- LÓGICA TÁCTIL ---

    def _coord_from_position(self, x, y):
        # Convertir píxeles a coordenadas de matriz
        effective_size = self.cell_size + 2
        col = int(x // effective_size)
        row = int(y // effective_size)
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return Coord(row, col)
        return None

    def _on_pan_start(self, e: ft.DragStartEvent):
        self.start_coord = self._coord_from_position(e.local_x, e.local_y)
        self.current_coord = self.start_coord
        self._calculate_tolerant_path()

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        new_coord = self._coord_from_position(e.local_x, e.local_y)
        if new_coord and new_coord != self.current_coord:
            self.current_coord = new_coord
            self._calculate_tolerant_path()

    def _on_pan_end(self, e: ft.DragEndEvent):
        self._check_word()

    def _calculate_tolerant_path(self):
        """
        3. SELECCIÓN INTELIGENTE: Detecta si quieres ir horizontal, vertical
        o diagonal y 'imanta' la selección a esa línea.
        """
        if not self.start_coord or not self.current_coord:
            return

        r1, c1 = self.start_coord.row, self.start_coord.col
        r2, c2 = self.current_coord.row, self.current_coord.col

        dr = r2 - r1
        dc = c2 - c1

        if dr == 0 and dc == 0:
            self.current_path = {self.start_coord}
            self._refresh_grid_colors()
            return

        # Calcular ángulo para determinar dirección
        angle = math.degrees(math.atan2(dr, dc)) % 360

        direction = None  # 'H', 'V', 'D1', 'D2'

        # Tolerancia angular para facilitar la selección
        if (337.5 <= angle or angle < 22.5) or (157.5 <= angle < 202.5):
            direction = 'H'
        elif (67.5 <= angle < 112.5) or (247.5 <= angle < 292.5):
            direction = 'V'
        elif (22.5 <= angle < 67.5) or (202.5 <= angle < 247.5):
            direction = 'D1'  # \
        elif (112.5 <= angle < 157.5) or (292.5 <= angle < 337.5):
            direction = 'D2'  # /

        # Ajustar punto final (Snapping)
        final_r, final_c = r2, c2

        if direction == 'H':
            final_r = r1
        elif direction == 'V':
            final_c = c1
        elif direction == 'D1':  # Diagonal perfecta
            dist = max(abs(dr), abs(dc))
            final_r = r1 + (dist * (1 if dr > 0 else -1))
            final_c = c1 + (dist * (1 if dc > 0 else -1))
        elif direction == 'D2':
            dist = max(abs(dr), abs(dc))
            final_r = r1 + (dist * (1 if dr > 0 else -1))
            final_c = c1 + (dist * (1 if dc > 0 else -1))

        # Límites
        final_r = max(0, min(self.grid_size - 1, final_r))
        final_c = max(0, min(self.grid_size - 1, final_c))

        # Generar camino
        self.current_path.clear()
        dr_final = final_r - r1
        dc_final = final_c - c1
        steps = max(abs(dr_final), abs(dc_final))

        for i in range(steps + 1):
            r = r1 + round(i * dr_final / steps) if steps else r1
            c = c1 + round(i * dc_final / steps) if steps else c1
            self.current_path.add(Coord(r, c))

        self._refresh_grid_colors()

    def _refresh_grid_colors(self):
        # Actualiza colores: Verde (ya encontrado), Azul (seleccionando), Blanco (normal)
        for i, cell in enumerate(self.grid_view.controls):
            coord = cell.data
            if coord in self.found_cells:
                cell.bgcolor = ft.Colors.GREEN_300
                cell.content.color = ft.Colors.WHITE
            elif coord in self.current_path:
                cell.bgcolor = ft.Colors.BLUE_300
                cell.content.color = ft.Colors.WHITE
            else:
                cell.bgcolor = ft.Colors.WHITE
                cell.content.color = ft.Colors.BLACK
        self.grid_view.update()

    def _check_word(self):
        if not self.current_path: return

        # Reconstruir palabra desde el path ordenado
        path_list = list(self.current_path)
        if not path_list: return

        # Encontrar extremos para ordenar correctamente
        r1, c1 = self.start_coord.row, self.start_coord.col
        end_coord = max(path_list, key=lambda c: max(abs(c.row - r1), abs(c.col - c1)))

        # Reconstruir línea ordenada
        line_coords = []
        dr = end_coord.row - r1
        dc = end_coord.col - c1
        steps = max(abs(dr), abs(dc))

        for i in range(steps + 1):
            r = r1 + round(i * dr / steps) if steps else r1
            c = c1 + round(i * dc / steps) if steps else c1
            line_coords.append(Coord(r, c))

        word_str = "".join([self.grid_data[c.row][c.col] for c in line_coords])

        # Verificar palabra (normal o invertida)
        if word_str in self.words and word_str not in self.found_words:
            self._word_found(word_str, line_coords)
        elif word_str[::-1] in self.words and word_str[::-1] not in self.found_words:
            self._word_found(word_str[::-1], line_coords)
        else:
            self.current_path.clear()
            self._refresh_grid_colors()

    def _word_found(self, word, path):
        self.found_words.add(word)
        self.found_cells.update(path)
        self.current_path.clear()
        self._refresh_grid_colors()
        self._draw_word_chips()
        self.words_row.update()

        if len(self.found_words) == len(self.words):
            self._show_win_dialog()

    def _show_win_dialog(self):
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()
            self._go_back()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("¡Felicidades!"),
            content=ft.Text("Has completado la sopa de letras."),
            actions=[ft.TextButton("Salir", on_click=close_dlg)],
        )
        self.page.dialog.open = True
        self.page.update()

    def _go_back(self):
        from src.screens.seleccionar_sopa_screen import SeleccionarSopaScreen
        self.page.controls.clear()
        id_carrera = self.page.client_storage.get("idCarrera")
        self.page.add(SeleccionarSopaScreen(self.page, id_carrera=id_carrera))
        self.page.update()