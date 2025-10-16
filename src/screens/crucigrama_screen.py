import flet as ft
from src.database.database import DatabaseHelper
import random


class CrucigramaScreen(ft.Column):
    def __init__(self, page: ft.Page, id_crucigrama: str):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.id_crucigrama = id_crucigrama
        self.db_helper = DatabaseHelper()

        # --- Game State ---
        self.max_rows = 6
        self.target_word = ""
        self.hint = ""
        self.grid_data = []  # Data (letters)
        self.grid_controls = []  # UI (Containers)
        self.key_buttons = {}  # UI (Buttons)
        self.current_row = 0
        self.current_col = 0

        # --- UI ---
        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando palabreta...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, expand=True
        )
        self.controls = [self.loading_view]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Palabreta"))
        self.page.update()
        self._cargar_palabra()

    def _cargar_palabra(self):
        try:
            data = self.db_helper.palabra_crucigrama(self.id_crucigrama)
            self.target_word = data['palabra'].upper()
            self.hint = data['descripcion']

            word_len = len(self.target_word)
            self.grid_data = [['' for _ in range(word_len)] for _ in range(self.max_rows)]

            self._build_game_view()
        except Exception as e:
            self.controls.clear()
            self.controls.append(ft.Text(f"Error: {e}"))
            self.update()

    def _build_game_view(self):
        word_len = len(self.target_word)

        # Build Grid UI
        self.grid_controls = []
        grid_rows = []
        for r in range(self.max_rows):
            row_controls = []
            row_ui_controls = []
            for c in range(word_len):
                cell = ft.Container(
                    width=50, height=50, margin=4,
                    bgcolor=ft.colors.GREY_300,
                    alignment=ft.alignment.center,
                    content=ft.Text("", size=24, weight=ft.FontWeight.BOLD)
                )
                row_controls.append(cell)
                row_ui_controls.append(cell)
            self.grid_controls.append(row_controls)
            grid_rows.append(ft.Row(controls=row_ui_controls, alignment=ft.MainAxisAlignment.CENTER))

        # Build Keyboard UI
        keyboard_rows = []
        keys = [
            "QWERTYUIOP",
            "ASDFGHJKLÑ",
            "ZXCVBNM"
        ]
        for row_keys in keys:
            key_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=6)
            for key in row_keys:
                button = self._create_key_button(key)
                self.key_buttons[key] = button
                key_row.controls.append(button)
            keyboard_rows.append(key_row)

        # Special buttons row
        special_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=6)
        submit_button = self._create_key_button("ENVIAR", on_click=self._on_submit)
        delete_button = self._create_key_button("BORRAR", on_click=lambda e: self._on_key_tap('BORRAR'))
        special_row.controls.extend([submit_button, delete_button])
        keyboard_rows.append(special_row)

        # Assemble final view
        self.controls.clear()
        self.controls.extend([
            ft.Text(f"Pista: {self.hint}", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            ft.Column(controls=grid_rows),
            ft.Container(height=30),
            ft.Column(controls=keyboard_rows, spacing=6)
        ])
        self.update()

    def _create_key_button(self, key, on_click=None):
        return ft.ElevatedButton(
            text=key,
            width=40 if len(key) == 1 else 100,
            height=50,
            on_click=on_click if on_click else lambda e, k=key: self._on_key_tap(k),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                bgcolor=ft.colors.GREY_600,
                color=ft.colors.WHITE
            )
        )

    def _on_key_tap(self, key: str):
        if self.current_row >= self.max_rows: return

        if key == 'BORRAR':
            if self.current_col > 0:
                self.current_col -= 1
                self.grid_data[self.current_row][self.current_col] = ''
        elif self.current_col < len(self.target_word):
            self.grid_data[self.current_row][self.current_col] = key
            self.current_col += 1

        self._update_grid_ui()

    def _on_submit(self, e):
        if self.current_col < len(self.target_word) or self.current_row >= self.max_rows:
            return

        attempt = "".join(self.grid_data[self.current_row])
        target_chars = list(self.target_word)
        temp_grid_colors = [None] * len(self.target_word)

        # Pass 1: Greens
        for i in range(len(self.target_word)):
            if attempt[i] == self.target_word[i]:
                temp_grid_colors[i] = ft.colors.GREEN_400
                self.key_buttons[attempt[i]].bgcolor = ft.colors.GREEN_400
                target_chars[i] = None  # Mark as used

        # Pass 2: Yellows and Grays
        for i in range(len(self.target_word)):
            if temp_grid_colors[i] is None:
                if attempt[i] in target_chars:
                    temp_grid_colors[i] = ft.colors.YELLOW_400
                    if self.key_buttons[attempt[i]].bgcolor != ft.colors.GREEN_400:
                        self.key_buttons[attempt[i]].bgcolor = ft.colors.YELLOW_400
                    target_chars.remove(attempt[i])
                else:
                    temp_grid_colors[i] = ft.colors.GREY_800
                    if self.key_buttons[attempt[i]].bgcolor not in [ft.colors.GREEN_400, ft.colors.YELLOW_400]:
                        self.key_buttons[attempt[i]].bgcolor = ft.colors.GREY_800

        # Update UI with colors
        for i in range(len(self.target_word)):
            self.grid_controls[self.current_row][i].bgcolor = temp_grid_colors[i]

        # Check for win/lose
        if attempt == self.target_word:
            self._show_result_dialog("¡Felicidades!", f"¡Has adivinado la palabra '{self.target_word}'!", True)
            self.current_row = self.max_rows  # Block further input
        elif self.current_row == self.max_rows - 1:
            self._show_result_dialog("¡Oh no!", f"Se acabaron los intentos. La palabra era '{self.target_word}'.",
                                     False)
            self.current_row += 1
        else:
            self.current_row += 1
            self.current_col = 0

        self.update()

    def _update_grid_ui(self):
        for r in range(self.max_rows):
            for c in range(len(self.target_word)):
                self.grid_controls[r][c].content.value = self.grid_data[r][c]
        self.update()

    def _show_result_dialog(self, title_text, content_text, is_win):
        def go_back(e):
            from src.screens.seleccionar_crucigrama_screen import SeleccionarCrucigramaScreen
            self.page.dialog.open = False
            self.page.clean()
            # We assume idCarrera is stored in client_storage to navigate back
            id_carrera = self.page.client_storage.get("idCarrera")
            if id_carrera:
                self.page.add(SeleccionarCrucigramaScreen(self.page, id_carrera=id_carrera))
            else:  # Fallback
                from src.screens.juegos_screen import JuegosScreen
                self.page.add(JuegosScreen(self.page, id_carrera="", id_campus="", id_usuario=""))

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text),
            content=ft.Text(content_text),
            actions=[ft.TextButton("OK", on_click=go_back)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()