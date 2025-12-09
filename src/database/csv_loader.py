import csv
import os


def populate_from_csv_if_empty(db_helper, conn):  # Recibe la conexión
    """
    Revisa si la base de datos está vacía y, de ser así, la puebla
    con los datos de los archivos CSV usando la conexión proporcionada.
    """
    cursor = conn.cursor()  # Usa la conexión recibida
    cursor.execute("SELECT COUNT(*) FROM Campus")
    if cursor.fetchone()[0] > 0:
        print("La base de datos ya contiene datos. No se cargará desde CSV.")
        return

    print("Base de datos vacía. Cargando datos desde archivos CSV...")

    csv_map = {
        'campus.csv': db_helper.insert_campus, 'carrera.csv': db_helper.insert_carrera,
        'carrera_campus.csv': db_helper.insert_carrera_campus, 'area.csv': db_helper.insert_area,
        'tema.csv': db_helper.insert_tema, 'video.csv': db_helper.insert_video,
        'pregunta.csv': db_helper.insert_pregunta, 'simulador.csv': db_helper.insert_simulador,
        'sopa.csv': db_helper.insert_sopa, 'crucigrama.csv': db_helper.insert_crucigrama,
        'palabra.csv': db_helper.insert_palabra,
    }

    csv_dir = os.path.join(db_helper.base_dir, '..', '..', 'assets', 'csv')
    print(f"\n>>> DEBUG: Buscando archivos CSV en la carpeta: {os.path.abspath(csv_dir)}\n")

    for file_name, insert_method in csv_map.items():
        file_path = os.path.join(csv_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    insert_method(row)
            print(f" - Datos de '{file_name}' cargados correctamente.")
        except FileNotFoundError:
            print(
                f" - ADVERTENCIA: No se encontró el archivo '{file_name}' en la ruta '{os.path.abspath(file_path)}'. Se omitirá.")
        except Exception as e:
            print(f" - ERROR al cargar '{file_name}': {e}")

    conn.commit()  # Usa la conexión recibida
    print("Carga de datos desde CSV completada.")