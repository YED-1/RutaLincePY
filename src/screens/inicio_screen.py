import flet as ft
import uuid
from database.database import DatabaseHelper
from src.widgets.nav_bar_widget import create_nav_bar



class InicioScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str):
        super().__init__(expand=True)
        self.page = page
        self.id_carrera = id_carrera
        self.id_campus = id_campus

        self.db_helper = DatabaseHelper()
        self.id_usuario = None
        self.current_area_index = 0
        self.areas = []
        self.videos = []
        self.video_index = 0
        self.has_counted_view = False

        # --- Controles de la UI ---
        self.area_tabs = ft.Row(scroll=ft.ScrollMode.AUTO)
        self.video_player = ft.Video(
            expand=True,
            #on_position_changed=self._on_video_update,  # Para contar visualizaciones
        )
        self.video_player.on_position_changed = self._on_video_update

        self.video_title = ft.Text(size=26, weight=ft.FontWeight.BOLD)
        self.video_description = ft.Text(size=18, text_align=ft.TextAlign.JUSTIFY)

        # Contenedor para la vista principal (video o indicador de carga)
        self.main_content = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Cargando...")],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            expand=True
        )

        self.controls = [
            self.area_tabs,
            ft.Container(height=30),
            self.main_content
        ]

    def did_mount(self):
        self.page.appbar = None

        # 2. CREAMOS Y ASIGNAMOS LA BARRA DE NAVEGACIÓN A LA PÁGINA
        self.page.navigation_bar = create_nav_bar(
            page=self.page,
            selected_index=0,  # 0 porque estamos en la pantalla de "Inicio"
            id_carrera=self.id_carrera,
            id_campus=self.id_campus,
            id_usuario=self.id_usuario  # Asegúrate de que _save_user_data se llame antes
        )

        self._initialize_screen()  # Esto carga los datos del video, etc.
        self.page.update()

    def _initialize_screen(self):
        """Método principal para cargar todo en orden."""
        self._save_user_data() # Importante que esto asigne self.id_usuario
        self._load_areas()

    def _get_or_create_user_id(self):
        user_id = self.page.client_storage.get("idUsuario")
        if not user_id:
            user_id = str(uuid.uuid4())
            self.page.client_storage.set("idUsuario", user_id)
        return user_id

    def _save_user_data(self):
        self.id_usuario = self._get_or_create_user_id()
        self.db_helper.insert_or_update_usuario(
            id_usuario=self.id_usuario,
            id_campus=self.id_campus,
            id_carrera=self.id_carrera
        )

    def _load_areas(self):
        self.areas = self.db_helper.get_areas_id_carrera(self.id_carrera)
        self.area_tabs.controls.clear()
        for i, area in enumerate(self.areas):
            self.area_tabs.controls.append(
                ft.GestureDetector(
                    on_tap=lambda e, index=i: self._on_area_tap(index),
                    content=ft.Container(
                        margin=ft.margin.only(right=12),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        bgcolor=ft.Colors.BLUE_900 if i == self.current_area_index else ft.Colors.BLUE_100,
                        border_radius=12,
                        content=ft.Text(
                            area['Nombre'],
                            color=ft.Colors.WHITE if i == self.current_area_index else ft.Colors.BLACK,
                        )
                    )
                )
            )
        self._load_videos()

    def _load_videos(self):
        if not self.areas:
            self.main_content.content = ft.Text("No hay áreas para esta carrera.")
            return

        area_id = self.areas[self.current_area_index]['ID_Area']
        self.videos = self.db_helper.get_videos_by_id_area(area_id)
        self.video_index = 0
        self._initialize_video()

    def _initialize_video(self):
        if not self.videos:
            self.main_content.content = ft.Text("No hay videos para esta área.")
            return

        self.has_counted_view = False
        video_data = self.videos[self.video_index]

        # Asumiendo que tus videos están en assets/videos/
        video_url = video_data['URL_Video']
        self.video_player.src = f"/videos/{video_url}.mp4"

        self.video_title.value = video_data['Nombre']
        self.video_description.value = video_data['Descripción']

        # Construimos la vista del video
        video_view = ft.Column(
            [
                ft.Stack([
                    self.video_player,
                    # Aquí podrías añadir un icono de Play/Pause si lo deseas
                ]),
                ft.Container(height=10),
                self.video_title,
                self.video_description,
                ft.Container(height=25),
                ft.ElevatedButton(
                    text="Siguiente Video" if self.video_index < len(self.videos) - 1 else "Volver al Inicio",
                    on_click=self._on_next_video_click,
                    bgcolor=ft.Colors.BLUE_900,
                    color=ft.Colors.WHITE
                )
            ]
        )
        self.main_content.content = video_view
        self.video_player.play()
        self.update()

    def _on_video_update(self, e):
        # El evento da la posición en milisegundos
        position_seconds = int(e.data) / 1000
        if not self.has_counted_view and position_seconds >= 5:
            self.has_counted_view = True
            video_id = self.videos[self.video_index]['ID_Video']
            self.db_helper.incrementar_visualizacion(video_id)
            print(f"Vista contada para el video {video_id}")

    def _on_area_tap(self, index):
        self.current_area_index = index
        # Re-renderizamos los tabs para el efecto de selección
        self._load_areas()

    def _on_next_video_click(self, e):
        if self.video_index < len(self.videos) - 1:
            self.video_index += 1
        else:
            self.video_index = 0
        self._initialize_video()