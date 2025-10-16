import flet as ft
from src.database.database import DatabaseHelper
import random
import uuid
import datetime
import time


class PreguntasScreen(ft.Column):
    def __init__(self, page: ft.Page, id_area: str, longitud: int, id_usuario: str, id_simulador: str):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        self.page = page
        self.id_area = id_area
        self.longitud = longitud
        self.id_usuario = id_usuario
        self.id_simulador = id_simulador

        self.db_helper = DatabaseHelper()
        self.preguntas = []
        self.opciones_seleccionadas = {}
        self.inicio_tiempo = time.time()  # Capturamos el tiempo de inicio

        # --- UI Controls ---
        self.loading_view = ft.Column(
            [ft.ProgressRing(), ft.Text("Cargando preguntas...")],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        self.submit_button = ft.ElevatedButton(
            "Enviar", on_click=self._mostrar_resultado_popup, disabled=True
        )

        # El contenido principal de la pantalla
        self.controls = [self.loading_view]

    def did_mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Simulador"))
        self.page.update()
        self._cargar_preguntas_aleatorias()

    def _cargar_preguntas_aleatorias(self):
        todas_preguntas = self.db_helper.get_preguntas_por_id_area_activo(self.id_area)
        random.shuffle(todas_preguntas)

        preguntas_limitadas = todas_preguntas[:self.longitud]

        ids_temas = list({p['ID_Tema'] for p in preguntas_limitadas})
        nombres_temas = self.db_helper.get_nombres_temas_por_ids(ids_temas)

        for p in preguntas_limitadas:
            correcta_texto = p['Opcion_Correcta']
            opciones = [p['Opcion_A'], p['Opcion_B'], correcta_texto]
            random.shuffle(opciones)
            p['opciones_mezcladas'] = opciones
            p['_respuesta_correcta_texto'] = correcta_texto
            p['Nombre_Tema'] = nombres_temas.get(p['ID_Tema'], 'Desconocido')

        self.preguntas = preguntas_limitadas
        self._build_quiz_view()

    def _build_quiz_view(self):
        if not self.preguntas:
            self.controls.clear()
            self.controls.append(
                ft.Text("No hay preguntas disponibles para esta área.", text_align=ft.TextAlign.CENTER))
            self.update()
            return

        question_widgets = []
        for i, p in enumerate(self.preguntas):
            question_widgets.append(ft.Text(f"{i + 1}. {p['Pregunta']}", weight=ft.FontWeight.BOLD, size=18))
            question_widgets.append(ft.Text(f"Tema: {p['Nombre_Tema']}", size=14, color=ft.Colors.GREY))

            opciones_radio = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value=opt, label=opt) for opt in p['opciones_mezcladas']
                ]),
                on_change=lambda e, index=i: self._on_option_selected(index, e.control.value)
            )
            question_widgets.append(opciones_radio)
            question_widgets.append(ft.Container(height=20))

        self.controls.clear()
        self.controls.extend(question_widgets)
        self.controls.append(self.submit_button)
        self.update()

    def _on_option_selected(self, question_index, selected_value):
        self.opciones_seleccionadas[question_index] = selected_value
        if len(self.opciones_seleccionadas) == len(self.preguntas):
            self.submit_button.disabled = False
        self.update()

    def _mostrar_resultado_popup(self, e):
        fin_tiempo = time.time()
        tiempo_total = int(fin_tiempo - self.inicio_tiempo)

        correctas = 0
        detalles_respuestas = []
        aciertos_por_tema = {}
        total_por_tema = {}

        for i, p in enumerate(self.preguntas):
            seleccion = self.opciones_seleccionadas.get(i)
            es_correcta = seleccion == p['_respuesta_correcta_texto']

            if es_correcta: correctas += 1

            id_tema = p['ID_Tema']
            total_por_tema[id_tema] = total_por_tema.get(id_tema, 0) + 1
            if es_correcta:
                aciertos_por_tema[id_tema] = aciertos_por_tema.get(id_tema, 0) + 1

            detalles_respuestas.append(
                ft.Container(
                    padding=8, margin=ft.margin.symmetric(vertical=4),
                    bgcolor=ft.Colors.GREEN_50 if es_correcta else ft.Colors.RED_50,
                    border=ft.border.all(2, ft.Colors.GREEN if es_correcta else ft.Colors.RED),
                    border_radius=8,
                    content=ft.Column([
                        ft.Text(f"{i + 1}. {p['Pregunta']}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Tu respuesta: {seleccion}"),
                    ])
                )
            )

        # Guardar resultados en la base de datos
        fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for id_tema, total in total_por_tema.items():
            aciertos = aciertos_por_tema.get(id_tema, 0)
            porcentaje = (aciertos / total) * 100
            self.db_helper.guardar_calificacion_por_tema(
                id_usuario=self.id_usuario, id_tema=id_tema, calificacion=porcentaje,
                id_simulador=self.id_simulador, tiempo=tiempo_total,
                id_resultado=str(uuid.uuid4()), fecha=fecha_actual
            )

        # Construir el contenido del BottomSheet
        porcentaje_total = (correctas / len(self.preguntas)) * 100

        # ... (Aquí iría la lógica para el icono y color del resultado)

        def close_and_go_back(e):
            from src.screens.simulador_screen import SimuladorScreen  # Importación local
            self.page.bottom_sheet.open = False
            self.page.clean()
            # Asumimos que los datos necesarios están en client_storage
            id_carrera = self.page.client_storage.get("idCarrera")
            id_campus = self.page.client_storage.get("idCampus")
            id_usuario = self.page.client_storage.get("idUsuario")
            self.page.add(SimuladorScreen(self.page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))

        self.page.bottom_sheet = ft.BottomSheet(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(f"Obtuviste {correctas} de {len(self.preguntas)} correctas.", size=18,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.Text("Resumen de respuestas:", weight=ft.FontWeight.BOLD),
                    ft.Column(controls=detalles_respuestas, scroll=ft.ScrollMode.AUTO, expand=True),
                    ft.ElevatedButton("Cerrar", on_click=close_and_go_back)
                ], expand=True)
            )
        )
        self.page.bottom_sheet.open = True
        self.page.update()