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
            "Enviar Respuestas",
            on_click=self._mostrar_resultado_popup,
            disabled=True,
            icon=ft.Icons.SEND,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_900,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=30, vertical=15)
            )
        )

        self.controls = [self.loading_view]

    def did_mount(self):
        print(f"--- DEBUG (Preguntas): Iniciando con id_area='{self.id_area}', longitud={self.longitud} ---")
        self.page.appbar = ft.AppBar(
            title=ft.Text("Simulador"),
            bgcolor=ft.Colors.BLUE_900,
            color=ft.Colors.WHITE
        )
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

            # Obtener nombres de temas
            nombres_temas = {}
            try:
                nombres_temas = self.db_helper.get_nombres_temas_por_ids(ids_temas)
                print(f"--- DEBUG (Preguntas): Nombres de temas obtenidos: {nombres_temas} ---")
            except Exception as e:
                print(f"--- DEBUG (Preguntas): Falló get_nombres_temas_por_ids, usando alternativa: {e} ---")
                for id_tema in ids_temas:
                    tema = self.db_helper.get_tema_by_id(id_tema)
                    if tema:
                        nombres_temas[id_tema] = tema.get('Nombre', f'Tema {id_tema}')
                    else:
                        nombres_temas[id_tema] = f'Tema {id_tema}'

            # Preparar preguntas
            for p in preguntas_limitadas:
                correcta_texto = p['Opcion_Correcta']

                # Crear lista de opciones (solo incluir opciones no vacías)
                opciones = [p['Opcion_A'], p['Opcion_B'], correcta_texto]

                # Solo agregar Opcion_C si existe y no está vacía
                if 'Opcion_C' in p and p['Opcion_C'] and p['Opcion_C'].strip():
                    opciones.append(p['Opcion_C'])

                # Eliminar duplicados y mezclar
                opciones = list(set(opciones))
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
                        "Volver al Simulador",
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

            # Header informativo
            question_widgets.append(
                ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20),
                    content=ft.Column([
                        ft.Text(f"Simulador: {self.id_simulador}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Total de preguntas: {len(self.preguntas)}", size=14),
                        ft.Text("Responde todas las preguntas para poder enviar", size=12, color=ft.Colors.GREY_600),
                    ])
                )
            )

            for i, p in enumerate(self.preguntas):
                # Título de la pregunta
                question_widgets.append(
                    ft.Container(
                        padding=15,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        margin=ft.margin.only(bottom=15),
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    width=30,
                                    height=30,
                                    border_radius=15,
                                    bgcolor=ft.Colors.BLUE_900,
                                    alignment=ft.alignment.center,
                                    content=ft.Text(f"{i + 1}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                ),
                                ft.Text(f"{p['Pregunta']}",
                                        weight=ft.FontWeight.BOLD, size=16, expand=True),
                            ]),
                            ft.Container(
                                padding=ft.padding.only(left=35),
                                content=ft.Text(f"Tema: {p['Nombre_Tema']}",
                                                size=14, color=ft.Colors.GREY_600),
                            ),
                        ])
                    )
                )

                # Opciones de respuesta
                opciones_radio = ft.RadioGroup(
                    content=ft.Column([
                        ft.Container(
                            margin=ft.margin.only(bottom=8),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            border_radius=6,
                            content=ft.Radio(
                                value=opt,
                                label=ft.Text(opt, size=14),
                                fill_color=ft.Colors.BLUE_900
                            )
                        ) for opt in p['opciones_mezcladas']
                    ], spacing=0),
                    on_change=lambda e, index=i: self._on_option_selected(index, e.control.value)
                )
                question_widgets.append(opciones_radio)
                question_widgets.append(ft.Divider(height=20, color=ft.Colors.TRANSPARENT))

            # Botón de enviar
            question_widgets.append(
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Divider(),
                        ft.Row([
                            ft.Text(
                                f"Progreso: {len(self.opciones_seleccionadas)}/{len(self.preguntas)} preguntas respondidas",
                                size=14,
                                color=ft.Colors.GREY_600
                            ),
                            self.submit_button
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
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
        self.submit_button.disabled = len(self.opciones_seleccionadas) < len(self.preguntas)
        self.update()

    def _obtener_comentario_por_opcion(self, pregunta, opcion_seleccionada):
        """Obtiene el comentario específico para la opción seleccionada"""
        # Mapear opciones a sus comentarios
        comentarios_map = {
            pregunta.get('Opcion_A', ''): pregunta.get('Comentario_A', ''),
            pregunta.get('Opcion_B', ''): pregunta.get('Comentario_B', ''),
            pregunta.get('Opcion_C', ''): pregunta.get('Comentario_C', ''),
            pregunta.get('Opcion_Correcta', ''): pregunta.get('Comentario_Correcta', '¡Respuesta correcta!')
        }

        return comentarios_map.get(opcion_seleccionada, '')

    def _mostrar_resultado_popup(self, e):
        try:
            print("--- DEBUG (Preguntas): Calculando resultados ---")
            fin_tiempo = time.time()
            tiempo_total = int(fin_tiempo - self.inicio_tiempo)

            correctas = 0
            detalles_respuestas = []
            aciertos_por_tema = {}
            total_por_tema = {}

            for i, p in enumerate(self.preguntas):
                seleccion = self.opciones_seleccionadas.get(i, "No respondida")
                es_correcta = seleccion == p['_respuesta_correcta_texto']

                if es_correcta:
                    correctas += 1

                id_tema = p['ID_Tema']
                total_por_tema[id_tema] = total_por_tema.get(id_tema, 0) + 1
                if es_correcta:
                    aciertos_por_tema[id_tema] = aciertos_por_tema.get(id_tema, 0) + 1

                # Obtener comentario basado en la opción seleccionada
                comentario_seleccion = self._obtener_comentario_por_opcion(p, seleccion)
                comentario_correcto = p.get('Comentario_Correcta', '¡Respuesta correcta!')

                # Detalle de cada respuesta con comentarios
                detalles_respuestas.append(
                    ft.Container(
                        padding=12,
                        margin=ft.margin.symmetric(vertical=4),
                        bgcolor=ft.Colors.GREEN_50 if es_correcta else ft.Colors.RED_50,
                        border=ft.border.all(2, ft.Colors.GREEN if es_correcta else ft.Colors.RED),
                        border_radius=8,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE if es_correcta else ft.Icons.CANCEL,
                                    color=ft.Colors.GREEN if es_correcta else ft.Colors.RED,
                                    size=20
                                ),
                                ft.Text(f"Pregunta {i + 1}", weight=ft.FontWeight.BOLD, size=14, expand=True),
                            ]),
                            ft.Text(f"Tu respuesta: {seleccion}", size=12, weight=ft.FontWeight.BOLD),

                            # Mostrar comentario específico de la opción seleccionada
                            ft.Container(
                                padding=ft.padding.only(left=10, top=5, bottom=5),
                                content=ft.Column([
                                    ft.Text("Retroalimentación:", size=12, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_700),
                                    ft.Text(
                                        comentario_seleccion if not es_correcta else comentario_correcto,
                                        size=11,
                                        color=ft.Colors.GREY_700
                                    )
                                ])
                            ) if comentario_seleccion or comentario_correcto else ft.Container(),

                            ft.Text(f"Respuesta correcta: {p['_respuesta_correcta_texto']}",
                                    size=12, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                        ], spacing=6)
                    )
                )

            # Guardar resultados en la base de datos
            print("--- DEBUG (Preguntas): Guardando resultados en BD ---")
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for id_tema, total in total_por_tema.items():
                aciertos = aciertos_por_tema.get(id_tema, 0)
                porcentaje = (aciertos / total) * 100 if total > 0 else 0

                print(f"--- DEBUG (Preguntas): Guardando tema {id_tema} - {aciertos}/{total} = {porcentaje:.1f}% ---")

                self.db_helper.guardar_calificacion_por_tema(
                    id_usuario=self.id_usuario,
                    id_tema=id_tema,
                    calificacion=porcentaje,
                    id_simulador=self.id_simulador,
                    tiempo=tiempo_total,
                    id_resultado=str(uuid.uuid4()),
                    fecha=fecha_actual
                )

            # Calcular porcentaje total
            porcentaje_total = (correctas / len(self.preguntas)) * 100

            # Determinar color según el resultado
            color_resultado = ft.Colors.GREEN if porcentaje_total >= 70 else ft.Colors.ORANGE if porcentaje_total >= 50 else ft.Colors.RED
            icono_resultado = ft.Icons.EMOJI_EVENTS if porcentaje_total >= 70 else ft.Icons.WARNING if porcentaje_total >= 50 else ft.Icons.SENTIMENT_DISSATISFIED

            print(
                f"--- DEBUG (Preguntas): Resultado final: {correctas}/{len(self.preguntas)} = {porcentaje_total:.1f}% ---")

            # Crear función para cerrar y volver
            def close_and_go_back(e):
                print("--- DEBUG (Preguntas): Cerrando resultados y volviendo al simulador ---")
                if hasattr(self.page, 'bottom_sheet') and self.page.bottom_sheet:
                    self.page.bottom_sheet.open = False
                    self.page.update()
                self._volver_a_simulador()

            # Crear el BottomSheet de resultados
            bottom_sheet_content = ft.BottomSheet(
                ft.Container(
                    padding=20,
                    height=600,
                    content=ft.Column([
                        # Header del resultado
                        ft.Container(
                            padding=20,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=12,
                            content=ft.Row([
                                ft.Icon(icono_resultado, color=color_resultado, size=32),
                                ft.Column([
                                    ft.Text(
                                        f"Resultado: {correctas}/{len(self.preguntas)}",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=color_resultado
                                    ),
                                    ft.Text(
                                        f"Calificación: {porcentaje_total:.1f}%",
                                        size=18,
                                        color=color_resultado
                                    ),
                                ], expand=True)
                            ])
                        ),

                        ft.Text(f"Tiempo total: {tiempo_total} segundos", size=14, color=ft.Colors.GREY_600),
                        ft.Divider(height=20),

                        # Detalle de respuestas
                        ft.Text("Detalle de respuestas:", weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(
                            content=ft.ListView(
                                controls=detalles_respuestas,
                                expand=True,
                                spacing=4
                            ),
                            height=300,
                        ),

                        # Botón de acción
                        ft.Container(
                            padding=ft.padding.only(top=20),
                            content=ft.ElevatedButton(
                                "Volver al Simulador",
                                on_click=close_and_go_back,
                                icon=ft.Icons.ARROW_BACK,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_900,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(horizontal=30, vertical=15)
                                )
                            )
                        )
                    ], scroll=ft.ScrollMode.ADAPTIVE)
                ),
                open=True,
                on_dismiss=lambda _: print("--- DEBUG (Preguntas): BottomSheet cerrado ---")
            )

            # Mostrar el BottomSheet
            self.page.overlay.append(bottom_sheet_content)
            self.page.bottom_sheet = bottom_sheet_content
            self.page.update()

            print("--- DEBUG (Preguntas): Resultados mostrados exitosamente ---")

        except Exception as ex:
            print(f"--- DEBUG (Preguntas): ERROR en _mostrar_resultado_popup: {ex} ---")
            traceback.print_exc()
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Error al mostrar resultados: {str(ex)}"),
                    bgcolor=ft.Colors.RED
                )
            )