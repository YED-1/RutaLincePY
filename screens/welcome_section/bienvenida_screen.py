import flet as ft
from widgets.button_welcome_widget import WelcomeButton


def WelcomeScreenView(page: ft.Page):
    """
    Retorna una Vista (View) que representa la pantalla de bienvenida,
    utilizando el botón personalizado.
    """

    # --- Función de Navegación ---
    def go_to_seleccion_campus(e):
        page.go("/seleccion-campus")

    # --- Controles de la UI ---

    welcome_text = ft.Text(
        "Bienvenido a Ruta Lince",
        size=32,
        weight=ft.FontWeight.BOLD,
    )

    subtitle_text = ft.Text(
        "Responde dos preguntas rápidas para comenzar.",
        size=16,
        color=ft.colors.GREY,
        text_align=ft.TextAlign.CENTER,
    )

    # --- Estructura de la Vista ---
    return ft.View(
        route="/",  # La ruta para esta vista (la raíz o inicial)

        # Centramos todo el contenido
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        controls=[
            ft.Column(
                controls=[
                    welcome_text,
                    ft.Container(height=10),
                    subtitle_text,
                    ft.Container(height=30),

                    # Usamos nuestro botón personalizado directamente
                    WelcomeButton(
                        label="¡Vamos!",
                        on_click=go_to_seleccion_campus
                    )
                ],
                # Centramos los controles dentro de la columna
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
        ]
    )