import sqlite3
import os


# import uuid
# import datetime


class DatabaseHelper:
    def __init__(self, db_name="ruta_lince.db"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.base_dir, db_name)
        self._ensure_tables_exist_and_populate()

    def _get_connection(self):
        """Creates and returns a new thread-safe connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables_exist_and_populate(self):
        """Ensures tables exist and calls the CSV loader if needed."""
        conn = self._get_connection()
        cursor = conn.cursor()

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
            '''CREATE TABLE IF NOT EXISTS Simulador (ID_Simulador TEXT PRIMARY KEY, Longitud INTEGER, Estado TEXT, ID_Carrera TEXT, ID_Area TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Resultado (ID_Resultado TEXT PRIMARY KEY, Calificacion REAL, Tiempo INTEGER, Fecha TEXT, ID_Tema TEXT, ID_Usuario TEXT, ID_Simulador TEXT, FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema), FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario), FOREIGN KEY (ID_Simulador) REFERENCES Simulador(ID_Simulador))''',
            '''CREATE TABLE IF NOT EXISTS Pregunta (ID_Pregunta TEXT PRIMARY KEY, Pregunta TEXT, Opcion_A TEXT, Opcion_B TEXT, Opcion_C TEXT, Opcion_Correcta TEXT, Comentario TEXT, Estado TEXT, ID_Video TEXT, ID_Area TEXT, ID_Tema TEXT, FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area), FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema))''',
            '''CREATE TABLE IF NOT EXISTS Sopa (ID_Sopa TEXT PRIMARY KEY, Cantidad_Palabras INTEGER, Estado TEXT, ID_Area TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Crucigrama (ID_Crucigrama TEXT PRIMARY KEY, Cantidad_Palabras INTEGER, Estado TEXT, ID_Area TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Palabra (ID_Palabra TEXT PRIMARY KEY, Palabra TEXT, Descripción TEXT, Estado TEXT, ID_Area TEXT, ID_Sopa TEXT, ID_Crucigrama TEXT, FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area), FOREIGN KEY (ID_Sopa) REFERENCES Sopa(ID_Sopa), FOREIGN KEY (ID_Crucigrama) REFERENCES Crucigrama(ID_Crucigrama))'''
        ]

        for query in create_table_queries:
            cursor.execute(query)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM Campus")
        if cursor.fetchone()[0] == 0:
            try:
                from src.database import csv_loader  # Usamos import absoluto
                csv_loader.populate_from_csv_if_empty(self, conn)
            except ImportError as e:
                print(f"ADVERTENCIA: No se pudo importar csv_loader ({e}). Omitiendo carga desde CSV.")
            except Exception as e:
                print(f"ERROR durante la carga CSV inicial: {e}")

        conn.close()

    def _execute_query(self, query, params=()):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def _execute_commit(self, query, params=()):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Ignorar duplicados
        except Exception as e:
            print(f"DB Error: {e}. Query: {query}, Params: {params}")
        finally:
            conn.close()

    # --- Insertion Methods ---
    def insert_campus(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Campus VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    def insert_carrera(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Carrera VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    def insert_carrera_campus(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Carrera_Campus VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    def insert_area(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Area VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

    def insert_tema(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Tema VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

    def insert_video(self, row):
        self._execute_commit(
            "INSERT OR IGNORE INTO Video (ID_Video, Nombre, Descripción, URL_Video, Estado, ID_Area) VALUES (?, ?, ?, ?, ?, ?)",
            (row[0], row[1], row[2], row[3], row[8], row[9]))

    def insert_pregunta(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Pregunta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

    def insert_simulador(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Simulador VALUES (?, ?, ?, ?, ?)",
                             (row[0], int(row[1]), row[2], row[3], row[4]))

    def insert_sopa(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Sopa VALUES (?, ?, ?, ?, ?)",
                             (row[0], int(row[1]), row[2], row[3], row[4]))

    def insert_crucigrama(self, row):
        self._execute_commit("INSERT OR IGNORE INTO Crucigrama VALUES (?, ?, ?, ?, ?)",
                             (row[0], int(row[1]), row[2], row[3], row[4]))

    def insert_palabra(self, row):
        self._execute_commit(
            "INSERT OR IGNORE INTO Palabra (ID_Palabra, Palabra, Descripción, Estado, ID_Area, ID_Sopa, ID_Crucigrama) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row[0], row[2], row[3], row[4], row[5], row[6], row[7]))

    # --- GET Methods ---
    def get_campus(self):
        return self._execute_query("SELECT ID_Campus, Nombre FROM Campus WHERE Estado = 'Activo'")

    def get_nombres_carrera_por_id_campus(self, id_campus):
        query = "SELECT c.Nombre FROM Carrera_Campus cc JOIN Carrera c ON cc.ID_Carrera = c.ID_Carrera WHERE cc.ID_Campus = ? AND c.Estado = 'Activo'"
        rows = self._execute_query(query, (id_campus,))
        return [row['Nombre'] for row in rows]

    def get_id_carrera_by_nombre(self, nombre_carrera):
        rows = self._execute_query("SELECT ID_Carrera FROM Carrera WHERE Nombre = ?", (nombre_carrera,))
        return rows[0]['ID_Carrera'] if rows else None

    def get_areas_id_carrera(self, id_carrera):
        return self._execute_query("SELECT ID_Area, Nombre FROM Area WHERE ID_Carrera = ? AND Estado = 'Activo'",
                                   (id_carrera,))

    def get_videos_by_id_area(self, id_area):
        return self._execute_query("SELECT * FROM Video WHERE ID_Area = ? AND Estado = 'Activo'", (id_area,))

    def get_campus_by_id(self, id_campus):
        rows = self._execute_query("SELECT * FROM Campus WHERE ID_Campus = ?", (id_campus,))
        return rows[0] if rows else None

    def get_carrera_by_id(self, id_carrera):
        rows = self._execute_query("SELECT * FROM Carrera WHERE ID_Carrera = ?", (id_carrera,))
        return rows[0] if rows else None

    def get_crucigramas_con_area_by_id_carrera(self, id_carrera):
        query = "SELECT cr.*, ar.Nombre as NombreArea FROM Crucigrama cr JOIN Area ar ON cr.ID_Area = ar.ID_Area WHERE cr.ID_Carrera = ? AND cr.Estado = 'Activo'"
        return self._execute_query(query, (id_carrera,))

    def get_sopas_con_area_by_id_carrera(self, id_carrera):
        query = "SELECT s.*, ar.Nombre as NombreArea FROM Sopa s JOIN Area ar ON s.ID_Area = ar.ID_Area WHERE s.ID_Carrera = ? AND s.Estado = 'Activo'"
        return self._execute_query(query, (id_carrera,))

    def get_palabras_por_sopa(self, id_sopa):
        rows = self._execute_query("SELECT Palabra FROM Palabra WHERE ID_Sopa = ?", (id_sopa,))
        return [row['Palabra'] for row in rows]

    def get_video_by_id(self, video_id):
        rows = self._execute_query("SELECT * FROM Video WHERE ID_Video = ?", (video_id,))
        return rows[0] if rows else None

    def get_user_reaction_for_video(self, video_id, user_id):
        rows = self._execute_query("SELECT Tipo FROM Reaccion WHERE ID_Video = ? AND ID_Usuario = ?",
                                   (video_id, user_id))
        return rows[0]['Tipo'] if rows else None

    def get_comments_by_id_video(self, video_id):
        return self._execute_query(
            "SELECT * FROM Comentario WHERE ID_Video = ? AND Estado = 'Activo' ORDER BY Fecha DESC", (video_id,))

    def get_preguntas_por_id_area_activo(self, id_area):
        return self._execute_query(
            "SELECT ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_C, Opcion_Correcta, Comentario_A, Comentario_B, Comentario_C, Comentario_Correcta, ID_Tema FROM Pregunta WHERE ID_Area = ? AND Estado = 'Activo' AND ID_Tema != 'No aplica'",
            (id_area,))

    def get_nombres_temas_por_ids(self, ids_tema: list):
        if not ids_tema: return {}
        placeholders = ','.join('?' for _ in ids_tema)
        rows = self._execute_query(f"SELECT ID_Tema, Nombre FROM Tema WHERE ID_Tema IN ({placeholders})", ids_tema)
        return {row['ID_Tema']: row['Nombre'] for row in rows}

    def get_tema_by_id(self, id_tema):
        rows = self._execute_query("SELECT * FROM Tema WHERE ID_Tema = ?", (id_tema,))
        return rows[0] if rows else None

    def get_simuladores_con_area_by_id_carrera(self, id_carrera):
        query = "SELECT s.*, ar.Nombre as NombreArea FROM Simulador s JOIN Area ar ON s.ID_Area = ar.ID_Area WHERE s.ID_Carrera = ? AND s.Estado = 'Activo'"
        return self._execute_query(query, (id_carrera,))

    def get_preguntas_por_id_video(self, video_id):
        return self._execute_query(
            "SELECT ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_Correcta, Comentario FROM Pregunta WHERE ID_Video = ? AND Estado = 'Activo'",
            (video_id,))

    def palabra_crucigrama(self, id_crucigrama):
        rows = self._execute_query(
            "SELECT Palabra, Descripción FROM Palabra WHERE ID_Crucigrama = ? AND Estado = 'Activo' ORDER BY RANDOM() LIMIT 1",
            (id_crucigrama,))
        if rows:
            return {'palabra': rows[0]['Palabra'], 'descripcion': rows[0]['Descripción']}
        else:
            raise Exception("No se encontró una palabra para este crucigrama.")

    def get_carrera(self):
        return self._execute_query("SELECT * FROM Carrera")

    def get_carrera_campus(self):
        return self._execute_query("SELECT * FROM Carrera_Campus")

    def get_video(self):
        return self._execute_query("SELECT * FROM Video")

    def get_area(self):
        return self._execute_query("SELECT * FROM Area")

    def get_pregunta(self):
        return self._execute_query("SELECT * FROM Pregunta")

    def get_comentario(self):
        return self._execute_query("SELECT * FROM Comentario")

    def get_simulador(self):
        return self._execute_query("SELECT * FROM Simulador")

    def get_crucigrama(self):
        return self._execute_query("SELECT * FROM Crucigrama")

    def get_sopa(self):
        return self._execute_query("SELECT * FROM Sopa")

    def get_palabra(self):
        return self._execute_query("SELECT * FROM Palabra")

    def get_usuario(self):
        return self._execute_query("SELECT * FROM Usuario")

    def get_tema(self):
        return self._execute_query("SELECT * FROM Tema")

    def get_resultado(self):
        return self._execute_query("SELECT * FROM Resultado")

    # --- UPDATE/INSERT Methods ---
    def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Usuario FROM Usuario WHERE ID_Usuario = ?", (id_usuario,))
        if cursor.fetchone():
            cursor.execute("UPDATE Usuario SET ID_Campus = ?, ID_Carrera = ? WHERE ID_Usuario = ?",
                           (id_campus, id_carrera, id_usuario))
        else:
            cursor.execute("INSERT INTO Usuario (ID_Usuario, ID_Campus, ID_Carrera) VALUES (?, ?, ?)",
                           (id_usuario, id_campus, id_carrera))
        conn.commit()
        conn.close()

    def incrementar_visualizacion(self, id_video):
        self._execute_commit("UPDATE Video SET Visualizaciones = Visualizaciones + 1 WHERE ID_Video = ?", (id_video,))

    def delete_reaction(self, video_id, user_id):
        self._execute_commit("DELETE FROM Reaccion WHERE ID_Video = ? AND ID_Usuario = ?", (video_id, user_id))

    def insert_reaction(self, reaction_id, video_id, user_id, tipo):
        self._execute_commit(
            "INSERT INTO Reaccion (ID_Reaccion, ID_Video, ID_Usuario, Tipo, Fecha, Estado) VALUES (?, ?, ?, ?, date('now'), 'Activo')",
            (reaction_id, video_id, user_id, tipo))

    def update_video_counter(self, video_id, field, delta):
        if field in ['Cantidad_Likes', 'Cantidad_Dislikes']:
            self._execute_commit(
                f"UPDATE Video SET {field} = MAX(0, {field} + ?) WHERE ID_Video = ?",
                (delta, video_id)
            )

    def add_comment(self, comment_id, video_id, user_id, comment_text):
        self._execute_commit(
            "INSERT INTO Comentario (ID_Comentario, Comentario, Fecha, Estado, ID_Usuario, ID_Video) VALUES (?, ?, date('now'), 'Activo', ?, ?)",
            (comment_id, comment_text, user_id, video_id))

    def guardar_calificacion_por_tema(self, id_usuario, id_tema, calificacion, id_simulador, tiempo, id_resultado,
                                      fecha):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Resultado FROM Resultado WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?",
                       (id_usuario, id_tema, id_simulador))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE Resultado SET Calificacion = ?, Tiempo = ?, Fecha = ? WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?",
                (calificacion, tiempo, fecha, id_usuario, id_tema, id_simulador))
        else:
            cursor.execute(
                "INSERT INTO Resultado (ID_Resultado, Calificacion, Tiempo, Fecha, ID_Tema, ID_Usuario, ID_Simulador) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_resultado, calificacion, tiempo, fecha, id_tema, id_usuario, id_simulador))
        conn.commit()
        conn.close()

    # --- Métodos adicionales para estadísticas ---
    def get_estadisticas_usuario(self, id_usuario):
        """Obtiene estadísticas del usuario"""
        query = """
        SELECT 
            COUNT(DISTINCT r.ID_Simulador) as simuladores_completados,
            AVG(r.Calificacion) as promedio_general,
            SUM(r.Tiempo) as tiempo_total
        FROM Resultado r 
        WHERE r.ID_Usuario = ?
        """
        rows = self._execute_query(query, (id_usuario,))
        return rows[0] if rows else None

    def get_progreso_por_area(self, id_usuario, id_carrera):
        """Obtiene el progreso del usuario por área"""
        query = """
        SELECT 
            a.ID_Area,
            a.Nombre as nombre_area,
            COUNT(DISTINCT r.ID_Tema) as temas_completados,
            COUNT(DISTINCT t.ID_Tema) as total_temas,
            AVG(r.Calificacion) as promedio_area
        FROM Area a
        LEFT JOIN Tema t ON a.ID_Area = t.ID_Area
        LEFT JOIN Resultado r ON t.ID_Tema = r.ID_Tema AND r.ID_Usuario = ?
        WHERE a.ID_Carrera = ? AND a.Estado = 'Activo'
        GROUP BY a.ID_Area, a.Nombre
        """
        return self._execute_query(query, (id_usuario, id_carrera))

    def get_historial_simuladores(self, id_usuario):
        """Obtiene el historial de simuladores del usuario"""
        query = """
        SELECT 
            r.Fecha,
            s.ID_Simulador,
            a.Nombre as area,
            r.Calificacion,
            r.Tiempo
        FROM Resultado r
        JOIN Simulador s ON r.ID_Simulador = s.ID_Simulador
        JOIN Area a ON s.ID_Area = a.ID_Area
        WHERE r.ID_Usuario = ?
        ORDER BY r.Fecha DESC
        LIMIT 10
        """
        return self._execute_query(query, (id_usuario,))

    # --- Métodos para limpieza y mantenimiento ---
    def limpiar_datos_temporales(self):
        """Limpia datos temporales o antiguos"""
        # Ejemplo: eliminar reacciones y comentarios de usuarios anónimos antiguos
        queries = [
            "DELETE FROM Reaccion WHERE Estado = 'Inactivo'",
            "DELETE FROM Comentario WHERE Estado = 'Inactivo'",
            "DELETE FROM Usuario WHERE ID_Usuario NOT IN (SELECT DISTINCT ID_Usuario FROM Resultado) AND ID_Usuario NOT IN (SELECT DISTINCT ID_Usuario FROM Reaccion) AND ID_Usuario NOT IN (SELECT DISTINCT ID_Usuario FROM Comentario)"
        ]

        conn = self._get_connection()
        cursor = conn.cursor()
        for query in queries:
            try:
                cursor.execute(query)
            except Exception as e:
                print(f"Error en limpieza: {e}")
        conn.commit()
        conn.close()

    def backup_database(self, backup_path):
        """Crea una copia de seguridad de la base de datos"""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error en backup: {e}")
            return False

    # --- Métodos de validación ---
    def verificar_integridad(self):
        """Verifica la integridad de la base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Verificar claves foráneas
        cursor.execute("PRAGMA foreign_key_check")
        foreign_key_issues = cursor.fetchall()

        # Verificar integridad de la estructura
        cursor.execute("PRAGMA integrity_check")
        integrity_check = cursor.fetchone()[0]

        conn.close()

        return {
            'integrity_check': integrity_check,
            'foreign_key_issues': foreign_key_issues,
            'is_valid': integrity_check == 'ok' and not foreign_key_issues
        }

    # --- Métodos para administración ---
    def obtener_estadisticas_globales(self):
        """Obtiene estadísticas globales del sistema"""
        queries = {
            'total_usuarios': "SELECT COUNT(*) as count FROM Usuario",
            'total_videos': "SELECT COUNT(*) as count FROM Video WHERE Estado = 'Activo'",
            'total_preguntas': "SELECT COUNT(*) as count FROM Pregunta WHERE Estado = 'Activo'",
            'total_simuladores': "SELECT COUNT(*) as count FROM Simulador WHERE Estado = 'Activo'",
            'total_resultados': "SELECT COUNT(*) as count FROM Resultado",
            'promedio_calificacion': "SELECT AVG(Calificacion) as avg FROM Resultado"
        }

        stats = {}
        conn = self._get_connection()
        cursor = conn.cursor()

        for key, query in queries.items():
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                stats[key] = result[0] if result[0] is not None else 0
            except Exception as e:
                print(f"Error en estadística {key}: {e}")
                stats[key] = 0

        conn.close()
        return stats