import flet as ft
from src.database.database import DatabaseHelper
from src.widgets.video_interaction_widget import VideoInteractionWidget
import uuid
import traceback # <--- AÑADIDO


class CommentsWidget(ft.Column):
    def __init__(self, page: ft.Page, video_id: str, id_usuario: str):
        print("--- DEBUG: CommentsWidget.__init__() - INICIANDO ---")
        try:
            super().__init__(expand=True)
            self.page = page
            self.video_id = video_id
            self.id_usuario = id_usuario
            self.db_helper = DatabaseHelper()
            print(f"--- DEBUG: CommentsWidget para video_id='{video_id}', usuario='{id_usuario}'")

            # --- UI Controls ---
            self.comments_list_view = ft.ListView(
                expand=True,
                spacing=10,
                padding=16,
                auto_scroll=False  # Evitar scroll automático al cargar
            )

            self.comment_input = ft.TextField(
                hint_text="Escribe un comentario...",
                border=ft.InputBorder.OUTLINE,
                border_radius=8,
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                expand=True,
                on_submit=self._add_comment  # Permitir enviar con Enter
            )

            # Área de contenido inicial
            self.content_area = ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Cargando comentarios...")
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                expand=True,
                alignment=ft.alignment.center
            )

            print("--- DEBUG: Creando VideoInteractionWidget...")
            interaction_widget = VideoInteractionWidget(
                page=self.page,
                video_id=self.video_id,
                id_usuario=self.id_usuario
            )
            print("--- DEBUG: VideoInteractionWidget creado.")

            # Configurar controles
            self.controls = [
                ft.Row([
                    ft.Text("Comentarios", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=self._close_bottom_sheet,
                        tooltip="Cerrar"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=12),
                interaction_widget,
                ft.Container(height=12),
                ft.Divider(height=1),
                ft.Container(
                    content=self.content_area,
                    expand=True
                ),
                ft.Divider(height=1),
                ft.Row(
                    controls=[
                        self.comment_input,
                        ft.ElevatedButton(
                            "Enviar",
                            on_click=self._add_comment,
                            bgcolor=ft.Colors.BLUE_900,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=16, vertical=14)
                            )
                        ),
                    ],
                    spacing=8
                ),
            ]

            print("--- DEBUG: CommentsWidget.__init__() - FINALIZADO CON ÉXITO ---")

        except Exception as e:
            print(f"\n\n¡¡¡ERROR en CommentsWidget.__init__!!!")
            print(f"Error: {e}")
            traceback.print_exc()

    def _close_bottom_sheet(self, e=None):
        """Cierra el BottomSheet"""
        if hasattr(self.page, 'bottom_sheet') and self.page.bottom_sheet:
            self.page.bottom_sheet.open = False
            self.page.update()

    def did_mount(self):
        print("--- DEBUG: CommentsWidget.did_mount() - INICIANDO ---")
        try:
            self._load_comments()
            print("--- DEBUG: CommentsWidget.did_mount() - FINALIZADO CON ÉXITO ---")
        except Exception as e:
            # --- ¡¡AQUÍ CAZAREMOS EL ERROR DEL DID_MOUNT!! ---
            print(f"\n\n¡¡¡ERROR CATASTRÓFICO EN CommentsWidget.did_mount!!!")
            print(f"Error: {e}")
            traceback.print_exc()
            self.content_area.content = ft.Text(f"Error al cargar: {e}")
            self.update()


    def _load_comments(self):
        """Carga los comentarios desde la BD y actualiza la lista."""
        print("--- DEBUG: CommentsWidget._load_comments: Obteniendo comentarios...")
        comments = self.db_helper.get_comments_by_id_video(self.video_id)
        print(f"--- DEBUG: CommentsWidget._load_comments: {len(comments)} encontrados.")

        self.comments_list_view.controls.clear()
        if not comments:
            self.content_area.content = ft.Container(
                content=ft.Text("No hay comentarios aún."),
                alignment=ft.alignment.center
            )
        else:
            for comment in comments:
                raw_date = comment.get('Fecha')
                date_str = "Fecha desconocida"
                if raw_date:
                    date_str = str(raw_date).split(' ')[0]

                self.comments_list_view.controls.append(
                    ft.Column(
                        [
                            ft.Text(comment['Comentario'], size=16, weight=ft.FontWeight.W_500),
                            ft.Text(date_str, size=12, color=ft.Colors.GREY),
                        ],
                        spacing=4
                    )
                )
            self.content_area.content = self.comments_list_view

        self.update()

    def _add_comment(self, e):
        """Guarda un nuevo comentario y refresca la lista."""
        comment_text = self.comment_input.value.strip()
        if not comment_text:
            return

        self.db_helper.add_comment(
            comment_id=str(uuid.uuid4()),
            video_id=self.video_id,
            user_id=self.id_usuario,
            comment_text=comment_text
        )

        self.comment_input.value = ""  # Limpiamos el campo de texto
        self._load_comments()  # Volvemos a cargar los comentarios