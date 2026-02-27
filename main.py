import json
import os


class Producto:
    """
    Representa un producto dentro del inventario.
    """

    def __init__(self, producto_id, nombre, cantidad, precio):
        self.__id = str(producto_id)
        self.__nombre = nombre.strip()
        self.__cantidad = int(cantidad)
        self.__precio = float(precio)

    # Getters
    def get_id(self):
        return self.__id

    def get_nombre(self):
        return self.__nombre

    def get_cantidad(self):
        return self.__cantidad

    def get_precio(self):
        return self.__precio

    # Setters
    def set_nombre(self, nuevo_nombre):
        self.__nombre = nuevo_nombre.strip()

    def set_cantidad(self, nueva_cantidad):
        if int(nueva_cantidad) < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        self.__cantidad = int(nueva_cantidad)

    def set_precio(self, nuevo_precio):
        if float(nuevo_precio) < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.__precio = float(nuevo_precio)

    def to_dict(self):
        """
        Convierte el objeto a diccionario para guardarlo en JSON.
        """
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "cantidad": self.__cantidad,
            "precio": self.__precio
        }

    def to_tuple(self):
        """
        Devuelve los datos del producto en forma de tupla.
        """
        return self.__id, self.__nombre, self.__cantidad, self.__precio

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto Producto desde un diccionario.
        """
        return Producto(
            data["id"],
            data["nombre"],
            data["cantidad"],
            data["precio"]
        )

    def __str__(self):
        return (
            f"ID: {self.__id} | "
            f"Nombre: {self.__nombre} | "
            f"Cantidad: {self.__cantidad} | "
            f"Precio: ${self.__precio:.2f}"
        )


class Inventario:
    """
    Gestiona los productos usando colecciones y almacenamiento en archivo.
    """

    def __init__(self, archivo="inventario.json"):
        # Diccionario principal: {id: Producto}
        self.productos = {}

        # Índice secundario por nombre: {nombre_en_minusculas: set(ids)}
        self.indice_nombres = {}

        self.archivo = archivo
        self.cargar_desde_archivo()

    def __actualizar_indice_nombre(self, producto):
        """
        Agrega el producto al índice por nombre.
        """
        nombre_clave = producto.get_nombre().lower()
        if nombre_clave not in self.indice_nombres:
            self.indice_nombres[nombre_clave] = set()
        self.indice_nombres[nombre_clave].add(producto.get_id())

    def __eliminar_del_indice_nombre(self, producto):
        """
        Elimina el producto del índice por nombre.
        """
        nombre_clave = producto.get_nombre().lower()
        if nombre_clave in self.indice_nombres:
            self.indice_nombres[nombre_clave].discard(producto.get_id())
            if len(self.indice_nombres[nombre_clave]) == 0:
                del self.indice_nombres[nombre_clave]

    def agregar_producto(self, producto):
        """
        Añade un nuevo producto al inventario.
        """
        if producto.get_id() in self.productos:
            raise ValueError("Ya existe un producto con ese ID.")

        self.productos[producto.get_id()] = producto
        self.__actualizar_indice_nombre(producto)
        self.guardar_en_archivo()

    def eliminar_producto(self, producto_id):
        """
        Elimina un producto por su ID.
        """
        producto_id = str(producto_id)
        if producto_id not in self.productos:
            raise KeyError("No se encontró un producto con ese ID.")

        producto = self.productos[producto_id]
        self.__eliminar_del_indice_nombre(producto)
        del self.productos[producto_id]
        self.guardar_en_archivo()

    def actualizar_producto(self, producto_id, nueva_cantidad=None, nuevo_precio=None, nuevo_nombre=None):
        """
        Actualiza cantidad, precio y/o nombre de un producto.
        """
        producto_id = str(producto_id)
        if producto_id not in self.productos:
            raise KeyError("No se encontró un producto con ese ID.")

        producto = self.productos[producto_id]

        # Si cambia el nombre, actualizamos el índice
        if nuevo_nombre is not None and nuevo_nombre.strip() != "":
            self.__eliminar_del_indice_nombre(producto)
            producto.set_nombre(nuevo_nombre)
            self.__actualizar_indice_nombre(producto)

        if nueva_cantidad is not None:
            producto.set_cantidad(nueva_cantidad)

        if nuevo_precio is not None:
            producto.set_precio(nuevo_precio)

        self.guardar_en_archivo()

    def buscar_por_nombre(self, nombre):
        """
        Busca productos por nombre exacto (ignorando mayúsculas/minúsculas).
        Devuelve una lista de productos.
        """
        nombre_clave = nombre.strip().lower()
        resultados = []

        if nombre_clave in self.indice_nombres:
            for producto_id in self.indice_nombres[nombre_clave]:
                resultados.append(self.productos[producto_id])

        return resultados

    def buscar_por_nombre_parcial(self, texto):
        """
        Busca productos que contengan un texto en el nombre.
        Devuelve una lista.
        """
        texto = texto.strip().lower()
        resultados = []

        for producto in self.productos.values():
            if texto in producto.get_nombre().lower():
                resultados.append(producto)

        return resultados

    def mostrar_todos(self):
        """
        Devuelve una lista de todos los productos.
        """
        return list(self.productos.values())

    def guardar_en_archivo(self):
        """
        Guarda el inventario en un archivo JSON.
        """
        try:
            datos = [producto.to_dict() for producto in self.productos.values()]
            with open(self.archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
        except PermissionError:
            print("Error: No tienes permisos para escribir en el archivo.")
        except Exception as e:
            print(f"Error inesperado al guardar: {e}")

    def cargar_desde_archivo(self):
        """
        Carga el inventario desde un archivo JSON.
        """
        if not os.path.exists(self.archivo):
            return

        try:
            with open(self.archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            self.productos.clear()
            self.indice_nombres.clear()

            for item in datos:
                producto = Producto.from_dict(item)
                self.productos[producto.get_id()] = producto
                self.__actualizar_indice_nombre(producto)

        except FileNotFoundError:
            print("El archivo de inventario no existe. Se creará uno nuevo.")
        except json.JSONDecodeError:
            print("Error: El archivo está dañado o no tiene formato JSON válido.")
        except PermissionError:
            print("Error: No tienes permisos para leer el archivo.")
        except Exception as e:
            print(f"Error inesperado al cargar: {e}")


def mostrar_menu():
    print("\n" + "=" * 50)
    print("   SISTEMA AVANZADO DE GESTIÓN DE INVENTARIO")
    print("=" * 50)
    print("1. Añadir producto")
    print("2. Eliminar producto por ID")
    print("3. Actualizar producto")
    print("4. Buscar producto por nombre exacto")
    print("5. Buscar producto por nombre parcial")
    print("6. Mostrar todos los productos")
    print("7. Salir")
    print("=" * 50)


def solicitar_numero_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Entrada inválida. Debes ingresar un número entero.")


def solicitar_numero_decimal(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Entrada inválida. Debes ingresar un número válido.")


def main():
    inventario = Inventario()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                producto_id = input("Ingrese el ID del producto: ").strip()
                nombre = input("Ingrese el nombre del producto: ").strip()
                cantidad = solicitar_numero_entero("Ingrese la cantidad: ")
                precio = solicitar_numero_decimal("Ingrese el precio: ")

                producto = Producto(producto_id, nombre, cantidad, precio)
                inventario.agregar_producto(producto)
                print("Producto añadido correctamente.")

            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")

        elif opcion == "2":
            try:
                producto_id = input("Ingrese el ID del producto a eliminar: ").strip()
                inventario.eliminar_producto(producto_id)
                print("Producto eliminado correctamente.")

            except KeyError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")

        elif opcion == "3":
            try:
                producto_id = input("Ingrese el ID del producto a actualizar: ").strip()

                print("\nDeje en blanco lo que no desea cambiar.")

                nuevo_nombre = input("Nuevo nombre: ").strip()
                cantidad_texto = input("Nueva cantidad: ").strip()
                precio_texto = input("Nuevo precio: ").strip()

                nueva_cantidad = None
                nuevo_precio = None

                if cantidad_texto != "":
                    nueva_cantidad = int(cantidad_texto)

                if precio_texto != "":
                    nuevo_precio = float(precio_texto)

                inventario.actualizar_producto(
                    producto_id,
                    nueva_cantidad=nueva_cantidad,
                    nuevo_precio=nuevo_precio,
                    nuevo_nombre=nuevo_nombre if nuevo_nombre != "" else None
                )

                print("Producto actualizado correctamente.")

            except ValueError as e:
                print(f"Error: {e}")
            except KeyError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")

        elif opcion == "4":
            nombre = input("Ingrese el nombre exacto del producto: ").strip()
            resultados = inventario.buscar_por_nombre(nombre)

            if resultados:
                print("\nProductos encontrados:")
                for producto in resultados:
                    print(producto)
            else:
                print("No se encontraron productos con ese nombre.")

        elif opcion == "5":
            texto = input("Ingrese parte del nombre del producto: ").strip()
            resultados = inventario.buscar_por_nombre_parcial(texto)

            if resultados:
                print("\nProductos encontrados:")
                for producto in resultados:
                    print(producto)
            else:
                print("No se encontraron coincidencias.")

        elif opcion == "6":
            productos = inventario.mostrar_todos()

            if productos:
                print("\nInventario completo:")
                for producto in productos:
                    print(producto)
            else:
                print("El inventario está vacío.")

        elif opcion == "7":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()