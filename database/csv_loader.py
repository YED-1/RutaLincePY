import csv
import os
from pathlib import Path
from database.database import DatabaseHelper


class CsvLoader:
    @staticmethod
    async def load_campus(db: DatabaseHelper):
        """Carga datos de campus desde CSV"""
        csv_path = Path("assets/csv/campus.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar header

            for row in reader:
                if len(row) >= 3:
                    await db.insert_campus({
                        'ID_Campus': row[0],
                        'Nombre': row[1],
                        'Estado': row[2]
                    })

    @staticmethod
    async def load_carrera(db: DatabaseHelper):
        """Carga datos de carrera desde CSV"""
        csv_path = Path("assets/csv/carrera.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 3:
                    await db.insert_carrera({
                        'ID_Carrera': row[0],
                        'Nombre': row[1],
                        'Estado': row[2]
                    })

    @staticmethod
    async def load_carrera_campus(db: DatabaseHelper):
        """Carga datos de relación carrera-campus desde CSV"""
        csv_path = Path("assets/csv/carrera_campus.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 3:
                    await db.insert_carrera_campus({
                        'ID_Carrera_Campus': row[0],
                        'ID_Carrera': row[1],
                        'ID_Campus': row[2]
                    })

    @staticmethod
    async def load_area(db: DatabaseHelper):
        """Carga datos de área desde CSV"""
        csv_path = Path("assets/csv/area.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 4:
                    await db.insert_area({
                        'ID_Area': row[0],
                        'Nombre': row[1],
                        'Estado': row[2],
                        'ID_Carrera': row[3]
                    })

    @staticmethod
    async def load_video(db: DatabaseHelper):
        """Carga datos de video desde CSV"""
        csv_path = Path("assets/csv/video.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 10:
                    await db.insert_video({
                        'ID_Video': row[0],
                        'Nombre': row[1],
                        'Descripción': row[2],
                        'URL_Video': row[3],
                        'Duración': int(row[4]) if row[4] else 0,
                        'Visualizaciones': int(row[5]) if row[5] else 0,
                        'Cantidad_Likes': int(row[6]) if row[6] else 0,
                        'Cantidad_Dislikes': int(row[7]) if row[7] else 0,
                        'Estado': row[8],
                        'ID_Area': row[9]
                    })

    @staticmethod
    async def load_pregunta(db: DatabaseHelper):
        """Carga datos de pregunta desde CSV"""
        csv_path = Path("assets/csv/pregunta.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 11:
                    await db.insert_pregunta({
                        'ID_Pregunta': row[0],
                        'Pregunta': row[1],
                        'Opcion_A': row[2],
                        'Opcion_B': row[3],
                        'Opcion_C': row[4],
                        'Opcion_Correcta': row[5],
                        'Comentario': row[6],
                        'Estado': row[7],
                        'ID_Video': row[8] if row[8] else None,
                        'ID_Area': row[9],
                        'ID_Tema': row[10] if row[10] else None
                    })

    @staticmethod
    async def load_tema(db: DatabaseHelper):
        """Carga datos de tema desde CSV"""
        csv_path = Path("assets/csv/tema.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 4:
                    await db.insert_tema({
                        'ID_Tema': row[0],
                        'Nombre': row[1],
                        'ID_Area': row[2],
                        'Estado': row[3]
                    })

    @staticmethod
    async def load_comentario(db: DatabaseHelper):
        """Carga datos de comentario desde CSV"""
        csv_path = Path("assets/csv/comentario.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 6:
                    await db.insert_comentario({
                        'ID_Comentario': row[0],
                        'Comentario': row[1],
                        'Fecha': row[2],
                        'Estado': row[3],
                        'ID_Usuario': row[4],
                        'ID_Video': row[5]
                    })

    @staticmethod
    async def load_simulador(db: DatabaseHelper):
        """Carga datos de simulador desde CSV"""
        csv_path = Path("assets/csv/simulador.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 5:
                    await db.insert_simulador({
                        'ID_Simulador': row[0],
                        'Longitud': int(row[1]) if row[1] else 0,
                        'Estado': row[2],
                        'ID_Carrera': row[3],
                        'ID_Area': row[4]
                    })

    @staticmethod
    async def load_crucigrama(db: DatabaseHelper):
        """Carga datos de crucigrama desde CSV"""
        csv_path = Path("assets/csv/crucigrama.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 5:
                    await db.insert_crucigrama({
                        'ID_Crucigrama': row[0],
                        'Cantidad_Palabras': int(row[1]) if row[1] else 0,
                        'Estado': row[2],
                        'ID_Area': row[3],
                        'ID_Carrera': row[4]
                    })

    @staticmethod
    async def load_sopa(db: DatabaseHelper):
        """Carga datos de sopa de letras desde CSV"""
        csv_path = Path("assets/csv/sopa.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 5:
                    await db.insert_sopa({
                        'ID_Sopa': row[0],
                        'Cantidad_Palabras': int(row[1]) if row[1] else 0,
                        'Estado': row[2],
                        'ID_Area': row[3],
                        'ID_Carrera': row[4]
                    })

    @staticmethod
    async def load_palabra(db: DatabaseHelper):
        """Carga datos de palabra desde CSV"""
        csv_path = Path("assets/csv/palabra.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 8:
                    await db.insert_palabra({
                        'ID_Palabra': row[0],
                        'Longitud': int(row[1]) if row[1] else 0,
                        'Palabra': row[2],
                        'Descripción': row[3],
                        'Estado': row[4],
                        'ID_Area': row[5],
                        'ID_Sopa': row[6] if row[6] else None,
                        'ID_Crucigrama': row[7] if row[7] else None
                    })

    @staticmethod
    async def load_resultado(db: DatabaseHelper):
        """Carga datos de resultado desde CSV"""
        csv_path = Path("assets/csv/resultado.csv")

        if not csv_path.exists():
            print(f"Archivo no encontrado: {csv_path}")
            return

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if len(row) >= 7:
                    await db.insert_resultado({
                        'ID_Resultado': row[0],
                        'Calificacion': float(row[1]) if row[1] else 0.0,
                        'Tiempo': int(row[2]) if row[2] else 0,
                        'Fecha': row[3],
                        'ID_Tema': row[4],
                        'ID_Usuario': row[5],
                        'ID_Simulador': row[6]
                    })

    @staticmethod
    async def load_all_data(db: DatabaseHelper):
        """Carga todos los datos CSV en orden correcto"""
        print("Cargando datos desde CSV...")

        # Orden importante por dependencias de foreign keys
        await CsvLoader.load_campus(db)
        await CsvLoader.load_carrera(db)
        await CsvLoader.load_carrera_campus(db)
        await CsvLoader.load_area(db)
        await CsvLoader.load_tema(db)
        await CsvLoader.load_video(db)
        await CsvLoader.load_pregunta(db)
        await CsvLoader.load_simulador(db)
        await CsvLoader.load_crucigrama(db)
        await CsvLoader.load_sopa(db)
        await CsvLoader.load_palabra(db)
        await CsvLoader.load_comentario(db)
        await CsvLoader.load_resultado(db)

        print("Datos cargados exitosamente!")