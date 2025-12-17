import flet as ft


class CreditosScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(
            scroll=ft.ScrollMode.AUTO,  # Habilita el scroll
            expand=True,  # <--- ESTO ES LA CLAVE: Obliga a respetar el alto de la ventana
            spacing=10
        )
        self.page = page

        # Configuración de la página para esta vista
        self.page.appbar = ft.AppBar(title=ft.Text("Créditos del Proyecto"))
        self.page.navigation_bar = None
        self.page.update()

        # Helper para no repetir código al crear las 'ListTile'
        def create_person_tile(name: str):
            return ft.ListTile(
                leading=ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON),
                    bgcolor=ft.Colors.BLUE_900
                ),
                title=ft.Text(name, size=18)
            )

        # Usamos extend en lugar de asignar la lista para que se agreguen directamente a la Columna principal
        self.controls.extend([
            ft.Container(
                padding=ft.padding.only(top=10, bottom=40, left=20, right=20),
                # Aumenté bottom para que no se corte el botón al final
                content=ft.Column(
                    controls=[
                        # Introducción
                        ft.Text(
                            'Este proyecto se realiza dentro del programa de Servicio Social / Practicas Profesionales de Dirección Nacional de Programas de Ingenierías',
                            size=16,
                            text_align=ft.TextAlign.JUSTIFY,
                        ),
                        ft.Container(height=20),

                        # Director del Proyecto
                        ft.Text(
                            'Director del Proyecto',
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Mtro. Sánchez Gutiérrez Salvador'),
                        ft.Container(height=20),

                        # Scrum Master
                        ft.Text(
                            'Scrum Master y/o Asesor Académico',
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='César Antonio Ríos Olivares'),
                        ft.Container(height=20),

                        # Desarrolladores Móvil
                        ft.Text(
                            'Devs Móvil:',
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Aguilar Cabrera Donovan Yosef'),
                        create_person_tile(name='Ayala Rayón Omar'),
                        create_person_tile(name='Jiménez Alvear Joshua Yedreick'),
                        create_person_tile(name='Luna Ocampo Alejandro'),
                        create_person_tile(name='Quiroz Mora Raúl Alejandro'),
                        ft.Container(height=20),

                        # Desarrolladores Web
                        ft.Text(
                            'Devs Web',
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Baltazar Hijanosa Carlos Alberto'),
                        ft.Container(height=20),

                        # Tester
                        ft.Text(
                            'Tester:',
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Melo Tatenco Cristopher Donovan'),
                        ft.Container(height=30),

                        ft.Text(
                            'Documentación',
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Ortiz Sánchez Mauricio Marat'),
                        ft.Container(height=20),

                        ft.Text(
                            'Universidad del Valle de México',
                            size=15,
                            italic=True,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),

                        # Botón centrado
                        ft.Row(
                            [ft.ElevatedButton("Volver a Ajustes", on_click=self.go_back, width=200)],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),

                        # Espacio extra al final para asegurar que el scroll llegue hasta abajo
                        ft.Container(height=20),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ])

    def go_back(self, e):
        from src.screens.ajustes_screen import AjustesScreen

        id_campus = self.page.client_storage.get("idCampus")
        id_carrera = self.page.client_storage.get("idCarrera")
        id_usuario = self.page.client_storage.get("idUsuario")

        self.page.clean()
        self.page.add(
            AjustesScreen(
                self.page,
                id_campus=id_campus,
                id_carrera=id_carrera,
                id_usuario=id_usuario
            )
        )