import flet as ft
from src.database.database import DatabaseHelper
from src.screens.welcome_section.bienvenida_screen import WelcomeScreen
from src.screens.welcome_section.seleccion_carrera_screen import SeleccionCarreraScreen
from src.screens.inicio_screen import InicioScreen


def main(page: ft.Page):
    page.title = "Ruta Lince"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 800
    #page.client_storage.clear() #Borra la memoria y genera un nuevo cliente; comentar cuando se inicie un nuevo cliente; Solo usar para probar la app desde 0


    # --- LÓGICA DE ARRANQUE TRADUCIDA ---
    saved_campus_id = page.client_storage.get("idCampus")
    saved_carrera_id = page.client_storage.get("idCarrera")

    initial_screen = None
    if saved_campus_id and saved_carrera_id:
        print("INFO: Usuario ya configurado. Cargando InicioScreen.")
        initial_screen = InicioScreen(page, id_carrera=saved_carrera_id, id_campus=saved_campus_id)

    elif saved_campus_id:
        print("INFO: Usuario a medio configurar. Cargando SeleccionCarreraScreen.")
        db = DatabaseHelper()
        campus_data = db.get_campus_by_id(saved_campus_id)
        campus_nombre = campus_data['Nombre'] if campus_data else "Campus Desconocido"
        initial_screen = SeleccionCarreraScreen(page, id_campus=saved_campus_id, campus_nombre=campus_nombre)

    else:
        print("INFO: Nuevo usuario. Cargando WelcomeScreen.")
        initial_screen = WelcomeScreen(page)

    page.add(initial_screen)


# Asegúrate de que 'assets' esté en la raíz del proyecto (RutaLincePY/)
ft.app(target=main, assets_dir="../assets")
