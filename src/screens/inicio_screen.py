import flet as ft
import uuid
from src.database.database import DatabaseHelper
from src.widgets.comments_widget import CommentsWidget


class InicioScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str):
        super().__init__(expand=True)
        # --- DEBUG PRINT 1: What ID did we receive? ---
        print(f"\n--- DEBUG: InicioScreen received id_carrera='{id_carrera}' ---")

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

        self.area_tabs = ft.Row(scroll=ft.ScrollMode.AUTO)
        self.video_player = ft.Video(
            expand=True,
            autoplay=True  # El video empezará solo cuando esté listo
        )
        self.video_player.on_position_changed = self._on_video_update

        self.video_title = ft.Text(size=26, weight=ft.FontWeight.BOLD)
        self.video_description = ft.Text(size=18, text_align=ft.TextAlign.JUSTIFY)

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
        from src.widgets.nav_bar_widget import create_nav_bar
        self._save_user_data()

        self.page.appbar = None
        self.page.navigation_bar = create_nav_bar(
            page=self.page, selected_index=0,
            id_carrera=self.id_carrera, id_campus=self.id_campus, id_usuario=self.id_usuario
        )
        self.page.update()  # Update to show NavBar immediately
        self._load_areas()  # Load data after NavBar is shown

    def _get_or_create_user_id(self):
        user_id = self.page.client_storage.get("idUsuario")
        if not user_id:
            user_id = str(uuid.uuid4())
            self.page.client_storage.set("idUsuario", user_id)
        return user_id

    def _save_user_data(self):
        self.id_usuario = self._get_or_create_user_id()
        self.page.client_storage.set("idCampus", self.id_campus)
        self.page.client_storage.set("idCarrera", self.id_carrera)

        self.db_helper.insert_or_update_usuario(
            id_usuario=self.id_usuario,
            id_campus=self.id_campus,
            id_carrera=self.id_carrera
        )

    def _load_areas(self):
        # --- DEBUG PRINT 2: Are we finding any Areas for this Career ID? ---
        print(f"--- DEBUG: Querying database for Areas with id_carrera='{self.id_carrera}' ---")
        self.areas = self.db_helper.get_areas_id_carrera(self.id_carrera)
        # --- DEBUG PRINT 3: Show the results of the Area query ---
        print(f"--- DEBUG: Found {len(self.areas)} Areas. Data: {self.areas} ---")

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
        # Update UI here to show tabs even if videos fail
        self.update()
        self._load_videos()

    def _load_videos(self):
        if not self.areas:
            print("--- DEBUG: No Areas found, stopping video load process. THIS IS LIKELY THE PROBLEM. ---")
            self.main_content.content = ft.Text("No hay áreas para esta carrera.")
            self.update()
            return

        area_id = self.areas[self.current_area_index]['ID_Area']
        # --- DEBUG PRINT 4: Are we finding any Videos for this Area ID? ---
        print(f"--- DEBUG: Querying database for Videos with id_area='{area_id}' ---")
        self.videos = self.db_helper.get_videos_by_id_area(area_id)
        # --- DEBUG PRINT 5: Show the results of the Video query ---
        print(f"--- DEBUG: Found {len(self.videos)} Videos. ---")

        self.video_index = 0
        self._initialize_video()

    def _initialize_video(self):
        if not self.videos:
            print("--- DEBUG: No Videos found for this area. Displaying error message. ---")
            self.main_content.content = ft.Text("No hay videos para esta área.")
            self.update()
            return

        print("--- DEBUG: Initializing video player... ---")
        self.has_counted_view = False
        video_data = self.videos[self.video_index]
        video_id = video_data['ID_Video']

        # Make sure the URL_Video exists and is not empty/None
        video_url = video_data.get('URL_Video')
        if not video_url:
            print(f"--- DEBUG ERROR: Video with ID '{video_id}' has an invalid URL_Video: {video_url} ---")
            self.main_content.content = ft.Text(f"Error: Video '{video_data.get('Nombre')}' tiene una URL inválida.")
            self.update()
            return

        # Ensure the video path is correctly formed
        video_path = f"/videos/{video_url}.mp4"
        print(f"--- DEBUG: Setting video source to: {video_path} ---")
        self.video_player.src = video_path

        self.video_title.value = video_data.get('Nombre', 'Sin Título')
        self.video_description.value = video_data.get('Descripción', 'Sin Descripción')

        comments_button = ft.IconButton(
            icon=ft.Icons.COMMENT_OUTLINED,
            tooltip="Ver comentarios y quiz",
            on_click=lambda e: self._show_comments(video_id)
        )

        video_view = ft.Column(
            [
                self.video_player,
                ft.Container(height=10),
                ft.Row([ft.Text(""), comments_button], alignment=ft.MainAxisAlignment.END),
                ft.Container(height=10),
                self.video_title,
                self.video_description,
                ft.Container(height=25),
                ft.ElevatedButton(
                    text="Siguiente Video" if self.video_index < len(self.videos) - 1 else "Volver al Inicio",
                    on_click=self._on_next_video_click,
                    bgcolor=ft.Colors.BLUE_900,
                    color=ft.Colors.WHITE,
                    width=250,
                    height=50
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.main_content.content = video_view
        # self.video_player.play() # No longer needed with autoplay=True
        self.update()
        print("--- DEBUG: Video player initialized and view updated. Autoplay enabled. ---")

    def _show_comments(self, video_id):
        print(f"--- DEBUG: Opening comments for video_id='{video_id}' ---")
        self.page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                content=CommentsWidget(
                    page=self.page,
                    video_id=video_id,
                    id_usuario=self.id_usuario
                ),
                padding=15,
                border_radius=ft.border_radius.vertical(top=20),
                height=self.page.window_height * 0.85
            )
        )
        self.page.bottom_sheet.open = True
        self.page.update()

    def _on_video_update(self, e):
        try:
            position_seconds = int(e.data) / 1000
            if not self.has_counted_view and position_seconds >= 5:
                self.has_counted_view = True
                video_id = self.videos[self.video_index]['ID_Video']
                self.db_helper.incrementar_visualizacion(video_id)
                print(f"--- DEBUG: Vista contada para el video {video_id} ---")
        except Exception as ex:
            print(f"--- DEBUG ERROR in _on_video_update: {ex} ---")

    def _on_area_tap(self, index):
        print(f"--- DEBUG: Area tab {index} tapped. ---")
        self.current_area_index = index
        # Reload areas to update tab colors, then load videos for the selected area
        self._load_areas()

    def _on_next_video_click(self, e):
        print("--- DEBUG: 'Next Video' button clicked. ---")
        self.video_player.pause()  # Pausamos el video actual antes de cargar el siguiente
        if self.video_index < len(self.videos) - 1:
            self.video_index += 1
        else:
            self.video_index = 0
        self._initialize_video()