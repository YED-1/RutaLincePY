import flet as ft


class CreditosScreen(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
        self.page = page

        # Configuración de la página para esta vista
        self.page.appbar = ft.AppBar(title=ft.Text("Créditos del Proyecto"))
        self.page.navigation_bar = None  # Ocultamos la barra de navegación principal
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

        self.controls = [
            ft.Container(
                padding=ft.padding.only(top=10, bottom=20, left=20, right=20),
                content=ft.Column(
                    controls=[
                        # Introducción
                        ft.Text(
                            'Este proyecto se realiza dentro del programa de Servicio Social de la Dirección Nacional de Programas de Ingenierías',
                            size=16,
                            text_align=ft.TextAlign.JUSTIFY,
                        ),
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

                        # Desarrolladores
                        ft.Text(
                            'Desarrolladores:',
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        create_person_tile(name='Aguilar Cabrera Donovan Yosef'),
                        create_person_tile(name='Ayala Rayón Omar'),
                        create_person_tile(name='Baeza Bernardes Aiker'), # Pendiente
                        create_person_tile(name='Jiménez Alvear Joshua Yedreick'),
                        create_person_tile(name='Luna Ocampo Alejandro'),
                        create_person_tile(name='Márquez González Adrián Aleksei'), #Pendiente
                        create_person_tile(name='Quiroz Mora Raúl Alejandro'), #Parte IOS
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
                            'Universidad del Valle de México',
                            size=15,
                            italic=True,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton("Volver a Ajustes", on_click=self.go_back, width=200)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]

    def go_back(self, e):
        # Función para regresar a la pantalla de Ajustes, recuperando los datos
        from src.screens.ajustes_screen import AjustesScreen  # Importación local para evitar ciclos

        # Recuperamos los IDs guardados para reconstruir la pantalla de Ajustes
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