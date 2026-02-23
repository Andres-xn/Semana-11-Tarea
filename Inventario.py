import os
import csv


class Producto:
    """
    Clase que representa un producto del inventario.
    """

    def __init__(self, codigo, nombre, cantidad, precio):
        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.cantidad = int(cantidad)
        self.precio = float(precio)

    def __str__(self):
        return f"Código: {self.codigo} | Nombre: {self.nombre} | Cantidad: {self.cantidad} | Precio: ${self.precio:.2f}"


class Inventario:
    """
    Gestiona productos en memoria y su persistencia en un archivo CSV.
    """

    def __init__(self, archivo="inventario.csv"):
        self.archivo = archivo
        self.productos = {}  # clave: código, valor: Producto
        self.cargar_desde_csv()

    def crear_csv_si_no_existe(self):
        """
        Crea el archivo CSV con encabezados si no existe.
        """
        if not os.path.exists(self.archivo):
            try:
                with open(self.archivo, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["codigo", "nombre", "cantidad", "precio"])
                print(f"[INFO] Archivo '{self.archivo}' creado correctamente.")
            except PermissionError:
                print(f"[ERROR] No tienes permisos para crear '{self.archivo}'.")
            except Exception as e:
                print(f"[ERROR] Error al crear el archivo CSV: {e}")

    def cargar_desde_csv(self):
        """
        Carga el inventario desde el archivo CSV.
        Si no existe, lo crea automáticamente.
        Maneja líneas corruptas y errores de permisos.
        """
        self.crear_csv_si_no_existe()

        try:
            with open(self.archivo, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # Validar encabezados esperados
                encabezados_esperados = {"codigo", "nombre", "cantidad", "precio"}
                if reader.fieldnames is None:
                    print("[ADVERTENCIA] El archivo CSV está vacío o sin encabezados. Se mantendrá vacío.")
                    return

                if set(reader.fieldnames) != encabezados_esperados:
                    print("[ADVERTENCIA] Encabezados CSV inválidos. Se esperaba: codigo,nombre,cantidad,precio")
                    print(f"[ADVERTENCIA] Encabezados encontrados: {reader.fieldnames}")
                    return

                cargados = 0
                for i, fila in enumerate(reader, start=2):  # empieza en 2 por encabezado
                    try:
                        codigo = fila["codigo"]
                        nombre = fila["nombre"]
                        cantidad = int(fila["cantidad"])
                        precio = float(fila["precio"])

                        producto = Producto(codigo, nombre, cantidad, precio)
                        self.productos[producto.codigo] = producto
                        cargados += 1
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"[ADVERTENCIA] Fila {i} corrupta ignorada: {e}")
                    except Exception as e:
                        print(f"[ADVERTENCIA] Error inesperado en fila {i}: {e}")

                print(f"[INFO] Inventario cargado con {cargados} producto(s) desde CSV.")

        except FileNotFoundError:
            print(f"[ERROR] No se encontró el archivo '{self.archivo}'.")
        except PermissionError:
            print(f"[ERROR] No tienes permisos para leer '{self.archivo}'.")
        except Exception as e:
            print(f"[ERROR] Error al cargar CSV: {e}")

    def guardar_en_csv(self):
        """
        Guarda TODO el inventario al archivo CSV.
        Reescribe el archivo para mantener consistencia.
        """
        try:
            with open(self.archivo, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["codigo", "nombre", "cantidad", "precio"])

                for producto in self.productos.values():
                    writer.writerow([
                        producto.codigo,
                        producto.nombre,
                        producto.cantidad,
                        producto.precio
                    ])

            return True, "Inventario guardado correctamente en CSV."

        except PermissionError:
            return False, "No tienes permisos de escritura en el archivo CSV."
        except Exception as e:
            return False, f"Error al guardar en CSV: {e}"

    def agregar_producto(self, codigo, nombre, cantidad, precio):
        """
        Agrega un producto y guarda cambios en CSV.
        """
        if codigo in self.productos:
            return False, f"Ya existe un producto con código '{codigo}'."

        try:
            nuevo = Producto(codigo, nombre, cantidad, precio)

            if nuevo.cantidad < 0:
                return False, "La cantidad no puede ser negativa."
            if nuevo.precio < 0:
                return False, "El precio no puede ser negativo."

            self.productos[nuevo.codigo] = nuevo
            ok, msg = self.guardar_en_csv()

            if ok:
                return True, f"Producto agregado exitosamente. {msg}"
            else:
                # Revertir en memoria si falla escritura
                del self.productos[nuevo.codigo]
                return False, f"No se pudo guardar en CSV. {msg}"

        except ValueError:
            return False, "Cantidad y precio deben ser numéricos válidos."
        except Exception as e:
            return False, f"Error inesperado al agregar producto: {e}"

    def actualizar_producto(self, codigo, nombre=None, cantidad=None, precio=None):
        """
        Actualiza un producto existente y guarda en CSV.
        """
        if codigo not in self.productos:
            return False, f"No existe producto con código '{codigo}'."

        producto = self.productos[codigo]
        respaldo = Producto(producto.codigo, producto.nombre, producto.cantidad, producto.precio)

        try:
            if nombre is not None and str(nombre).strip():
                producto.nombre = nombre.strip()

            if cantidad is not None and str(cantidad).strip():
                nueva_cantidad = int(cantidad)
                if nueva_cantidad < 0:
                    return False, "La cantidad no puede ser negativa."
                producto.cantidad = nueva_cantidad

            if precio is not None and str(precio).strip():
                nuevo_precio = float(precio)
                if nuevo_precio < 0:
                    return False, "El precio no puede ser negativo."
                producto.precio = nuevo_precio

            ok, msg = self.guardar_en_csv()

            if ok:
                return True, f"Producto actualizado exitosamente. {msg}"
            else:
                self.productos[codigo] = respaldo
                return False, f"No se pudo guardar la actualización. {msg}"

        except ValueError:
            return False, "Cantidad y precio deben ser numéricos válidos."
        except Exception as e:
            self.productos[codigo] = respaldo
            return False, f"Error inesperado al actualizar producto: {e}"

    def eliminar_producto(self, codigo):
        """
        Elimina un producto y guarda cambios en CSV.
        """
        if codigo not in self.productos:
            return False, f"No existe producto con código '{codigo}'."

        respaldo = self.productos[codigo]

        try:
            del self.productos[codigo]
            ok, msg = self.guardar_en_csv()

            if ok:
                return True, f"Producto eliminado exitosamente. {msg}"
            else:
                self.productos[codigo] = respaldo
                return False, f"No se pudo guardar la eliminación. {msg}"

        except Exception as e:
            self.productos[codigo] = respaldo
            return False, f"Error inesperado al eliminar producto: {e}"

    def buscar_producto(self, codigo):
        return self.productos.get(codigo)

    def mostrar_inventario(self):
        if not self.productos:
            print("\n[INFO] El inventario está vacío.\n")
            return

        print("\n========= INVENTARIO ACTUAL =========")
        for producto in self.productos.values():
            print(producto)
        print("=====================================\n")


