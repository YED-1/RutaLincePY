import flet as ft
from database.database import DatabaseHelper
from src.widgets.quiz_widget import QuizWidget
import uuid


class VideoInteractionWidget(ft.Row):
    def __init__(self, page: ft.Page, video_id: str, id_usuario: str):
        super().__init__(alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        self.page = page
        self.video_id = video_id
        self.id_usuario = id_usuario
        self.db_helper = DatabaseHelper()

        # --- Estado ---
        self.is_liked = False
        self.is_disliked = False
        self.video_data = None

        # --- Controles de UI ---
        self.like_count = ft.Text("0")
        self.dislike_count = ft.Text("0")
        self.views_count = ft.Text("0")

        # Creamos los "botones" como contenedores clickeables
        self.like_tile = self._create_icon_tile(
            icon=ft.Icons.THUMB_UP,
            count_text=self.like_count,
            on_click=lambda e: self._handle_reaction('Like')
        )
        self.dislike_tile = self._create_icon_tile(
            icon=ft.Icons.THUMB_DOWN,
            count_text=self.dislike_count,
            on_click=lambda e: self._handle_reaction('Dislike')
        )
        self.views_tile = self._create_icon_tile(
            icon=ft.Icons.REMOVE_RED_EYE,
            count_text=self.views_count
        )
        self.quiz_tile = self._create_icon_tile(
            icon=ft.Icons.DESCRIPTION,
            count_text=ft.Text("Quiz"),
            on_click=self._open_quiz_sheet
        )

        self.controls = [self.like_tile, self.dislike_tile, self.views_tile, self.quiz_tile]

    def did_mount(self):
        self._init_all()

    def _init_all(self):
        """Carga todos los datos iniciales y actualiza la UI."""
        self.video_data = self.db_helper.get_video_by_id(self.video_id)
        user_reaction = self.db_helper.get_user_reaction_for_video(self.video_id, self.id_usuario)

        if user_reaction:
            self.is_liked = user_reaction == 'Like'
            self.is_disliked = user_reaction == 'Dislike'
        else:
            self.is_liked = False
            self.is_disliked = False

        self._update_ui()

    def _handle_reaction(self, tipo: str):
        current_reaction = self.db_helper.get_user_reaction_for_video(self.video_id, self.id_usuario)
        field = 'Cantidad_Likes' if tipo == 'Like' else 'Cantidad_Dislikes'

        if current_reaction == tipo:
            # Si ya había una reacción igual, la borramos y decrementamos
            self.db_helper.delete_reaction(self.video_id, self.id_usuario)
            self.db_helper.update_video_counter(self.video_id, field, -1)
        else:
            # Si había reacción contraria, la borramos y decrementamos
            if current_reaction:
                prev_field = 'Cantidad_Likes' if current_reaction == 'Like' else 'Cantidad_Dislikes'
                self.db_helper.delete_reaction(self.video_id, self.id_usuario)
                self.db_helper.update_video_counter(self.video_id, prev_field, -1)

            # Insertamos la nueva reacción y actualizamos el contador
            self.db_helper.insert_reaction(str(uuid.uuid4()), self.video_id, self.id_usuario, tipo)
            self.db_helper.update_video_counter(self.video_id, field, 1)

        # Refrescamos los datos y la UI
        self._init_all()

    def _update_ui(self):
        """Actualiza la apariencia de los controles con los datos más recientes."""
        if self.video_data:
            self.like_count.value = str(self.video_data.get('Cantidad_Likes', 0))
            self.dislike_count.value = str(self.video_data.get('Cantidad_Dislikes', 0))
            self.views_count.value = str(self.video_data.get('Visualizaciones', 0))

            # Actualizar estilo de "Like"
            self.like_tile.bgcolor = ft.Colors.with_opacity(0.2,ft.Colors.GREEN) if self.is_liked else ft.Colors.GREY_200
            self.like_tile.border = ft.border.all(1, ft.Colors.GREEN) if self.is_liked else None
            self.like_tile.content.controls[0].color = ft.Colors.GREEN if self.is_liked else ft.Colors.BLACK54

            # Actualizar estilo de "Dislike"
            self.dislike_tile.bgcolor = ft.Colors.with_opacity(0.2,
                                                               ft.Colors.RED) if self.is_disliked else ft.Colors.GREY_200
            self.dislike_tile.border = ft.border.all(1, ft.Colors.RED) if self.is_disliked else None
            self.dislike_tile.content.controls[0].color = ft.Colors.RED if self.is_disliked else ft.Colors.BLACK54

        self.update()

    def _open_quiz_sheet(self, e):
        """Muestra el BottomSheet con el widget del quiz."""
        self.page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                content=QuizWidget(page=self.page, video_id=self.video_id),
                padding=15,
                height=self.page.window_height * 0.8  # Ocupa el 80% de la pantalla
            ),
            is_scroll_controlled=True,
            on_dismiss=lambda _: print("Quiz cerrado")
        )
        self.page.bottom_sheet.open = True
        self.page.update()

    def _create_icon_tile(self, icon, count_text, on_click=None):
        """Función helper para no repetir código al crear los botones."""
        return ft.Container(
            content=ft.Row([ft.Icon(icon), ft.Container(width=4), count_text]),
            margin=ft.margin.symmetric(horizontal=4),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=20,
            bgcolor=ft.Colors.GREY_200,
            on_click=on_click,
            ink=True
        )