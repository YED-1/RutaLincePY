import sqlite3
import os


class DatabaseHelper:
    def __init__(self, db_name="ruta_lince.db"):
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
            '''CREATE TABLE IF NOT EXISTS Video (ID_Video TEXT PRIMARY KEY, Nombre TEXT, Descripción TEXT, URL_Video TEXT, Visualizaciones INTEGER DEFAULT 0, Estado TEXT, ID_Area TEXT, FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))''',
            '''CREATE TABLE IF NOT EXISTS Crucigrama (ID_Crucigrama TEXT PRIMARY KEY, Cantidad_Palabras INTEGER, Estado TEXT, ID_Area TEXT, ID_Carrera TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area))'''
            # ... y el resto de tus tablas ...
        ]

        for query in create_table_queries:
            cursor.execute(query)

        self.conn.commit()

    def get_campus(self):
        """Obtiene todos los campus."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Campus, Nombre FROM Campus WHERE Estado = 'Activo'")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_nombres_carrera_por_id_campus(self, id_campus):
        """Obtiene los nombres de las carreras para un campus específico."""
        cursor = self.conn.cursor()
        query = """
            SELECT c.Nombre
            FROM Carrera_Campus cc
            JOIN Carrera c ON cc.ID_Carrera = c.ID_Carrera
            WHERE cc.ID_Campus = ? AND c.Estado = 'Activo'
        """
        cursor.execute(query, (id_campus,))
        rows = cursor.fetchall()
        return [row['Nombre'] for row in rows]

    def get_id_carrera_by_nombre(self, nombre_carrera):
        """Obtiene el ID de una carrera a partir de su nombre."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Carrera FROM Carrera WHERE Nombre = ?", (nombre_carrera,))
        result = cursor.fetchone()
        return result['ID_Carrera'] if result else None

    def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        """Inserta un nuevo usuario o actualiza sus datos si ya existe."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Usuario FROM Usuario WHERE ID_Usuario = ?", (id_usuario,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE Usuario SET ID_Campus = ?, ID_Carrera = ? WHERE ID_Usuario = ?
            """, (id_campus, id_carrera, id_usuario))
        else:
            cursor.execute("""
                INSERT INTO Usuario (ID_Usuario, ID_Campus, ID_Carrera) VALUES (?, ?, ?)
            """, (id_usuario, id_campus, id_carrera))
        self.conn.commit()

    def get_areas_id_carrera(self, id_carrera):
        """Obtiene las áreas asociadas a una carrera."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Area, Nombre FROM Area WHERE ID_Carrera = ? AND Estado = 'Activo'", (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    def get_videos_by_id_area(self, id_area):
        """Obtiene los videos para un área específica."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Video WHERE ID_Area = ? AND Estado = 'Activo'", (id_area,))
        return [dict(row) for row in cursor.fetchall()]

    def incrementar_visualizacion(self, id_video):
        """Incrementa el contador de visualizaciones de un video."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Video SET Visualizaciones = Visualizaciones + 1 WHERE ID_Video = ?", (id_video,))
        self.conn.commit()

    def get_campus_by_id(self, id_campus):
        """Obtiene los datos de un campus a partir de su ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Campus WHERE ID_Campus = ?", (id_campus,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_carrera_by_id(self, id_carrera):
        """Obtiene los datos de una carrera a partir de su ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Carrera WHERE ID_Carrera = ?", (id_carrera,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_crucigramas_con_area_by_id_carrera(self, id_carrera):
        """
        Obtiene los crucigramas de una carrera y une el nombre del área
        en una sola consulta optimizada.
        """
        cursor = self.conn.cursor()
        query = """
            SELECT cr.*, ar.Nombre as NombreArea
            FROM Crucigrama cr
            JOIN Area ar ON cr.ID_Area = ar.ID_Area
            WHERE cr.ID_Carrera = ? AND cr.Estado = 'Activo'
        """
        cursor.execute(query, (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]

    def get_sopas_con_area_by_id_carrera(self, id_carrera):
        """
        Obtiene las sopas de letras de una carrera y une el nombre del área
        en una sola consulta optimizada.
        """
        cursor = self.conn.cursor()
        query = """
               SELECT s.*, ar.Nombre as NombreArea
               FROM Sopa s
               JOIN Area ar ON s.ID_Area = ar.ID_Area
               WHERE s.ID_Carrera = ? AND s.Estado = 'Activo'
           """
        cursor.execute(query, (id_carrera,))
        return [dict(row) for row in cursor.fetchall()]