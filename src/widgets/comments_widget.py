import flet as ft
from src.database.database import DatabaseHelper
from src.widgets.video_interaction_widget import VideoInteractionWidget
import uuid
import traceback  # Importamos traceback


class CommentsWidget(ft.Column):
    def __init__(self, page: ft.Page, video_id: str, id_usuario: str):
        super().__init__(expand=True)
        self.page = page
        self.video_id = video_id
        self.id_usuario = id_usuario
        self.db_helper = DatabaseHelper()

        # --- UI Controls ---
        self.comments_list_view = ft.ListView(expand=True, spacing=10, padding=16)
        self.comment_input = ft.TextField(
            hint_text="Escribe un comentario...",
            border=ft.InputBorder.OUTLINE,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
            expand=True
        )

        # This container will hold the loading indicator or the list of comments
        self.content_area = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(), ft.Text("Cargando comentarios...")],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            expand=True
        )

        self.controls = [
            ft.Text("Comentarios", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            # Incluimos el widget de interacciones (Likes, Dislikes, etc.)
            VideoInteractionWidget(page=self.page, video_id=self.video_id, id_usuario=self.id_usuario),
            ft.Container(height=12),
            ft.Divider(height=1),
            self.content_area,  # Área para la lista de comentarios
            ft.Divider(height=1),
            # Fila para añadir un nuevo comentario
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

    # --- FUNCIÓN MODIFICADA CON TRY...EXCEPT ---
    def did_mount(self):
        try:
            print("--- DEBUG: CommentsWidget did_mount. Cargando comentarios... ---")
            self._load_comments()
            print("--- DEBUG: CommentsWidget _load_comments() terminó. ---")
        except Exception as e:
            # --- ¡¡AQUÍ CAZAREMOS EL ERROR!! ---
            print(f"\n\n¡¡¡ERROR CATASTRÓFICO EN CommentsWidget.did_mount!!!")
            print(f"Error: {e}")
            traceback.print_exc()
            # Mostramos el error en la UI
            self.content_area.content = ft.Text(f"Error al cargar comentarios: {e}")
            self.update()

    def _load_comments(self):
        """Carga los comentarios desde la BD y actualiza la lista."""
        print("--- DEBUG: CommentsWidget._load_comments: Obteniendo comentarios de la BD...")
        comments = self.db_helper.get_comments_by_id_video(self.video_id)
        print(f"--- DEBUG: CommentsWidget._load_comments: {len(comments)} comentarios encontrados.")

        self.comments_list_view.controls.clear()
        if not comments:
            self.content_area.content = ft.Container(
                content=ft.Text("No hay comentarios aún."),
                alignment=ft.alignment.center
            )
        else:
            for i, comment in enumerate(comments):
                print(f"--- DEBUG: Procesando comentario {i}, Data: {comment}")
                # --- CORRECCIÓN ANTERIOR (DEJADA POR SEGURIDAD) ---
                raw_date = comment.get('Fecha')
                date_str = "Fecha desconocida"

                if raw_date:
                    date_str = str(raw_date).split(' ')[0]  # Convertimos a str por si acaso
                # --- FIN CORRECCIÓN ---

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

        print("--- DEBUG: CommentsWidget._load_comments: UI actualizada.")
        self.update()

    def _add_comment(self, e):
        """Guarda un nuevo comentario y refresca la lista."""
        comment_text = self.comment_input.value.strip()
        if not comment_text:
            return

        print("--- DEBUG: CommentsWidget._add_comment: Añadiendo comentario a la BD...")
        self.db_helper.add_comment(
            comment_id=str(uuid.uuid4()),
            video_id=self.video_id,
            user_id=self.id_usuario,
            comment_text=comment_text
        )
        print("--- DEBUG: CommentsWidget._add_comment: Comentario añadido.")

        self.comment_input.value = ""  # Limpiamos el campo de texto
        self._load_comments()  # Volvemos a cargar los comentarios