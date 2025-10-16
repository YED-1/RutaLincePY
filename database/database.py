import sqlite3
import os
import datetime
import uuid


class DatabaseHelper:
    def __init__(self, db_name="ruta_lince.db"):
        # La base de datos se guardará en la carpeta 'src/database/'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.conn = None
        self._connect_and_create()

    def _connect_and_create(self):
        """Conecta a la BD y crea las tablas si no existen."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        cursor = self.conn.cursor()

        create_table_queries = [
            '''CREATE TABLE IF NOT EXISTS Campus (ID_Campus TEXT PRIMARY KEY, Nombre TEXT, Estado TEXT)''',
            '''CREATE TABLE IF NOT EXISTS Carrera (ID_Carrera TEXT PRIMARY KEY, Nombre TEXT, Estado TEXT)''',
            '''CREATE TABLE IF NOT EXISTS Usuario (ID_Usuario TEXT PRIMARY KEY, ID_Campus TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus))''',
            '''CREATE TABLE IF NOT EXISTS Carrera_Campus (ID_Carrera_Campus TEXT PRIMARY KEY, ID_Carrera TEXT, ID_Campus TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus))''',
            '''CREATE TABLE IF NOT EXISTS Area (ID_Area TEXT PRIMARY KEY, Nombre TEXT, Estado TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera))''',
            '''CREATE TABLE IF NOT EXISTS Tema (ID_Tema TEXT PRIMARY KEY, Nombre TEXT, ID_Area TEXT, Estado TEXT, FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Video (ID_Video TEXT PRIMARY KEY, Nombre TEXT, Descripción TEXT, URL_Video TEXT, Visualizaciones INTEGER DEFAULT 0, Cantidad_Likes INTEGER DEFAULT 0, Cantidad_Dislikes INTEGER DEFAULT 0, Estado TEXT, ID_Area TEXT, FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Reaccion (ID_Reaccion TEXT PRIMARY KEY, Tipo TEXT, Fecha DATE, Estado TEXT, ID_Video TEXT, ID_Usuario TEXT, FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video), FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario))''',
            '''CREATE TABLE IF NOT EXISTS Comentario (ID_Comentario TEXT PRIMARY KEY, Comentario TEXT, Fecha DATE, Estado TEXT, ID_Usuario TEXT, ID_Video TEXT, FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario), FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video))''',
            '''CREATE TABLE IF NOT EXISTS Simulador (ID_Simulador TEXT PRIMARY KEY, Longitud INTEGER, Estado TEXT, ID_Carrera TEXT, ID_Area TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera))''',
            '''CREATE TABLE IF NOT EXISTS Resultado (ID_Resultado TEXT PRIMARY KEY, Calificacion REAL, Tiempo INTEGER, Fecha TEXT, ID_Tema TEXT, ID_Usuario TEXT, ID_Simulador TEXT, FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema), FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario), FOREIGN KEY (ID_Simulador) REFERENCES Simulador(ID_Simulador))''',
            '''CREATE TABLE IF NOT EXISTS Pregunta (ID_Pregunta TEXT PRIMARY KEY, Pregunta TEXT, Opcion_A TEXT, Opcion_B TEXT, Opcion_C TEXT, Opcion_Correcta TEXT, Comentario TEXT, Estado TEXT, ID_Video TEXT, ID_Area TEXT, ID_Tema TEXT, FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area), FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema))''',
            '''CREATE TABLE IF NOT EXISTS Sopa (ID_Sopa TEXT PRIMARY KEY, Cantidad_Palabras INTEGER, Estado TEXT, ID_Area TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Crucigrama (ID_Crucigrama TEXT PRIMARY KEY, Cantidad_Palabras INTEGER, Estado TEXT, ID_Area TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Palabra (ID_Palabra TEXT PRIMARY KEY, Palabra TEXT, Descripción TEXT, Estado TEXT, ID_Area TEXT, ID_Sopa TEXT, ID_Crucigrama TEXT, FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area), FOREIGN KEY (ID_Sopa) REFERENCES Sopa(ID_Sopa), FOREIGN KEY (ID_Crucigrama) REFERENCES Crucigrama(ID_Crucigrama))'''
        ]

        for query in create_table_queries:
            cursor.execute(query)

        self.conn.commit()

    def get_campus(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Campus, Nombre FROM Campus WHERE Estado = 'Activo'")
        return [dict(row) for row in cursor.fetchall()]

    def get_nombres_carrera_por_id_campus(self, id_campus):
        cursor = self.conn.cursor()
        query = "SELECT c.Nombre FROM Carrera_Campus cc JOIN Carrera c ON cc.ID_Carrera = c.ID_Carrera WHERE cc.ID_Campus = ? AND c.Estado = 'Activo'"
        cursor.execute(query, (id_campus,))
        return [row['Nombre'] for row in cursor.fetchall()]

    def get_id_carrera_by_nombre(self, nombre_carrera):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Carrera FROM Carrera WHERE Nombre = ?", (nombre_carrera,))
        result = cursor.fetchone()
        return result['ID_Carrera'] if result else None

    def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Usuario FROM Usuario WHERE ID_Usuario = ?", (id_usuario,))
        if cursor.fetchone():
            cursor.execute("UPDATE Usuario SET ID_Campus = ?, ID_Carrera = ? WHERE ID_Usuario = ?",
                           (id_campus, id_carrera, id_usuario))
        else:
            cursor.execute("INSERT INTO Usuario (ID_Usuario, ID_Campus, ID_Carrera) VALUES (?, ?, ?)",
                           (id_usuario, id_campus, id_carrera))
        self.conn.commit()

    def get_areas_id_carrera(self, id_carrera):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Area, Nombre FROM Area WHERE ID_Carrera = ? AND Estado = 'Activo'", (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    def get_videos_by_id_area(self, id_area):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Video WHERE ID_Area = ? AND Estado = 'Activo'", (id_area,))
        return [dict(row) for row in cursor.fetchall()]

    def incrementar_visualizacion(self, id_video):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Video SET Visualizaciones = Visualizaciones + 1 WHERE ID_Video = ?", (id_video,))
        self.conn.commit()

    def get_campus_by_id(self, id_campus):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Campus WHERE ID_Campus = ?", (id_campus,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_carrera_by_id(self, id_carrera):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Carrera WHERE ID_Carrera = ?", (id_carrera,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_crucigramas_con_area_by_id_carrera(self, id_carrera):
        cursor = self.conn.cursor()
        query = "SELECT cr.*, ar.Nombre as NombreArea FROM Crucigrama cr JOIN Area ar ON cr.ID_Area = ar.ID_Area WHERE cr.ID_Carrera = ? AND cr.Estado = 'Activo'"
        cursor.execute(query, (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    def get_sopas_con_area_by_id_carrera(self, id_carrera):
        cursor = self.conn.cursor()
        query = "SELECT s.*, ar.Nombre as NombreArea FROM Sopa s JOIN Area ar ON s.ID_Area = ar.ID_Area WHERE s.ID_Carrera = ? AND s.Estado = 'Activo'"
        cursor.execute(query, (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    def get_palabras_por_sopa(self, id_sopa):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Palabra FROM Palabra WHERE ID_Sopa = ?", (id_sopa,))
        return [row['Palabra'] for row in cursor.fetchall()]

    def get_video_by_id(self, video_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Video WHERE ID_Video = ?", (video_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_reaction_for_video(self, video_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Tipo FROM Reaccion WHERE ID_Video = ? AND ID_Usuario = ?", (video_id, user_id))
        row = cursor.fetchone()
        return row['Tipo'] if row else None

    def delete_reaction(self, video_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Reaccion WHERE ID_Video = ? AND ID_Usuario = ?", (video_id, user_id))
        self.conn.commit()

    def insert_reaction(self, reaction_id, video_id, user_id, tipo):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Reaccion (ID_Reaccion, ID_Video, ID_Usuario, Tipo, Fecha, Estado) VALUES (?, ?, ?, ?, date('now'), 'Activo')",
            (reaction_id, video_id, user_id, tipo))
        self.conn.commit()

    def update_video_counter(self, video_id, field, delta):
        cursor = self.conn.cursor()
        if field in ['Cantidad_Likes', 'Cantidad_Dislikes']:
            cursor.execute(f"UPDATE Video SET {field} = {field} + ? WHERE ID_Video = ?", (delta, video_id))
            self.conn.commit()

    def get_comments_by_id_video(self, video_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Comentario WHERE ID_Video = ? AND Estado = 'Activo' ORDER BY Fecha DESC",
                       (video_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_comment(self, comment_id, video_id, user_id, comment_text):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Comentario (ID_Comentario, Comentario, Fecha, Estado, ID_Usuario, ID_Video) VALUES (?, ?, date('now'), 'Activo', ?, ?)",
            (comment_id, comment_text, user_id, video_id))
        self.conn.commit()

    def get_preguntas_por_id_area_activo(self, id_area):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_Correcta, Comentario, ID_Tema FROM Pregunta WHERE ID_Area = ? AND Estado = 'Activo' AND ID_Tema != 'No aplica'",
            (id_area,))
        return [dict(row) for row in cursor.fetchall()]

    def get_nombres_temas_por_ids(self, ids_tema: list):
        if not ids_tema: return {}
        placeholders = ','.join('?' for _ in ids_tema)
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT ID_Tema, Nombre FROM Tema WHERE ID_Tema IN ({placeholders})", ids_tema)
        return {row['ID_Tema']: row['Nombre'] for row in cursor.fetchall()}

    def guardar_calificacion_por_tema(self, id_usuario, id_tema, calificacion, id_simulador, tiempo, id_resultado,
                                      fecha):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Resultado FROM Resultado WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?",
                       (id_usuario, id_tema, id_simulador))
        existe = cursor.fetchone()
        if existe:
            cursor.execute(
                "UPDATE Resultado SET Calificacion = ?, Tiempo = ?, Fecha = ? WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?",
                (calificacion, tiempo, fecha, id_usuario, id_tema, id_simulador))
        else:
            cursor.execute(
                "INSERT INTO Resultado (ID_Resultado, Calificacion, Tiempo, Fecha, ID_Tema, ID_Usuario, ID_Simulador) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_resultado, calificacion, tiempo, fecha, id_tema, id_usuario, id_simulador))
        self.conn.commit()

    def get_simuladores_con_area_by_id_carrera(self, id_carrera):
        cursor = self.conn.cursor()
        query = "SELECT s.*, ar.Nombre as NombreArea FROM Simulador s JOIN Area ar ON s.ID_Area = ar.ID_Area WHERE s.ID_Carrera = ? AND s.Estado = 'Activo'"
        cursor.execute(query, (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    # --- NUEVA FUNCIÓN AÑADIDA ---
    def get_preguntas_por_id_video(self, video_id):
        """Obtiene las preguntas y opciones para un video específico."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_Correcta, Comentario
            FROM Pregunta
            WHERE ID_Video = ? AND Estado = 'Activo'
        """, (video_id,))
        return [dict(row) for row in cursor.fetchall()]