import flet as ft
import uuid
from src.database.database import DatabaseHelper
from src.widgets.comments_widget import CommentsWidget
import traceback  # Importamos traceback


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

        # --- INICIO DE REFACTORIZACIÓN ---
        # 1. Definimos TODOS los controles de la vista de video como atributos de clase

        # Video (Solución 1: Controles de diagnóstico)
        self.video_player = ft.Video(
            autoplay=True,  # Dejamos autoplay=True por si acaso
            width=360,
            height=240,
            show_controls=True
        )
        self.video_player.on_ended = self._on_video_ended
        self.video_player.on_position_changed = self._on_video_update

        # Título y Descripción
        self.video_title = ft.Text(size=26, weight=ft.FontWeight.BOLD)
        self.video_description = ft.Text(size=18, text_align=ft.TextAlign.JUSTIFY)

        # Botón de Comentarios (Solución 3)
        self.comments_button = ft.IconButton(
            icon=ft.Icons.COMMENT_OUTLINED,
            tooltip="Ver comentarios y quiz",
            # El on_click se asignará dinámicamente en _initialize_video
        )

        # Botones de Navegación (Solución 2)
        self.prev_button = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
            on_click=self._on_prev_video_click,
            icon_size=40,
            tooltip="Video Anterior",
        )
        self.next_button = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT_ROUNDED,
            on_click=self._on_next_video_click,
            icon_size=40,
            tooltip="Siguiente Video"
        )
        self.navigation_buttons = ft.Row(
            [self.prev_button, self.next_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50
        )

        # 2. Creamos la Columna de la vista de video UNA SOLA VEZ
        self.video_view_column = ft.Column(
            [
                self.video_player,
                ft.Container(height=10),
                ft.Row([ft.Text(""), self.comments_button], alignment=ft.MainAxisAlignment.END),
                ft.Container(height=10),
                self.video_title,
                self.video_description,
                ft.Container(height=25),
                self.navigation_buttons
            ],
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # 3. El main_content empieza con "Cargando..."
        self.main_content = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Cargando...")],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            ),
            expand=True
        )
        # --- FIN DE REFACTORIZACIÓN ---

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
        self.page.update()
        self._load_areas()

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
        print(f"--- DEBUG: Querying database for Areas with id_carrera='{self.id_carrera}' ---")
        self.areas = self.db_helper.get_areas_id_carrera(self.id_carrera)
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
        self.update()
        self._load_videos()

    def _load_videos(self):
        if not self.areas:
            print("--- DEBUG: No Areas found, stopping video load process. THIS IS LIKELY THE PROBLEM. ---")
            self.main_content.content = ft.Text("No hay áreas para esta carrera.")
            self.main_content.update()  # <-- Actualización específica
            return

        area_id = self.areas[self.current_area_index]['ID_Area']
        print(f"--- DEBUG: Querying database for Videos with id_area='{area_id}' ---")
        self.videos = self.db_helper.get_videos_by_id_area(area_id)
        print(f"--- DEBUG: Found {len(self.videos)} Videos. ---")

        self.video_index = 0
        self._initialize_video()

    # --- FUNCIÓN MODIFICADA CON LA CORRECCIÓN ---
    def _initialize_video(self):
        if not self.videos:
            print("--- DEBUG: No Videos found for this area. Displaying error message. ---")
            self.main_content.content = ft.Text("No hay videos para esta área.")
            self.main_content.update()
            return

        self.main_content.content = self.video_view_column
        self.has_counted_view = False
        video_data = self.videos[self.video_index]
        video_id = video_data['ID_Video']

        try:
            video_url_raw = video_data.get('URL_Video')
            if not isinstance(video_url_raw, str) or not video_url_raw:
                print(f"--- DEBUG ERROR: Video ID '{video_id}' tiene URL inválida: '{video_url_raw}' ---")
                self.main_content.content = ft.Text(f"Error: URL de video inválida.")
                self.main_content.update()
                return

            video_url = video_url_raw.strip()

            # (Tu lógica de CSV parece tener solo el nombre base, ej: 'Video1')
            video_path = f"/videos/{video_url}"
            if not video_url.endswith('.mp4'):
                video_path = f"/videos/{video_url}.mp4"

            print(f"Ruta final asignada a video_player.src: '{video_path}'")

            self.video_player.src = video_path

            self.video_title.value = video_data.get('Nombre', 'Sin Título')
            self.video_description.value = video_data.get('Descripción', 'Sin Descripción')
            self.comments_button.on_click = lambda _, video_id=video_id: self._show_comments(video_id)

            # --- INICIO DE LA CORRECCIÓN ---
            print(f"--- DEBUG: Actualizando main_content (para 'montar' el video) ---")
            self.main_content.update()  # <-- FORZAMOS LA ACTUALIZACIÓN AQUÍ
            print(f"--- DEBUG: main_content actualizado.")
            # --- FIN DE LA CORRECCIÓN ---

            print(f"--- DEBUG: Intentando video_player.play()... ---")
            self.video_player.play()  # <-- AHORA ESTA LÍNEA DEBERÍA FUNCIONAR
            print(f"--- DEBUG: .play() llamado sin error. ---")

            # self.main_content.update() # <-- Ya no es necesario aquí

        except Exception as e:
            # --- ¡¡AQUÍ CAZAREMOS EL ERROR!! ---
            print(f"\n\n¡¡¡ERROR CATASTRÓFICO EN _initialize_video!!!")
            print(f"Error: {e}")
            traceback.print_exc()
            # Mostramos el error en la UI también
            self.main_content.content = ft.Text(f"Error al cargar video: {e}")
            self.main_content.update()

    # --- FUNCIÓN MODIFICADA CON TRY...EXCEPT (LA DEJAMOS ASÍ POR AHORA) ---
    def _show_comments(self, video_id: str):
        print(f"--- DEBUG: Intentando abrir comments para video_id='{video_id}' ---")
        try:
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
            print(f"--- DEBUG: BottomSheet de comentarios abierto. ---")

        except Exception as e:
            # --- ¡¡AQUÍ CAZAREMOS EL ERROR!! ---
            print(f"\n\n¡¡¡ERROR CATASTRÓFICO EN _show_comments!!!")
            print(f"Error al *crear* CommentsWidget: {e}")
            traceback.print_exc()

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

    # (La lógica de estos botones ya estaba bien)
    def _on_prev_video_click(self, e):
        print("--- DEBUG: 'Previous Video' button clicked. ---")
        self.video_player.pause()
        if self.video_index > 0:
            self.video_index -= 1
        else:
            self.video_index = len(self.videos) - 1
        self._initialize_video()

    def _on_next_video_click(self, e):
        print("--- DEBUG: 'Next Video' button clicked. ---")
        self.video_player.pause()
        if self.video_index < len(self.videos) - 1:
            self.video_index += 1
        else:
            self.video_index = 0
        self._initialize_video()

    def _on_video_ended(self, e):
        print("--- DEBUG: Video terminado. Cargando el siguiente. ---")
        self._on_next_video_click(e)