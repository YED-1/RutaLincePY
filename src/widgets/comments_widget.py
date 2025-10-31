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
            print("--- DEBUG: CommentsWidget.__init__() - db_helper creado.")

            # --- UI Controls ---
            self.comments_list_view = ft.ListView(expand=True, spacing=10, padding=16)
            self.comment_input = ft.TextField(
                hint_text="Escribe un comentario...",
                border=ft.InputBorder.OUTLINE,
                border_radius=8,
                content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
                expand=True
            )

            self.content_area = ft.Container(
                content=ft.Column(
                    [ft.ProgressRing(), ft.Text("Cargando comentarios...")],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                expand=True
            )
            print("--- DEBUG: CommentsWidget.__init__() - Controles base creados.")

            # --- POSIBLE PUNTO DE FALLO ---
            print("--- DEBUG: CommentsWidget.__init__() - Creando VideoInteractionWidget...")
            interaction_widget = VideoInteractionWidget(
                page=self.page,
                video_id=self.video_id,
                id_usuario=self.id_usuario
            )
            print("--- DEBUG: CommentsWidget.__init__() - VideoInteractionWidget CREADO.")
            # --- FIN POSIBLE PUNTO DE FALLO ---


            self.controls = [
                ft.Text("Comentarios", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=12),
                interaction_widget, # Usamos la variable
                ft.Container(height=12),
                ft.Divider(height=1),
                self.content_area,  # Área para la lista de comentarios
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
            # --- ¡¡AQUÍ CAZAREMOS EL ERROR DEL CONSTRUCTOR!! ---
            print(f"\n\n¡¡¡ERROR CATASTRÓFICO EN CommentsWidget.__init__!!!")
            print(f"Error: {e}")
            traceback.print_exc()


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