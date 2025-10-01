# En widgets/button_welcome_widget.py
import flet as ft

def WelcomeButton(label: str, on_click=None):
    """
    Crea un botón de bienvenida estilizado, idéntico al original de Flutter.
    """
    return ft.ElevatedButton(
        # Usamos 'content' en lugar de 'text' para un estilo detallado
        content=ft.Text(
            value=label,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE # El color del texto va aquí
        ),
        on_click=on_click,
        style=ft.ButtonStyle(
            # El color del texto ya no es necesario aquí
            bgcolor=ft.colors.BLUE_900,
            padding=ft.padding.all(16),
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )