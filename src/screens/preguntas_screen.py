import flet as ft
from src.database.database import DatabaseHelper
import random
import uuid
import datetime
import time
import traceback


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
        self.inicio_tiempo = time.time()

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

        self.controls = [self.loading_view]

    def did_mount(self):
        print(f"--- DEBUG (Preguntas): Iniciando con id_area='{self.id_area}', longitud={self.longitud} ---")
        self.page.appbar = ft.AppBar(title=ft.Text("Simulador"))
        self.page.update()
        self._cargar_preguntas_aleatorias()

    def _cargar_preguntas_aleatorias(self):
        try:
            print(f"--- DEBUG (Preguntas): Cargando preguntas para id_area='{self.id_area}' ---")
            todas_preguntas = self.db_helper.get_preguntas_por_id_area_activo(self.id_area)
            print(f"--- DEBUG (Preguntas): {len(todas_preguntas)} preguntas encontradas en total ---")

            if not todas_preguntas:
                self._mostrar_error("No hay preguntas disponibles para esta área.")
                return

            random.shuffle(todas_preguntas)
            preguntas_limitadas = todas_preguntas[:self.longitud]
            print(f"--- DEBUG (Preguntas): Seleccionadas {len(preguntas_limitadas)} preguntas ---")

            # Obtener IDs de temas únicos
            ids_temas = list({p['ID_Tema'] for p in preguntas_limitadas})
            print(f"--- DEBUG (Preguntas): IDs de temas encontrados: {ids_temas} ---")

            # SOLUCIÓN: Si no existe get_nombres_temas_por_ids, lo simulamos
            nombres_temas = {}
            try:
                nombres_temas = self.db_helper.get_nombres_temas_por_ids(ids_temas)
            except Exception as e:
                print(f"--- DEBUG (Preguntas): Falló get_nombres_temas_por_ids, usando alternativa: {e} ---")
                # Alternativa: obtener nombres uno por uno
                for id_tema in ids_temas:
                    tema = self.db_helper.get_tema_by_id(id_tema)
                    if tema:
                        nombres_temas[id_tema] = tema.get('Nombre', f'Tema {id_tema}')
                    else:
                        nombres_temas[id_tema] = f'Tema {id_tema}'

            # Preparar preguntas
            for p in preguntas_limitadas:
                correcta_texto = p['Opcion_Correcta']
                opciones = [p['Opcion_A'], p['Opcion_B'], correcta_texto]

                # Asegurarnos de que hay 3 opciones únicas
                if p['Opcion_C'] and p['Opcion_C'].strip():
                    opciones.append(p['Opcion_C'])

                random.shuffle(opciones)
                p['opciones_mezcladas'] = opciones
                p['_respuesta_correcta_texto'] = correcta_texto
                p['Nombre_Tema'] = nombres_temas.get(p['ID_Tema'], 'Desconocido')

            self.preguntas = preguntas_limitadas
            self._build_quiz_view()

        except Exception as e:
            print(f"--- DEBUG (Preguntas): ERROR en _cargar_preguntas_aleatorias: {e} ---")
            traceback.print_exc()
            self._mostrar_error(f"Error al cargar preguntas: {str(e)}")

    def _mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        self.controls.clear()
        self.controls.append(
            ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED),
                    ft.Text(mensaje, text_align=ft.TextAlign.CENTER, size=16),
                    ft.ElevatedButton(
                        "Volver",
                        on_click=self._volver_a_simulador,
                        icon=ft.Icons.ARROW_BACK
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        self.update()

    def _volver_a_simulador(self, e=None):
        """Vuelve a la pantalla de simulador"""
        from src.screens.simulador_screen import SimuladorScreen
        self.page.clean()
        id_carrera = self.page.client_storage.get("idCarrera")
        id_campus = self.page.client_storage.get("idCampus")
        id_usuario = self.page.client_storage.get("idUsuario")
        self.page.add(SimuladorScreen(self.page, id_carrera=id_carrera, id_campus=id_campus, id_usuario=id_usuario))

    def _build_quiz_view(self):
        try:
            if not self.preguntas:
                self._mostrar_error("No hay preguntas disponibles.")
                return

            print(f"--- DEBUG (Preguntas): Construyendo vista con {len(self.preguntas)} preguntas ---")

            question_widgets = []
            for i, p in enumerate(self.preguntas):
                # Título de la pregunta
                question_widgets.append(
                    ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(f"{i + 1}. {p['Pregunta']}",
                                    weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(f"Tema: {p['Nombre_Tema']}",
                                    size=14, color=ft.Colors.GREY),
                        ])
                    )
                )

                # Opciones de respuesta
                opciones_radio = ft.RadioGroup(
                    content=ft.Column([
                        ft.Radio(value=opt, label=ft.Text(opt)) for opt in p['opciones_mezcladas']
                    ], spacing=5),
                    on_change=lambda e, index=i: self._on_option_selected(index, e.control.value)
                )
                question_widgets.append(opciones_radio)
                question_widgets.append(ft.Divider(height=20, color=ft.Colors.TRANSPARENT))

            # Botón de enviar
            question_widgets.append(
                ft.Container(
                    padding=20,
                    content=ft.Row([
                        self.submit_button
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            )

            self.controls.clear()
            self.controls.extend(question_widgets)
            self.update()
            print("--- DEBUG (Preguntas): Vista construida exitosamente ---")

        except Exception as e:
            print(f"--- DEBUG (Preguntas): ERROR en _build_quiz_view: {e} ---")
            traceback.print_exc()
            self._mostrar_error(f"Error al construir el cuestionario: {str(e)}")

    def _on_option_selected(self, question_index, selected_value):
        self.opciones_seleccionadas[question_index] = selected_value
        # Habilitar botón si todas las preguntas tienen respuesta
        if len(self.opciones_seleccionadas) == len(self.preguntas):
            self.submit_button.disabled = False
        self.update()

    def _mostrar_resultado_popup(self, e):
        try:
            print("--- DEBUG (Preguntas): Mostrando resultados ---")
            fin_tiempo = time.time()
            tiempo_total = int(fin_tiempo - self.inicio_tiempo)

            correctas = 0
            detalles_respuestas = []
            aciertos_por_tema = {}
            total_por_tema = {}

            for i, p in enumerate(self.preguntas):
                seleccion = self.opciones_seleccionadas.get(i)
                es_correcta = seleccion == p['_respuesta_correcta_texto']

                if es_correcta:
                    correctas += 1

                id_tema = p['ID_Tema']
                total_por_tema[id_tema] = total_por_tema.get(id_tema, 0) + 1
                if es_correcta:
                    aciertos_por_tema[id_tema] = aciertos_por_tema.get(id_tema, 0) + 1

                detalles_respuestas.append(
                    ft.Container(
                        padding=8,
                        margin=ft.margin.symmetric(vertical=4),
                        bgcolor=ft.Colors.GREEN_50 if es_correcta else ft.Colors.RED_50,
                        border=ft.border.all(2, ft.Colors.GREEN if es_correcta else ft.Colors.RED),
                        border_radius=8,
                        content=ft.Column([
                            ft.Text(f"{i + 1}. {p['Pregunta']}", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"Tu respuesta: {seleccion or 'No respondida'}", size=12),
                            ft.Text(f"Respuesta correcta: {p['_respuesta_correcta_texto']}", size=12,
                                    color=ft.Colors.GREEN),
                        ], spacing=4)
                    )
                )

            # Guardar resultados
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for id_tema, total in total_por_tema.items():
                aciertos = aciertos_por_tema.get(id_tema, 0)
                porcentaje = (aciertos / total) * 100 if total > 0 else 0
                self.db_helper.guardar_calificacion_por_tema(
                    id_usuario=self.id_usuario,
                    id_tema=id_tema,
                    calificacion=porcentaje,
                    id_simulador=self.id_simulador,
                    tiempo=tiempo_total,
                    id_resultado=str(uuid.uuid4()),
                    fecha=fecha_actual
                )

            # Mostrar resultados
            porcentaje_total = (correctas / len(self.preguntas)) * 100

            def close_and_go_back(e):
                self.page.bottom_sheet.open = False
                self.page.update()
                self._volver_a_simulador()

            self.page.bottom_sheet = ft.BottomSheet(
                ft.Container(
                    padding=20,
                    height=600,
                    content=ft.Column([
                        ft.Text(
                            f"Resultado: {correctas}/{len(self.preguntas)} ({porcentaje_total:.1f}%)",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900
                        ),
                        ft.Text(f"Tiempo: {tiempo_total} segundos", size=14),
                        ft.Divider(height=20),
                        ft.Text("Detalle de respuestas:", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column(
                                controls=detalles_respuestas,
                                scroll=ft.ScrollMode.ADAPTIVE
                            ),
                            height=400,
                            expand=True
                        ),
                        ft.ElevatedButton("Volver al Simulador", on_click=close_and_go_back)
                    ])
                ),
                open=True
            )
            self.page.update()

        except Exception as ex:
            print(f"--- DEBUG (Preguntas): ERROR en _mostrar_resultado_popup: {ex} ---")
            traceback.print_exc()
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error al mostrar resultados: {str(ex)}")))