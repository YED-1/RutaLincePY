import firebase_admin
from firebase_admin import credentials, firestore
import os
import random
import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Verificamos si ya está inicializado para evitar errores al recargar Flet
if not firebase_admin._apps:
    # Ajustamos la ruta para buscar credenciales.json en la misma carpeta que este archivo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(base_dir, "credenciales.json")

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        print(f"⚠️ ERROR: No se encontró el archivo {cred_path}")


class DatabaseHelper:
    def __init__(self, db_name=None):
        # db_name se mantiene por compatibilidad, pero no se usa en Firebase
        self.db = firestore.client()

    # ==========================================
    #      MÉTODOS DE LECTURA (GET)
    # ==========================================

    def get_campus(self):
        docs = self.db.collection('campus').where('estado', '==', 'Activo').stream()
        return [{"ID_Campus": doc.id, "Nombre": doc.to_dict().get('nombre')} for doc in docs]

    def get_carrera(self):
        docs = self.db.collection('carreras').stream()
        resultado = []
        for doc in docs:
            d = doc.to_dict()
            d['ID_Carrera'] = doc.id
            d['Nombre'] = d.get('nombre')  # Mapeo para Flet
            resultado.append(d)
        return resultado

    def get_nombres_carrera_por_id_campus(self, id_campus):
        # 1. Buscar en la colección intermedia
        docs = self.db.collection('carrera_campus').where('id_campus', '==', id_campus).stream()
        nombres = []
        for doc in docs:
            id_carrera = doc.to_dict().get('id_carrera')
            if id_carrera:
                carrera_doc = self.db.collection('carreras').document(id_carrera).get()
                if carrera_doc.exists:
                    nombres.append(carrera_doc.to_dict().get('nombre'))
        return nombres

    def get_areas_id_carrera(self, id_carrera):
        docs = self.db.collection('areas') \
            .where('id_carrera', '==', id_carrera) \
            .where('estado', '==', 'Activo').stream()
        return [{"ID_Area": doc.id, "Nombre": doc.to_dict().get('nombre')} for doc in docs]

    def get_videos_by_id_area(self, id_area):
        docs = self.db.collection('videos') \
            .where('id_area', '==', id_area) \
            .where('estado', '==', 'Activo').stream()

        videos = []
        for doc in docs:
            data = doc.to_dict()
            data['ID_Video'] = doc.id
            # Mapeo de campos a Mayúsculas como espera tu app antigua
            data['Nombre'] = data.get('nombre')
            data['Descripción'] = data.get('descripcion')
            data['URL_Video'] = data.get('url_video')
            data['Visualizaciones'] = data.get('visualizaciones', 0)

            # --- PARCHE DE SEGURIDAD ---
            # Evitamos números negativos con max(0, valor)
            data['Cantidad_Likes'] = max(0, data.get('cantidad_likes', 0))

            videos.append(data)
        return videos

    def get_video_by_id(self, video_id):
        doc = self.db.collection('videos').document(video_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['ID_Video'] = doc.id
            data['Nombre'] = data.get('nombre')
            data['Descripción'] = data.get('descripcion')
            data['URL_Video'] = data.get('url_video')
            data['Visualizaciones'] = data.get('visualizaciones', 0)

            # --- PARCHE DE SEGURIDAD ---
            # Evitamos números negativos con max(0, valor)
            data['Cantidad_Likes'] = max(0, data.get('cantidad_likes', 0))
            data['Cantidad_Dislikes'] = max(0, data.get('cantidad_dislikes', 0))

            return data
        return None

    def get_preguntas_por_id_video(self, video_id):
        docs = self.db.collection('preguntas') \
            .where('id_video', '==', video_id) \
            .where('estado', '==', 'Activo').stream()

        lista = []
        for doc in docs:
            d = doc.to_dict()
            opciones = d.get('opciones', {})
            comentarios = d.get('comentarios', {})

            lista.append({
                "ID_Pregunta": doc.id,
                "Pregunta": d.get('pregunta'),
                "Opcion_A": opciones.get('a'),
                "Opcion_B": opciones.get('b'),
                "Opcion_C": opciones.get('c'),  # Por si acaso
                "Opcion_Correcta": d.get('opcion_correcta'),
                "Comentario_Correcta": comentarios.get('correcta'),
                # Agrega más campos si tu UI los pide
            })
        return lista

    def get_preguntas_por_id_area_activo(self, id_area):
        docs = self.db.collection('preguntas') \
            .where('id_area', '==', id_area) \
            .where('estado', '==', 'Activo').stream()

        lista = []
        for doc in docs:
            d = doc.to_dict()
            opciones = d.get('opciones', {})
            comentarios = d.get('comentarios', {})
            lista.append({
                "ID_Pregunta": doc.id,
                "Pregunta": d.get('pregunta'),
                "Opcion_A": opciones.get('a'),
                "Opcion_B": opciones.get('b'),
                "Opcion_C": opciones.get('c'),
                "Opcion_Correcta": d.get('opcion_correcta'),
                "Comentario_A": comentarios.get('a'),
                "Comentario_B": comentarios.get('b'),
                "Comentario_C": comentarios.get('c'),
                "Comentario_Correcta": comentarios.get('correcta'),
                "ID_Tema": d.get('id_tema')
            })
        return lista

    def get_user_reaction_for_video(self, video_id, user_id):
        docs = self.db.collection('reacciones') \
            .where('id_video', '==', video_id) \
            .where('id_usuario', '==', user_id).limit(1).stream()
        for doc in docs:
            return doc.to_dict().get('tipo')
        return None

    def get_comments_by_id_video(self, video_id):
        # Nota: Ordenar por fecha requiere un índice en Firebase.
        # Si falla, remueve el .order_by o crea el índice en la consola.
        try:
            docs = self.db.collection('comentarios') \
                .where('id_video', '==', video_id) \
                .where('estado', '==', 'Activo') \
                .order_by('fecha', direction=firestore.Query.DESCENDING).stream()
        except Exception:
            # Fallback si no hay índice
            docs = self.db.collection('comentarios') \
                .where('id_video', '==', video_id) \
                .where('estado', '==', 'Activo').stream()

        comentarios = []
        for doc in docs:
            d = doc.to_dict()
            d['ID_Comentario'] = doc.id
            d['Comentario'] = d.get('comentario')
            # Convertir Timestamp a string para Flet
            fecha = d.get('fecha')
            if fecha:
                d['Fecha'] = str(fecha)
            comentarios.append(d)
        return comentarios

    # --- JUEGOS Y SIMULADORES ---

    def get_sopas_con_area_by_id_carrera(self, id_carrera):
        docs = self.db.collection('sopa') \
            .where('id_carrera', '==', id_carrera) \
            .where('estado', '==', 'Activo').stream()

        resultado = []
        for doc in docs:
            data = doc.to_dict()
            data['ID_Sopa'] = doc.id
            data['Cantidad_Palabras'] = data.get('cantidad_palabras')

            # Simular JOIN con Area
            id_area = data.get('id_area')
            if id_area:
                area_doc = self.db.collection('areas').document(id_area).get()
                data['NombreArea'] = area_doc.to_dict().get('nombre') if area_doc.exists else "N/A"

            resultado.append(data)
        return resultado

    def get_crucigramas_con_area_by_id_carrera(self, id_carrera):
        docs = self.db.collection('crucigrama') \
            .where('id_carrera', '==', id_carrera) \
            .where('estado', '==', 'Activo').stream()

        resultado = []
        for doc in docs:
            data = doc.to_dict()
            data['ID_Crucigrama'] = doc.id
            data['Cantidad_Palabras'] = data.get('cantidad_palabras')

            id_area = data.get('id_area')
            if id_area:
                area_doc = self.db.collection('areas').document(id_area).get()
                data['NombreArea'] = area_doc.to_dict().get('nombre') if area_doc.exists else "N/A"

            resultado.append(data)
        return resultado

    def get_simuladores_con_area_by_id_carrera(self, id_carrera):
        docs = self.db.collection('simuladores') \
            .where('id_carrera', '==', id_carrera) \
            .where('estado', '==', 'Activo').stream()

        resultado = []
        for doc in docs:
            data = doc.to_dict()
            data['ID_Simulador'] = doc.id
            data['Longitud'] = data.get('longitud')

            id_area = data.get('id_area')
            if id_area:
                area_doc = self.db.collection('areas').document(id_area).get()
                data['NombreArea'] = area_doc.to_dict().get('nombre') if area_doc.exists else "N/A"

            resultado.append(data)
        return resultado

    def get_palabras_por_sopa(self, id_sopa):
        docs = self.db.collection('palabras') \
            .where('id_sopa', '==', id_sopa).stream()
        return [doc.to_dict().get('palabra') for doc in docs]

    def palabra_crucigrama(self, id_crucigrama):
        # Traer todas las palabras y elegir una al azar en Python
        docs = list(self.db.collection('palabras') \
                    .where('id_crucigrama', '==', id_crucigrama) \
                    .where('estado', '==', 'Activo').stream())

        if docs:
            elegida = random.choice(docs)
            d = elegida.to_dict()
            return {'palabra': d.get('palabra'), 'descripcion': d.get('descripcion')}
        else:
            raise Exception("No se encontró una palabra para este crucigrama.")

    def get_tema_by_id(self, id_tema):
        doc = self.db.collection('temas').document(id_tema).get()
        if doc.exists:
            d = doc.to_dict()
            d['ID_Tema'] = doc.id
            d['Nombre'] = d.get('nombre')
            return d
        return None

    # ==========================================
    #      MÉTODOS DE ESCRITURA (INSERT/UPDATE)
    # ==========================================

    def insert_reaction(self, reaction_id, video_id, user_id, tipo):
        self.db.collection('reacciones').document(reaction_id).set({
            "id_video": video_id,
            "id_usuario": user_id,
            "tipo": tipo,
            "fecha": firestore.SERVER_TIMESTAMP,
            "estado": "Activo"
        })
        # Actualización atómica de contador
        if tipo == 'like':
            self.db.collection('videos').document(video_id) \
                .update({"cantidad_likes": firestore.Increment(1)})
        elif tipo == 'dislike':
            self.db.collection('videos').document(video_id) \
                .update({"cantidad_dislikes": firestore.Increment(1)})

    def delete_reaction(self, video_id, user_id):
        docs = self.db.collection('reacciones') \
            .where('id_video', '==', video_id) \
            .where('id_usuario', '==', user_id).stream()

        for doc in docs:
            tipo = doc.to_dict().get('tipo')
            self.db.collection('reacciones').document(doc.id).delete()

            campo = "cantidad_likes" if tipo == "like" else "cantidad_dislikes"
            self.db.collection('videos').document(video_id) \
                .update({campo: firestore.Increment(-1)})

    def incrementar_visualizacion(self, id_video):
        self.db.collection('videos').document(id_video) \
            .update({"visualizaciones": firestore.Increment(1)})

    def add_comment(self, comment_id, video_id, user_id, comment_text):
        self.db.collection('comentarios').document(comment_id).set({
            "comentario": comment_text,
            "id_usuario": user_id,
            "id_video": video_id,
            "fecha": firestore.SERVER_TIMESTAMP,
            "estado": "Activo"
        })

    def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        self.db.collection('usuarios').document(id_usuario).set({
            "id_campus": id_campus,
            "id_carrera": id_carrera
        }, merge=True)

    def guardar_calificacion_por_tema(self, id_usuario, id_tema, calificacion, id_simulador, tiempo, id_resultado,
                                      fecha):
        self.db.collection('resultados').document(id_resultado).set({
            "id_usuario": id_usuario,
            "id_tema": id_tema,
            "calificacion": calificacion,
            "id_simulador": id_simulador,
            "tiempo": tiempo,
            "fecha": fecha
        })

    def get_campus_by_id(self, id_campus):
        # Busca el documento específico por ID
        doc = self.db.collection('campus').document(id_campus).get()
        if doc.exists:
            d = doc.to_dict()
            # Retornamos estructura compatible con tu main
            return {"ID_Campus": doc.id, "Nombre": d.get('nombre')}
        return None

    def get_id_carrera_by_nombre(self, nombre_carrera):
        # Busca en la colección 'carreras' el documento que tenga ese nombre
        docs = self.db.collection('carreras') \
            .where(field_path='nombre', op_string='==', value=nombre_carrera) \
            .limit(1).stream()

        for doc in docs:
            return doc.id  # Retorna el ID del documento (ej: "ISO")
        return None

    def get_carrera_by_id(self, id_carrera):
        doc = self.db.collection('carreras').document(id_carrera).get()
        if doc.exists:
            d = doc.to_dict()
            # Retornamos el diccionario con 'Nombre' en mayúscula para compatibilidad
            return {"ID_Carrera": doc.id, "Nombre": d.get('nombre')}
        return None

    def update_video_counter(self, video_id, field, delta):
        """
        Actualiza contadores (Likes, Dislikes, Vistas) de forma atómica.
        field: Nombre del campo que venía de SQL (ej: 'Cantidad_Likes')
        delta: +1 o -1
        """
        # Mapeo de nombres de columnas SQL a campos Firestore (minúsculas)
        mapa_campos = {
            "Cantidad_Likes": "cantidad_likes",
            "Cantidad_Dislikes": "cantidad_dislikes",
            "Visualizaciones": "visualizaciones"
        }

        # Obtenemos el nombre correcto en Firestore
        campo_firestore = mapa_campos.get(field)

        if campo_firestore:
            self.db.collection('videos').document(video_id).update({
                campo_firestore: firestore.Increment(delta)
            })
        else:
            print(f"ERROR: Campo desconocido para contador: {field}")

    # --- Métodos de compatibilidad vacíos ---
    # Estos métodos ya no son necesarios en Firebase o se manejan distinto,
    # pero los dejo vacíos para que no den error si se llaman por accidente.
    def _get_connection(self):
        pass

    def _ensure_tables_exist_and_populate(self):
        pass

    def _execute_query(self, query, params=()):
        return []

    def _execute_commit(self, query, params=()):
        pass