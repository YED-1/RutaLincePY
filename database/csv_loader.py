import csv
from pathlib import Path
from database import DatabaseHelper


class CsvLoader:
    # Usamos pathlib para definir la ruta base de forma segura y moderna.
    _BASE_PATH = Path("assets/csv/")

    @staticmethod
    def _load_generic_csv(db: DatabaseHelper, table_name: str, file_name: str, type_conversions: dict = None):
        """
        Método genérico para leer un CSV, convertir tipos de datos y cargarlo en la BD.
        - type_conversions: Un diccionario que mapea nombres de columna a un tipo (ej. {'Cantidad': int}).
        """
        if type_conversions is None:
            type_conversions = {}

        file_path = CsvLoader._BASE_PATH / file_name

        if not file_path.exists():
            print(f"Error: No se pudo encontrar el archivo en la ruta '{file_path}'.")
            return

        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                processed_rows = []
                for row in reader:
                    # Aplica las conversiones de tipo especificadas
                    for column, type_func in type_conversions.items():
                        if column in row:
                            value = row[column]
                            try:
                                # Convierte el valor si no está vacío, sino lo deja como 0 o 0.0
                                row[column] = type_func(value) if value else (0.0 if type_func is float else 0)
                            except (ValueError, TypeError):
                                print(
                                    f"Advertencia: No se pudo convertir '{value}' para la columna '{column}' en {file_name}. Usando valor por defecto.")
                                row[column] = 0.0 if type_func is float else 0

                    # Maneja valores que deben ser NULL (ej. foreign keys opcionales)
                    for key, value in row.items():
                        if value == '':
                            row[key] = None

                    processed_rows.append(row)

            # Inserta todos los datos en una transacción para mayor eficiencia
            print(f"Cargando datos desde '{file_name}' en la tabla '{table_name}'...")
            for row_data in processed_rows:
                db.insert_data(table_name, row_data)
            print(f"-> Datos de '{file_name}' cargados exitosamente.")

        except Exception as e:
            print(f"Ocurrió un error inesperado al cargar '{file_name}': {e}")

    # --- Métodos públicos para cargar cada archivo ---
    # Cada uno define las conversiones de tipo que necesita.

    @staticmethod
    def load_campus(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Campus', 'campus.csv')

    @staticmethod
    def load_carrera(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Carrera', 'carrera.csv')

    @staticmethod
    def load_carrera_campus(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Carrera_Campus', 'carrera_campus.csv')

    @staticmethod
    def load_video(db: DatabaseHelper):
        conversions = {'Duración': int, 'Visualizaciones': int, 'Cantidad_Likes': int, 'Cantidad_Dislikes': int}
        CsvLoader._load_generic_csv(db, 'Video', 'video.csv', type_conversions=conversions)

    @staticmethod
    def load_area(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Area', 'area.csv')

    @staticmethod
    def load_pregunta(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Pregunta', 'pregunta.csv')

    @staticmethod
    def load_comentario(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Comentario', 'comentario.csv')

    @staticmethod
    def load_simulador(db: DatabaseHelper):
        conversions = {'Longitud': int}
        CsvLoader._load_generic_csv(db, 'Simulador', 'simulador.csv', type_conversions=conversions)

    @staticmethod
    def load_crucigrama(db: DatabaseHelper):
        conversions = {'Cantidad_Palabras': int}
        CsvLoader._load_generic_csv(db, 'Crucigrama', 'crucigrama.csv', type_conversions=conversions)

    @staticmethod
    def load_sopa(db: DatabaseHelper):
        conversions = {'Cantidad_Palabras': int}
        CsvLoader._load_generic_csv(db, 'Sopa', 'sopa.csv', type_conversions=conversions)

    @staticmethod
    def load_palabra(db: DatabaseHelper):
        conversions = {'Longitud': int}
        CsvLoader._load_generic_csv(db, 'Palabra', 'palabra.csv', type_conversions=conversions)

    @staticmethod
    def load_tema(db: DatabaseHelper):
        CsvLoader._load_generic_csv(db, 'Tema', 'tema.csv')

    @staticmethod
    def load_resultado(db: DatabaseHelper):
        conversions = {'Calificacion': float, 'Tiempo': int}
        CsvLoader._load_generic_csv(db, 'Resultado', 'resultado.csv', type_conversions=conversions)

    @staticmethod
    def load_all_data(db: DatabaseHelper):
        """
        Un método maestro para ejecutar toda la carga de datos inicial con una sola llamada.
        El orden es importante por las llaves foráneas (foreign keys).
        """
        print("--- Iniciando carga masiva de datos desde archivos CSV ---")
        CsvLoader.load_campus(db)
        CsvLoader.load_carrera(db)
        CsvLoader.load_carrera_campus(db)
        CsvLoader.load_area(db)
        CsvLoader.load_tema(db)
        CsvLoader.load_video(db)
        CsvLoader.load_pregunta(db)
        CsvLoader.load_comentario(db)

        CsvLoader.load_simulador(db)
        CsvLoader.load_crucigrama(db)
        CsvLoader.load_sopa(db)
        CsvLoader.load_palabra(db)
        CsvLoader.load_resultado(db)
        print("--- Carga masiva de datos finalizada. ---")


# --- Ejemplo de cómo usarías este archivo ---
if __name__ == '__main__':
    db_instance = DatabaseHelper()
    CsvLoader.load_all_data(db_instance)