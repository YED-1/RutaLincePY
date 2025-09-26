import sqlite3
import os
from pathlib import Path


class DatabaseHelper:
    _instance = None
    _database = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHelper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._database is None:
            self._database = self.init_db()

    def get_connection(self):
        """Obtiene la conexión a la base de datos"""
        return self._database

    def init_db(self):
        """Inicializa la base de datos y crea las tablas"""
        documents_path = Path.home() / "Documents"
        db_path = documents_path / "Migracion.db"

        documents_path.mkdir(exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")

        self.create_tables(conn)
        return conn

    def create_tables(self, conn):
        """Crea todas las tablas necesarias"""
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS Campus (
                ID_Campus TEXT(50) PRIMARY KEY,
                Nombre TEXT(100) NOT NULL,
                Estado TEXT(50) NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Carrera (
                ID_Carrera TEXT(50) PRIMARY KEY,
                Nombre TEXT(100) NOT NULL,
                Estado TEXT(50) NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Usuario (
                ID_Usuario TEXT(50) PRIMARY KEY,
                ID_Campus TEXT(100) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera),
                FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Carrera_Campus (
                ID_Carrera_Campus TEXT(50) PRIMARY KEY,
                ID_Carrera TEXT(50) NOT NULL,
                ID_Campus TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera),
                FOREIGN KEY (ID_Campus) REFERENCES Campus(ID_Campus)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Area (
                ID_Area TEXT(50) PRIMARY KEY,
                Nombre TEXT(100) NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Tema (
                ID_Tema TEXT(50) PRIMARY KEY,
                Nombre TEXT(100) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                Estado TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Video (
                ID_Video TEXT(50) PRIMARY KEY,
                Nombre TEXT(100) NOT NULL,
                Descripción TEXT(255) NOT NULL,
                URL_Video TEXT(255) NOT NULL,
                Duración INTEGER NOT NULL,
                Visualizaciones INTEGER NOT NULL,
                Cantidad_Likes INTEGER NOT NULL,
                Cantidad_Dislikes INTEGER NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Comentario (
                ID_Comentario TEXT(50) PRIMARY KEY,
                Comentario TEXT(255) NOT NULL,
                Fecha DATE NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Usuario TEXT(50) NOT NULL,
                ID_Video TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario),
                FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Reaccion (
                ID_Reaccion TEXT(50) PRIMARY KEY,
                Tipo TEXT(255) NOT NULL,
                Fecha DATE NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Video TEXT(50) NOT NULL,
                ID_Usuario TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video),
                FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Simulador (
                ID_Simulador TEXT(50) PRIMARY KEY,
                Longitud INTEGER NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Resultado (
                ID_Resultado TEXT(50) PRIMARY KEY,
                Calificacion INTEGER NOT NULL,
                Tiempo INTEGER NOT NULL,
                Fecha DATE NOT NULL,
                ID_Tema TEXT(50) NOT NULL,
                ID_Usuario TEXT(50) NOT NULL,
                ID_Simulador TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema),
                FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario),
                FOREIGN KEY (ID_Simulador) REFERENCES Simulador(ID_Simulador)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Pregunta (
                ID_Pregunta TEXT(50) PRIMARY KEY,
                Pregunta TEXT(255) NOT NULL,
                Opcion_A TEXT(255) NOT NULL,
                Opcion_B TEXT(255) NOT NULL,
                Opcion_C TEXT(255) NOT NULL,
                Opcion_Correcta TEXT(255) NOT NULL,
                Comentario TEXT(255) NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Video TEXT(50),
                ID_Area TEXT(50) NOT NULL,
                ID_Tema TEXT(50),
                FOREIGN KEY (ID_Video) REFERENCES Video(ID_Video),
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area),
                FOREIGN KEY (ID_Tema) REFERENCES Tema(ID_Tema)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Sopa (
                ID_Sopa TEXT(50) PRIMARY KEY,
                Cantidad_Palabras INTEGER NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera),
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Crucigrama (
                ID_Crucigrama TEXT(50) PRIMARY KEY,
                Cantidad_Palabras INTEGER NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                ID_Carrera TEXT(50) NOT NULL,
                FOREIGN KEY (ID_Carrera) REFERENCES Carrera(ID_Carrera),
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Palabra (
                ID_Palabra TEXT(50) PRIMARY KEY,
                Longitud INTEGER NOT NULL,
                Palabra TEXT(100) NOT NULL,
                Descripción TEXT(255) NOT NULL,
                Estado TEXT(50) NOT NULL,
                ID_Area TEXT(50) NOT NULL,
                ID_Sopa TEXT(50),
                ID_Crucigrama TEXT(50),
                FOREIGN KEY (ID_Area) REFERENCES Area(ID_Area),
                FOREIGN KEY (ID_Sopa) REFERENCES Sopa(ID_Sopa),
                FOREIGN KEY (ID_Crucigrama) REFERENCES Crucigrama(ID_Crucigrama)
            )
            '''
        ]

        for table in tables:
            conn.execute(table)

        conn.commit()

    # MÉTODOS DE INSERCIÓN
    async def insert_campus(self, campus):
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO Campus (ID_Campus, Nombre, Estado) VALUES (?, ?, ?)",
            (campus['ID_Campus'], campus['Nombre'], campus['Estado'])
        )
        conn.commit()

    async def insert_carrera(self, carrera):
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO Carrera (ID_Carrera, Nombre, Estado) VALUES (?, ?, ?)",
            (carrera['ID_Carrera'], carrera['Nombre'], carrera['Estado'])
        )
        conn.commit()

    async def insert_carrera_campus(self, carrera_campus):
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO Carrera_Campus (ID_Carrera_Campus, ID_Carrera, ID_Campus) VALUES (?, ?, ?)",
            (carrera_campus['ID_Carrera_Campus'], carrera_campus['ID_Carrera'], carrera_campus['ID_Campus'])
        )
        conn.commit()

    async def insert_area(self, area):
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO Area (ID_Area, Nombre, Estado, ID_Carrera) VALUES (?, ?, ?, ?)",
            (area['ID_Area'], area['Nombre'], area['Estado'], area['ID_Carrera'])
        )
        conn.commit()

    async def insert_video(self, video):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Video 
            (ID_Video, Nombre, Descripción, URL_Video, Duración, Visualizaciones, Cantidad_Likes, Cantidad_Dislikes, Estado, ID_Area) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (video['ID_Video'], video['Nombre'], video['Descripción'], video['URL_Video'],
             video['Duración'], video['Visualizaciones'], video['Cantidad_Likes'],
             video['Cantidad_Dislikes'], video['Estado'], video['ID_Area'])
        )
        conn.commit()

    async def insert_pregunta(self, pregunta):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Pregunta 
            (ID_Pregunta, Pregunta, Opcion_A, Opcion_B, Opcion_C, Opcion_Correcta, Comentario, Estado, ID_Video, ID_Area, ID_Tema) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (pregunta['ID_Pregunta'], pregunta['Pregunta'], pregunta['Opcion_A'],
             pregunta['Opcion_B'], pregunta['Opcion_C'], pregunta['Opcion_Correcta'],
             pregunta['Comentario'], pregunta['Estado'], pregunta['ID_Video'],
             pregunta['ID_Area'], pregunta['ID_Tema'])
        )
        conn.commit()

    async def insert_tema(self, tema):
        conn = self.get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO Tema (ID_Tema, Nombre, ID_Area, Estado) VALUES (?, ?, ?, ?)",
            (tema['ID_Tema'], tema['Nombre'], tema['ID_Area'], tema['Estado'])
        )
        conn.commit()

    async def insert_comentario(self, comentario):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Comentario 
            (ID_Comentario, Comentario, Fecha, Estado, ID_Usuario, ID_Video) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (comentario['ID_Comentario'], comentario['Comentario'], comentario['Fecha'],
             comentario['Estado'], comentario['ID_Usuario'], comentario['ID_Video'])
        )
        conn.commit()

    async def insert_simulador(self, simulador):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Simulador 
            (ID_Simulador, Longitud, Estado, ID_Carrera, ID_Area) 
            VALUES (?, ?, ?, ?, ?)""",
            (simulador['ID_Simulador'], simulador['Longitud'], simulador['Estado'],
             simulador['ID_Carrera'], simulador['ID_Area'])
        )
        conn.commit()

    async def insert_crucigrama(self, crucigrama):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Crucigrama 
            (ID_Crucigrama, Cantidad_Palabras, Estado, ID_Area, ID_Carrera) 
            VALUES (?, ?, ?, ?, ?)""",
            (crucigrama['ID_Crucigrama'], crucigrama['Cantidad_Palabras'], crucigrama['Estado'],
             crucigrama['ID_Area'], crucigrama['ID_Carrera'])
        )
        conn.commit()

    async def insert_sopa(self, sopa):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Sopa 
            (ID_Sopa, Cantidad_Palabras, Estado, ID_Area, ID_Carrera) 
            VALUES (?, ?, ?, ?, ?)""",
            (sopa['ID_Sopa'], sopa['Cantidad_Palabras'], sopa['Estado'],
             sopa['ID_Area'], sopa['ID_Carrera'])
        )
        conn.commit()

    async def insert_palabra(self, palabra):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Palabra 
            (ID_Palabra, Longitud, Palabra, Descripción, Estado, ID_Area, ID_Sopa, ID_Crucigrama) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (palabra['ID_Palabra'], palabra['Longitud'], palabra['Palabra'], palabra['Descripción'],
             palabra['Estado'], palabra['ID_Area'], palabra['ID_Sopa'], palabra['ID_Crucigrama'])
        )
        conn.commit()

    async def insert_resultado(self, resultado):
        conn = self.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO Resultado 
            (ID_Resultado, Calificacion, Tiempo, Fecha, ID_Tema, ID_Usuario, ID_Simulador) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (resultado['ID_Resultado'], resultado['Calificacion'], resultado['Tiempo'], resultado['Fecha'],
             resultado['ID_Tema'], resultado['ID_Usuario'], resultado['ID_Simulador'])
        )
        conn.commit()

    # MÉTODOS DE CONSULTA (GET ALL)
    async def get_campus(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Campus")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_carrera(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Carrera")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_carrera_campus(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Carrera_Campus")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_video(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Video")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_area(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Area")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_pregunta(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Pregunta")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_comentario(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Comentario")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_simulador(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Simulador")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_crucigrama(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Crucigrama")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_sopa(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Sopa")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_palabra(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Palabra")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_usuario(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Usuario")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_tema(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Tema")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    async def get_resultado(self):
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM Resultado")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # MÉTODOS ESPECÍFICOS PARA LA APLICACIÓN
    async def get_nombres_carrera_por_id_campus(self, id_campus):
        conn = self.get_connection()

        cursor = conn.execute(
            "SELECT ID_Carrera FROM Carrera_Campus WHERE ID_Campus = ?",
            (id_campus,)
        )
        resultados = cursor.fetchall()

        if not resultados:
            return []

        nombres_carreras = []
        for resultado in resultados:
            id_carrera = resultado[0]
            cursor_carrera = conn.execute(
                "SELECT Nombre FROM Carrera WHERE ID_Carrera = ?",
                (id_carrera,)
            )
            carrera_result = cursor_carrera.fetchone()
            if carrera_result:
                nombres_carreras.append(carrera_result[0])

        return nombres_carreras

    async def get_id_carrera_by_nombre(self, nombre_carrera):
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT ID_Carrera FROM Carrera WHERE Nombre = ?",
            (nombre_carrera,)
        )
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            raise Exception('Carrera no encontrada')

    async def insert_or_update_usuario(self, id_usuario, id_campus, id_carrera):
        conn = self.get_connection()

        cursor = conn.execute(
            "SELECT * FROM Usuario WHERE ID_Usuario = ?",
            (id_usuario,)
        )
        existe = cursor.fetchone()

        if existe:
            conn.execute(
                "UPDATE Usuario SET ID_Campus = ?, ID_Carrera = ? WHERE ID_Usuario = ?",
                (id_campus, id_carrera, id_usuario)
            )
        else:
            conn.execute(
                "INSERT INTO Usuario (ID_Usuario, ID_Campus, ID_Carrera) VALUES (?, ?, ?)",
                (id_usuario, id_campus, id_carrera)
            )

        conn.commit()