def mostrar_menu():
    print("=== SISTEMA DE GESTIÓN DE INVENTARIOS (CSV) ===")
    print("1. Agregar producto")
    print("2. Actualizar producto")
    print("3. Eliminar producto")
    print("4. Buscar producto")
    print("5. Mostrar inventario")
    print("6. Salir")


def main():
    inventario = Inventario("inventario.csv")

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            print("\n--- Agregar producto ---")
            codigo = input("Código: ")
            nombre = input("Nombre: ")
            cantidad = input("Cantidad: ")
            precio = input("Precio: ")

            exito, mensaje = inventario.agregar_producto(codigo, nombre, cantidad, precio)
            print(f"[{'OK' if exito else 'ERROR'}] {mensaje}\n")

        elif opcion == "2":
            print("\n--- Actualizar producto ---")
            codigo = input("Código del producto a actualizar: ")

            if inventario.buscar_producto(codigo) is None:
                print("[ERROR] Producto no encontrado.\n")
                continue

            print("Deje en blanco lo que no desea cambiar.")
            nombre = input("Nuevo nombre: ")
            cantidad = input("Nueva cantidad: ")
            precio = input("Nuevo precio: ")

            exito, mensaje = inventario.actualizar_producto(
                codigo,
                nombre=nombre if nombre.strip() else None,
                cantidad=cantidad if cantidad.strip() else None,
                precio=precio if precio.strip() else None
            )
            print(f"[{'OK' if exito else 'ERROR'}] {mensaje}\n")

        elif opcion == "3":
            print("\n--- Eliminar producto ---")
            codigo = input("Código del producto a eliminar: ")
            exito, mensaje = inventario.eliminar_producto(codigo)
            print(f"[{'OK' if exito else 'ERROR'}] {mensaje}\n")

        elif opcion == "4":
            print("\n--- Buscar producto ---")
            codigo = input("Código del producto: ")
            producto = inventario.buscar_producto(codigo)

            if producto:
                print(f"[OK] Producto encontrado: {producto}\n")
            else:
                print("[INFO] Producto no encontrado.\n")

        elif opcion == "5":
            inventario.mostrar_inventario()

        elif opcion == "6":
            print("\n[INFO] Saliendo del sistema... ¡Hasta luego!")
            break

        else:
            print("[ERROR] Opción inválida. Intente nuevamente.\n")


if __name__ == "__main__":
    main()