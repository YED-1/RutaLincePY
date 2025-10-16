import flet as ft
from database.database import DatabaseHelper
import random


class QuizWidget(ft.Column):
    def __init__(self, page: ft.Page, video_id: str):
        super().__init__(expand=True)
        self.page = page
        self.video_id = video_id
        self.db_helper = DatabaseHelper()

        # --- Estado del Quiz ---
        self.preguntas = []
        self.opciones_seleccionadas = {}
        self.quiz_enviado = False

        # --- Controles de UI ---
        self.questions_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.submit_button = ft.ElevatedButton(
            "Enviar", on_click=self._enviar_quiz, disabled=True
        )
        self.results_column = ft.Column(scroll=ft.ScrollMode.AUTO)

        self.content_area = ft.Container(
            content=ft.ProgressRing(),
            alignment=ft.alignment.center,
            expand=True
        )

        self.controls = [
            ft.Row(
                [
                    ft.Text("Quiz", size=24, weight=ft.FontWeight.BOLD),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.close_sheet)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            self.content_area
        ]

    def did_mount(self):
        self._cargar_preguntas()

    def _cargar_preguntas(self):
        preguntas_db = self.db_helper.get_preguntas_por_id_video(self.video_id)

        # Mezclamos las opciones para cada pregunta
        for p in preguntas_db:
            correcta = p['Opcion_Correcta']
            opciones = [p['Opcion_A'], p['Opcion_B'], correcta]
            random.shuffle(opciones)
            p['opciones_mezcladas'] = opciones
            p['_respuesta_correcta'] = correcta  # Guardamos la respuesta original

        self.preguntas = preguntas_db
        self._build_questions_view()
        self.update()

    def _build_questions_view(self):
        if not self.preguntas:
            self.content_area.content = ft.Text("No hay preguntas para este video.")
            return

        self.questions_column.controls.clear()
        for i, p in enumerate(self.preguntas):
            self.questions_column.controls.append(
                ft.Text(f"{i + 1}. {p['Pregunta']}", weight=ft.FontWeight.BOLD, size=18)
            )

            # Creamos los Radio buttons para las opciones
            opciones_radio = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value=opt, label=opt) for opt in p['opciones_mezcladas']
                ]),
                on_change=lambda e, index=i: self._on_option_selected(index, e.control.value)
            )
            self.questions_column.controls.append(opciones_radio)
            self.questions_column.controls.append(ft.Divider())

        self.content_area.content = ft.Column(
            [self.questions_column, self.submit_button],
            expand=True, scroll=ft.ScrollMode.AUTO
        )

    def _on_option_selected(self, question_index, selected_value):
        self.opciones_seleccionadas[question_index] = selected_value
        # Habilitar el botón de enviar si todas las preguntas han sido respondidas
        if len(self.opciones_seleccionadas) == len(self.preguntas):
            self.submit_button.disabled = False
        self.update()

    def _enviar_quiz(self, e):
        correctas = 0
        self.results_column.controls.clear()

        for i, p in enumerate(self.preguntas):
            seleccionada = self.opciones_seleccionadas.get(i)
            correcta = p['_respuesta_correcta']
            es_ok = seleccionada == correcta

            if es_ok: correctas += 1

            self.results_column.controls.append(
                ft.Container(
                    padding=8,
                    bgcolor=ft.Colors.GREEN_50 if es_ok else ft.Colors.RED_50,
                    border=ft.border.all(2, ft.Colors.GREEN if es_ok else ft.Colors.RED),
                    border_radius=8,
                    margin=ft.margin.symmetric(vertical=4),
                    content=ft.Column([
                        ft.Text(f"{i + 1}. {p['Pregunta']}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tu respuesta: {seleccionada}"),
                        ft.Text(f"Correcta: {correcta}"),
                    ])
                )
            )

        resultado_final = ft.Text(f"Obtuviste {correctas} de {len(self.preguntas)} correctas.", size=16,
                                  weight=ft.FontWeight.BOLD)
        self.results_column.controls.insert(0, resultado_final)

        self.content_area.content = self.results_column
        self.quiz_enviado = True
        self.update()

    def close_sheet(self, e):
        self.page.bottom_sheet.open = False
        self.page.update()