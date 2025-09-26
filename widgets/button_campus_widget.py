import flet as ft

class CampusButton:
    def __init__(self, label: str, on_click=None, is_selected=False):
        self.label = label
        self.on_click = on_click
        self.is_selected = is_selected

    def build(self):
        # Colores exactos según tu código Dart
        bg_color = ft.colors.BLUE_900 if self.is_selected else ft.colors.WHITE
        text_color = ft.colors.WHITE if self.is_selected else "#0D47A1"  # Color azul exacto

        return ft.ElevatedButton(
            text=self.label,
            on_click=self.on_click,
            style=ft.ButtonStyle(
                color=text_color,
                bgcolor=bg_color,
                padding=ft.padding.symmetric(vertical=12, horizontal=24),
                side=ft.BorderSide(color="#0D47A1", width=1),  # Borde azul
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            disabled=not self.is_selected
        )