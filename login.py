import os

ARCHIVO = "tareas.txt"


def cargar_tareas():
    if not os.path.exists(ARCHIVO):
        return []

    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        return [linea.strip() for linea in archivo.readlines()]


def guardar_tareas(tareas):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        for tarea in tareas:
            archivo.write(tarea + "\n")


def mostrar_tareas(tareas):
    if not tareas:
        print("\nNo hay tareas registradas.\n")
        return

    print("\n=== LISTA DE TAREAS ===")
    for i, tarea in enumerate(tareas, start=1):
        print(f"{i}. {tarea}")
    print()


def agregar_tarea(tareas):
    tarea = input("Ingrese una nueva tarea: ")
    tareas.append(tarea)
    guardar_tareas(tareas)
    print("Tarea agregada correctamente.\n")


def eliminar_tarea(tareas):
    mostrar_tareas(tareas)

    if not tareas:
        return

    try:
        indice = int(input("Número de tarea a eliminar: ")) - 1

        if 0 <= indice < len(tareas):
            eliminada = tareas.pop(indice)
            guardar_tareas(tareas)
            print(f"Tarea '{eliminada}' eliminada.\n")
        else:
            print("Número inválido.\n")
    except ValueError:
        print("Debe ingresar un número.\n")


def menu():
    tareas = cargar_tareas()

    while True:
        print("====== GESTOR DE TAREAS ======")
        print("1. Ver tareas")
        print("2. Agregar tarea")
        print("3. Eliminar tarea")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            mostrar_tareas(tareas)
        elif opcion == "2":
            agregar_tarea(tareas)
        elif opcion == "3":
            eliminar_tarea(tareas)
        elif opcion == "4":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.\n")


if __name__ == "__main__":
    menu()