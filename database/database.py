import sqlite3
import os

class DatabaseHelper:
    def __init__(self, db_name="ruta_lince.db"):
        # La base de datos se guardará en la misma carpeta que este archivo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.conn = None
        self._connect_and_create()

    def _connect_and_create(self):
        """Conecta a la BD y crea las tablas si no existen."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        cursor = self.conn.cursor()

        # Lista de todas las sentencias CREATE TABLE
        create_table_queries = [
            '''CREATE TABLE IF NOT EXISTS Campus (ID_Campus TEXT PRIMARY KEY, Nombre TEXT, Estado TEXT)''',
            '''CREATE TABLE IF NOT EXISTS Carrera (ID_Carrera TEXT PRIMARY KEY, Nombre TEXT, Estado TEXT)''',
            '''CREATE TABLE IF NOT EXISTS Carrera_Campus (ID_Carrera_Campus TEXT PRIMARY KEY, ID_Carrera TEXT, ID_Campus TEXT, FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus))'''

        ]

        for query in create_table_queries:
            cursor.execute(query)

        self.conn.commit()
        self._seed_data_if_empty()

    def _seed_data_if_empty(self):
        """Revisa si la base de datos está vacía y lo notifica."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Campus")
        if cursor.fetchone()[0] == 0:
            print("Base de datos vacía. Lista para ser poblada con datos reales.")
            # Aquí es donde irían los datos iniciales si quisieras agregarlos desde el código.
            # Por ahora, se deja vacía para que la llenes manualmente.
            self.conn.commit()

    def get_campus(self):
        """Obtiene todos los campus."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Campus, Nombre FROM Campus WHERE Estado = 'Activo'")
        # Convierte los resultados en una lista de diccionarios
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_nombres_carrera_por_id_campus(self, id_campus):
        """Obtiene los nombres de las carreras para un campus específico (forma optimizada)."""
        cursor = self.conn.cursor()
        # Usamos un JOIN para hacer una sola consulta eficiente
        query = """
            SELECT c.Nombre
            FROM Carrera_Campus cc
            JOIN Carrera c ON cc.ID_Carrera = c.ID_Carrera
            WHERE cc.ID_Campus = ? AND c.Estado = 'Activo'
        """
        cursor.execute(query, (id_campus,))
        rows = cursor.fetchall()
        # Devuelve una lista de nombres, ej: ['Ingeniería de Software', 'Diseño Gráfico']
        return [row['Nombre'] for row in rows]

    def get_id_carrera_by_nombre(self, nombre_carrera):
        """Obtiene el ID de una carrera a partir de su nombre."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Carrera FROM Carrera WHERE Nombre = ?", (nombre_carrera,))
        result = cursor.fetchone()
        return result['ID_Carrera'] if result else None