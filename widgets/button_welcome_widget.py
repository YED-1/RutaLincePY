import flet as ft

class WelcomeButton:
    def __init__(self, label: str, on_click=None):
        self.label = label
        self.on_click = on_click

    def build(self):
        return ft.ElevatedButton(
            text=self.label,
            on_click=self.on_click,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_900,
                padding=ft.padding.all(16),
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )