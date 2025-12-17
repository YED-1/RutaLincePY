import flet as ft
import flet_video as fv
import uuid
from src.database.database import DatabaseHelper
from src.widgets.comments_widget import CommentsWidget
import traceback


class InicioScreen(ft.Column):
    def __init__(self, page: ft.Page, id_carrera: str, id_campus: str):
        super().__init__(expand=True)
        print(f"\n--- DEBUG: Iniciando InicioScreen para id_carrera='{id_carrera}' ---")
        self.page = page
        self.id_carrera = id_carrera
        self.id_campus = id_campus

        self.db_helper = DatabaseHelper()
        self.id_usuario = None
        self.current_area_index = 0
        self.areas = []
        self.videos = []
        self.video_index = 0

        self.area_tabs = ft.Row(scroll=ft.ScrollMode.AUTO)

        # Placeholder inicial
        self.video_player = ft.Container(
            width=360,
            height=240,
            bgcolor=ft.Colors.BLACK,
            content=ft.ProgressRing()
        )

        self.video_title = ft.Text(size=26, weight=ft.FontWeight.BOLD)
        self.video_description = ft.Text(size=18, text_align=ft.TextAlign.JUSTIFY)

        self.comments_button = ft.IconButton(
            icon=ft.Icons.COMMENT_OUTLINED,
            tooltip="Ver comentarios y quiz",
        )

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
        print("--- DEBUG: InicioScreen.did_mount() ---")
        # Importación diferida para evitar ciclos circulares
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
        print("--- DEBUG: _save_user_data() ---")
        self.id_usuario = self._get_or_create_user_id()
        self.page.client_storage.set("idCampus", self.id_campus)
        self.page.client_storage.set("idCarrera", self.id_carrera)

        self.db_helper.insert_or_update_usuario(
            id_usuario=self.id_usuario,
            id_campus=self.id_campus,
            id_carrera=self.id_carrera
        )

    def _load_areas(self):
        print(f"--- DEBUG: _load_areas() para id_carrera='{self.id_carrera}' ---")
        self.areas = self.db_helper.get_areas_id_carrera(self.id_carrera)

        self.area_tabs.controls.clear()

        # Validar si hay áreas
        if not self.areas:
            print("--- DEBUG: No se encontraron áreas.")
            self.main_content.content = ft.Text("No se encontraron áreas para esta carrera.")
            self.update()
            return

        for i, area in enumerate(self.areas):
            # Usamos .get() por seguridad
            nombre_area = area.get('Nombre', 'Área sin nombre')
            self.area_tabs.controls.append(
                ft.GestureDetector(
                    on_tap=lambda e, index=i: self._on_area_tap(index),
                    content=ft.Container(
                        margin=ft.margin.only(right=12),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        bgcolor=ft.Colors.BLUE_900 if i == self.current_area_index else ft.Colors.BLUE_100,
                        border_radius=12,
                        content=ft.Text(
                            nombre_area,
                            color=ft.Colors.WHITE if i == self.current_area_index else ft.Colors.BLACK,
                        )
                    )
                )
            )
        self.update()
        self._load_videos()

    def _load_videos(self):
        if not self.areas: return

        # Aseguramos que el índice sea válido
        if self.current_area_index >= len(self.areas):
            self.current_area_index = 0

        area_id = self.areas[self.current_area_index].get('ID_Area')

        print(f"--- DEBUG: Buscando videos para id_area='{area_id}'")
        self.videos = self.db_helper.get_videos_by_id_area(area_id)

        if not self.videos:
            print("--- DEBUG: No hay videos para esta área.")
            self.main_content.content = ft.Text("No hay videos disponibles en esta área.")
            self.page.update()
            return

        self.video_index = 0
        self._initialize_video()

    def _initialize_video(self):
        self.main_content.content = self.video_view_column
        video_data = self.videos[self.video_index]
        video_id = video_data.get('ID_Video')  # .get() es más seguro

        # Obtener URL con manejo de errores
        video_url_raw = video_data.get('URL_Video')
        if not video_url_raw:
            video_url_raw = "video_placeholder"  # Evitar crash si es None

        # Lógica híbrida: Si empieza con http es web, si no es local
        if video_url_raw.startswith("http"):
            video_path = video_url_raw
        else:
            video_path = f"assets/videos/{video_url_raw}.mp4"

        print(f"--- DEBUG: Reproduciendo: '{video_path}' ---")

        # Configuración del reproductor
        media = [fv.VideoMedia(video_path)]
        new_video_player = fv.Video(
            playlist=media,
            autoplay=True,
            width=360,
            height=240,
            show_controls=True,
            on_completed=self._on_video_ended
        )

        self.video_player = new_video_player
        self.video_view_column.controls[0] = self.video_player

        # Actualizar textos UI
        self.video_title.value = video_data.get('Nombre', 'Sin Título')
        self.video_description.value = video_data.get('Descripción', 'Sin Descripción')
        self.comments_button.on_click = lambda _, vid=video_id: self._show_comments(vid)

        self.page.update()

    def _show_comments(self, video_id: str):
        print(f"--- DEBUG: _show_comments() para video_id='{video_id}' ---")
        try:
            if hasattr(self.page, 'bottom_sheet') and self.page.bottom_sheet is not None:
                self.page.bottom_sheet.open = False
                self.page.update()

            comments_widget = CommentsWidget(
                page=self.page,
                video_id=video_id,
                id_usuario=self.id_usuario
            )

            bottom_sheet = ft.BottomSheet(
                ft.Container(
                    content=comments_widget,
                    padding=15,
                    border_radius=ft.border_radius.vertical(top=20),
                    height=self.page.height * 0.85
                ),
                open=True,
                # Evitar referencia circular al cerrar
                on_dismiss=lambda _: None
            )

            self.page.overlay.append(bottom_sheet)
            self.page.bottom_sheet = bottom_sheet
            self.page.update()

        except Exception as e:
            print(f"ERROR en _show_comments: {e}")
            traceback.print_exc()

    def _on_area_tap(self, index):
        # Intentar pausar antes de cambiar
        if isinstance(self.video_player, fv.Video):
            try:
                self.video_player.pause()
            except:
                pass

        self.current_area_index = index
        self._load_areas()

    def _on_prev_video_click(self, e):
        if isinstance(self.video_player, fv.Video):
            try:
                self.video_player.pause()
            except:
                pass

        if self.video_index > 0:
            self.video_index -= 1
        else:
            self.video_index = len(self.videos) - 1
        self._initialize_video()

    def _on_next_video_click(self, e):
        if isinstance(self.video_player, fv.Video):
            try:
                self.video_player.pause()
            except:
                pass

        if self.video_index < len(self.videos) - 1:
            self.video_index += 1
        else:
            self.video_index = 0
        self._initialize_video()

    def _on_video_ended(self, e):
        print("--- DEBUG: Video terminado. ---")
        # Opcional: Auto-play siguiente video
        # self._on_next_video_click(e)