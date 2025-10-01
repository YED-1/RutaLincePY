import flet as ft

def CampusButton(label: str, on_click, is_selected: bool = False):
    """
    Crea un botón cuyo estilo cambia si algo ha sido seleccionado.

    Args:
        label: El texto que mostrará el botón.
        on_click: La función a ejecutar al hacer clic.
        is_selected: Si es True, el botón se muestra en su estilo "activo".
    """
    return ft.ElevatedButton(
        on_click=on_click,
        content=ft.Text(
            value=label,
            size=16,
            weight=ft.FontWeight.BOLD,
            # Lógica condicional para el color del texto
            color=ft.colors.WHITE if is_selected else ft.colors.BLUE_900,
        ),
        style=ft.ButtonStyle(
            # Lógica condicional para el color de fondo
            bgcolor=ft.colors.BLUE_900 if is_selected else ft.colors.WHITE,

            # El borde siempre es azul
            side=ft.BorderSide(color=ft.colors.BLUE_900),

            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(vertical=12, horizontal=24),
        ),
        # Desactivamos el botón si nada ha sido seleccionado
        disabled=not is_selected
    )