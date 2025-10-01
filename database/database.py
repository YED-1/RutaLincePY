import sqlite3

class DatabaseHelper:
    _instance = None
    _database_name = "lince_data.db"

    # Implementación del patrón Singleton para asegurar una única instancia
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHelper, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(cls._database_name, check_same_thread=False)

            # Esto permite que los resultados de las consultas sean como diccionarios
            cls._instance.conn.row_factory = sqlite3.Row

            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Inicializa el esquema de la base de datos si no existe."""
        cursor = self.conn.cursor()

        # Se agrupan todas las sentencias CREATE TABLE para ejecutarlas una sola vez.
        script = '''
            CREATE TABLE IF NOT EXISTS Campus (
                ID_Campus TEXT(50) PRIMARY KEY, Nombre TEXT(100) NOT NULL, Estado TEXT(50) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Carrera (
                ID_Carrera TEXT(50) PRIMARY KEY, Nombre TEXT(100) NOT NULL, Estado TEXT(50) NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Usuario (
                ID_Usuario TEXT(50) PRIMARY KEY, ID_Campus TEXT(100) NOT NULL, ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus)
            );
            CREATE TABLE IF NOT EXISTS Carrera_Campus (
                ID_Carrera_Campus TEXT(50) PRIMARY KEY, ID_Carrera TEXT(50) NOT NULL, ID_Campus TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus)
            );
            CREATE TABLE IF NOT EXISTS Area (
                ID_Area TEXT(50) PRIMARY KEY, Nombre TEXT(100) NOT NULL, Estado TEXT(50) NOT NULL, ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera)
            );
            CREATE TABLE IF NOT EXISTS Tema (
                ID_Tema TEXT(50) PRIMARY KEY, Nombre TEXT(100) NOT NULL, ID_Area TEXT(50) NOT NULL, Estado TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            );
            CREATE TABLE IF NOT EXISTS Video (
                ID_Video TEXT(50) PRIMARY KEY, Nombre TEXT(100) NOT NULL, Descripción TEXT(255) NOT NULL, URL_Video TEXT(255) NOT NULL,
                Duración INTEGER NOT NULL, Visualizaciones INTEGER NOT NULL, Cantidad_Likes INTEGER NOT NULL, Cantidad_Dislikes INTEGER NOT NULL,
                Estado TEXT(50) NOT NULL, ID_Area TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            );
            CREATE TABLE IF NOT EXISTS Comentario (
                ID_Comentario TEXT(50) PRIMARY KEY, Comentario TEXT(255) NOT NULL, Fecha DATE NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Usuario TEXT(50) NOT NULL, ID_Video TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario), FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video)
            );
            CREATE TABLE IF NOT EXISTS Reaccion (
                ID_Reaccion TEXT(50) PRIMARY KEY, Tipo TEXT(255) NOT NULL, Fecha DATE NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Video TEXT(50) NOT NULL, ID_Usuario TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video), FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario)
            );
            CREATE TABLE IF NOT EXISTS Simulador (
                ID_Simulador TEXT(50) PRIMARY KEY, Longitud INTEGER NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL, ID_Area TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera)
            );
            CREATE TABLE IF NOT EXISTS Resultado (
                ID_Resultado TEXT(50) PRIMARY KEY, Calificacion INTEGER NOT NULL, Tiempo INTEGER NOT NULL, Fecha DATE NOT NULL,
                ID_Tema TEXT(50) NOT NULL, ID_Usuario TEXT(50) NOT NULL, ID_Simulador TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema), FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario),
                FOREIGN KEY (ID_Simulador) REFERENCES Simulador(ID_Simulador)
            );
            CREATE TABLE IF NOT EXISTS Pregunta (
                ID_Pregunta TEXT(50) PRIMARY KEY, Pregunta TEXT(255) NOT NULL, Opcion_A TEXT(255) NOT NULL, Opcion_B TEXT(255) NOT NULL,
                Opcion_C TEXT(255) NOT NULL, Opcion_Correcta TEXT(255) NOT NULL, Comentario TEXT(255) NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Video TEXT(50), ID_Area TEXT(50) NOT NULL, ID_Tema TEXT(50),
                FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area),
                FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema)
            );
            CREATE TABLE IF NOT EXISTS Sopa (
                ID_Sopa TEXT(50) PRIMARY KEY, Cantidad_Palabras INTEGER NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL, ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            );
            CREATE TABLE IF NOT EXISTS Crucigrama (
                ID_Crucigrama TEXT(50) PRIMARY KEY, Cantidad_Palabras INTEGER NOT NULL, Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL, ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera), FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            );
            CREATE TABLE IF NOT EXISTS Palabra (
                ID_Palabra TEXT(50) PRIMARY KEY, Longitud INTEGER NOT NULL, Palabra TEXT(100) NOT NULL, Descripción TEXT(255) NOT NULL,
                Estado TEXT(50) NOT NULL, ID_Area TEXT(50) NOT NULL, ID_Sopa TEXT(50), ID_Crucigrama TEXT(50),
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area), FOREIGN KEY (ID_Sopa) REFERENCES Sopa(ID_Sopa),
                FOREIGN KEY (ID_Crucigrama) REFERENCES Crucigrama(ID_Crucigrama)
            );
        '''
        cursor.executescript(script)
        self.conn.commit()
        cursor.close()

    def _execute_query(self, query, params=(), fetch_one=False):
        """Método genérico para ejecutar consultas SELECT."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        # Por defecto, devuelve todos los resultados (fetchall)
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def _execute_modification(self, query, params=()):
        """Método genérico para ejecutar INSERT, UPDATE, DELETE."""
        with self.conn:
            self.conn.execute(query, params)

    # --- Métodos Genéricos para Insert y Get ---

    def insert_data(self, table_name, data):
        """Inserta un diccionario de datos. Reemplaza si la PK ya existe."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
        self._execute_modification(query, tuple(data.values()))

    def get_all_data(self, table_name):
        """Obtiene todos los registros de una tabla."""
        return self._execute_query(f"SELECT * FROM {table_name}")

    # --- Métodos de la App (Traducción 1 a 1) ---

    def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        user = self._execute_query("SELECT ID_Usuario FROM Usuario WHERE ID_Usuario = ?", (id_usuario,), fetch_one=True)
        if user:
            query = "UPDATE Usuario SET ID_Campus = ?, ID_Carrera = ? WHERE ID_Usuario = ?"
            self._execute_modification(query, (id_campus, id_carrera, id_usuario))
        else:
            data = {'ID_Usuario': id_usuario, 'ID_Campus': id_campus, 'ID_Carrera': id_carrera}
            self.insert_data('Usuario', data)

    def get_usuario(self):
        return self.get_all_data('Usuario')

    def palabra_crucigrama(self, id_crucigrama):
        query = "SELECT Palabra, Descripción FROM Palabra WHERE ID_Crucigrama = ? ORDER BY RANDOM() LIMIT 1"
        result = self._execute_query(query, (id_crucigrama,), fetch_one=True)
        if not result:
            raise Exception('No se encontró una palabra activa')
        return {'palabra': result['Palabra'], 'descripcion': result['Descripción']}

    def get_nombres_carrera_por_id_campus(self, id_campus):
        query = """
            SELECT C.Nombre FROM Carrera C
            JOIN Carrera_Campus CC ON C.ID_Carrera = CC.ID_Carrera
            WHERE CC.ID_Campus = ?
        """
        results = self._execute_query(query, (id_campus,))
        return [row['Nombre'] for row in results]

    def get_videos_by_id_area(self, area_id):
        return self._execute_query("SELECT * FROM Video WHERE ID_Area = ?", (area_id,))

    def get_simulador_by_id_carrera(self, carrera_id):
        return self._execute_query("SELECT * FROM Simulador WHERE ID_Carrera = ?", (carrera_id,))

    def get_sopa_by_id_carrera(self, carrera_id):
        return self._execute_query("SELECT * FROM Sopa WHERE ID_Carrera = ?", (carrera_id,))

    def get_crucigrama_by_id_carrera(self, carrera_id):
        return self._execute_query("SELECT * FROM Crucigrama WHERE ID_Carrera = ?", (carrera_id,))

    def get_nombre_area_by_id_area(self, id_area):
        result = self._execute_query("SELECT Nombre FROM Area WHERE ID_Area = ?", (id_area,), fetch_one=True)
        return result['Nombre'] if result else None

    def get_palabras_por_sopa(self, id_sopa):
        results = self._execute_query("SELECT Palabra FROM Palabra WHERE ID_Sopa = ?", (id_sopa,))
        return [row['Palabra'] for row in results]

    def get_palabras_por_crucigrama(self, id_crucigrama):
        results = self._execute_query("SELECT Palabra FROM Palabra WHERE ID_Crucigrama = ?", (id_crucigrama,))
        return [row['Palabra'] for row in results]

    def get_preguntas_by_id_area(self, area_id):
        return self._execute_query("SELECT * FROM Pregunta WHERE ID_Area = ?", (area_id,))

    def get_preguntas_por_id_area_activo(self, id_area):
        query = """
            SELECT ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_Correcta, Comentario, ID_Tema 
            FROM Pregunta 
            WHERE ID_Area = ? AND Estado = ? AND ID_Tema != ?
        """
        return self._execute_query(query, (id_area, 'Activo', 'No aplica'))

    def guardar_calificacion_por_tema(self, id_usuario, id_tema, calificacion, id_simulador, tiempo, fecha,
                                      id_resultado):
        params = (id_usuario, id_tema, id_simulador)
        resultado = self._execute_query(
            "SELECT * FROM Resultado WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?", params, fetch_one=True)

        if resultado:
            query = "UPDATE Resultado SET Calificacion = ?, Tiempo = ? WHERE ID_Usuario = ? AND ID_Tema = ? AND ID_Simulador = ?"
            self._execute_modification(query, (calificacion, tiempo) + params)
        else:
            data = {
                'ID_Resultado': id_resultado, 'Calificacion': calificacion, 'Tiempo': tiempo,
                'Fecha': fecha, 'ID_Tema': id_tema, 'ID_Usuario': id_usuario, 'ID_Simulador': id_simulador
            }
            self.insert_data('Resultado', data)

    def get_nombres_temas_por_ids(self, ids_tema):
        if not ids_tema: return {}
        placeholders = ','.join(['?'] * len(ids_tema))
        query = f"SELECT ID_Tema, Nombre FROM Tema WHERE ID_Tema IN ({placeholders})"
        results = self._execute_query(query, tuple(ids_tema))
        return {row['ID_Tema']: row['Nombre'] for row in results}

    def get_comments_by_id_video(self, video_id):
        return self._execute_query("SELECT * FROM Comentario WHERE ID_Video = ?", (video_id,))

    def get_video_data_by_id_video(self, video_id):
        return self._execute_query("SELECT * FROM Video WHERE ID_Video = ?", (video_id,))

    def get_id_carrera_by_nombre(self, nombre_carrera):
        result = self._execute_query("SELECT ID_Carrera FROM Carrera WHERE Nombre = ?", (nombre_carrera,),
                                     fetch_one=True)
        if not result:
            raise Exception('Carrera no encontrada')
        return result['ID_Carrera']

    def get_preguntas_por_id_video(self, id_video):
        query = "SELECT Pregunta, Opcion_A, Opcion_B, Opcion_Correcta, Comentario FROM Pregunta WHERE ID_Video = ?"
        return self._execute_query(query, (id_video,))

    def get_areas_id_carrera(self, id_carrera):
        return self._execute_query("SELECT ID_Area, Nombre FROM Area WHERE ID_Carrera = ?", (id_carrera,))

    def get_campus_by_id(self, id_campus):
        result = self._execute_query("SELECT * FROM Campus WHERE ID_Campus = ?", (id_campus,), fetch_one=True)
        if not result:
            raise Exception('Campus no encontrado')
        return result

    def get_carrera_by_id(self, id_carrera):
        result = self._execute_query("SELECT * FROM Carrera WHERE ID_Carrera = ?", (id_carrera,), fetch_one=True)
        if not result:
            raise Exception('Carrera no encontrada')
        return result

    def incrementar_visualizacion(self, video_id):
        query = "UPDATE Video SET Visualizaciones = Visualizaciones + 1 WHERE ID_Video = ?"
        self._execute_modification(query, (video_id,))


# Ejemplo de cómo usar la clase:
if __name__ == '__main__':
    db = DatabaseHelper()  # Se crea la instancia (y la bd si no existe)

    # Ejemplo de inserción
    # db.insert_data('Campus', {'ID_Campus': 'C01', 'Nombre': 'Campus Central', 'Estado': 'Activo'})

    # Ejemplo de consulta
    # all_campus = db.get_all_data('Campus')
    # print(all_campus)