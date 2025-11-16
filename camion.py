class Caja:
    def __init__(self, codigo, peso_kg, descripcion_carga, largo, ancho, altura):
        self.codigo = codigo
        self.peso_kg = peso_kg
        self.descripcion_carga = descripcion_carga
        self.largo = largo
        self.ancho = ancho
        self.altura = altura

    def __str__(self):
        return (f"--- Caja {self.codigo} ---\n"
                f"Peso: {self.peso_kg} kg\n"
                f"Descripción: {self.descripcion_carga}\n"
                f"Dimensiones: {self.largo} x {self.ancho} x {self.altura}\n")


class Camion:
    def __init__(self, matricula, conductor, capacidad_kg, descripcion_carga, rumbo, velocidad):
        self.matricula = matricula
        self.conductor = conductor
        self.capacidad_kg = capacidad_kg
        self.descripcion_carga = descripcion_carga
        self.rumbo = rumbo
        self.velocidad = velocidad
        self.cajas = []

    def peso_total(self):
        total = 0
        for caja in self.cajas:
            total += caja.peso_kg
        return total

    def add_caja(self, caja):
        if self.peso_total() + caja.peso_kg <= self.capacidad_kg:
            self.cajas.append(caja)
        else:
            print("AVISO: No se puede añadir la caja. Capacidad excedida.")

    def __str__(self):
        texto = (f"Camión {self.matricula}\n"
                 f"Conductor: {self.conductor}\n"
                 f"Descripción carga: {self.descripcion_carga}\n"
                 f"Velocidad: {self.velocidad} km/h\n"
                 f"Rumbo: {self.rumbo} grados\n"
                 f"Capacidad máxima: {self.capacidad_kg} kg\n"
                 f"Peso total cargado: {self.peso_total()} kg\n"
                 f"Número de cajas: {len(self.cajas)}\n")

        texto += "=== Cajas cargadas ===\n"
        for c in self.cajas:
            texto += str(c)
        return texto

    def setVelocidad(self):
        self.velocidad = int(input("Introduce la velocidad a la que quieres ir: "))
        while self.velocidad < 0 or self.velocidad > 180:
            print("La velocidad no está entre 0 y 180 km/h.")
            self.velocidad = int(input("Introduce una velocidad válida: "))

    def setRumbo(self):
        self.rumbo = int(input("Introduce el nuevo rumbo (1-359): "))
        while self.rumbo < 1 or self.rumbo > 359:
            print("El rumbo no está entre 1 y 359 grados.")
            self.rumbo = int(input("Introduce un rumbo válido: "))

    def claxon(self):
        print("piiiiiii")


#main
if __name__ == "__main__":

    caja1 = Caja("A1", 100, "Herramientas", 1.0, 0.5, 0.5)
    caja2 = Caja("A2", 200, "Tornillos", 1.2, 0.6, 0.5)
    caja3 = Caja("A3", 150, "Electrónica", 1.1, 0.6, 0.4)

    caja4 = Caja("B1", 90, "Ropa", 1.0, 0.5, 0.4)
    caja5 = Caja("B2", 160, "Alimentos", 1.2, 0.8, 0.6)
    caja6 = Caja("B3", 180, "Material de oficina", 1.3, 0.7, 0.5)

    camion1 = Camion("1234ABC", "Juan", 1000, "Carga variada", 90, 80)
    camion2 = Camion("5678DEF", "Pedro", 1200, "Mercancías generales", 140, 70)

    camion1.add_caja(caja1)
    camion1.add_caja(caja2)
    camion1.add_caja(caja3)

    camion2.add_caja(caja4)
    camion2.add_caja(caja5)
    camion2.add_caja(caja6)

    print("ESTADO INICIAL DE LOS CAMIONES")
    print(camion1)
    print(camion2)


    caja_extra1 = Caja("X1", 120, "Libros", 1.0, 0.5, 0.4)
    caja_extra2 = Caja("X2", 130, "Pintura", 1.1, 0.6, 0.5)

    caja_extra3 = Caja("X3", 140, "Juguetes", 1.0, 0.5, 0.5)
    caja_extra4 = Caja("X4", 170, "Electrodomésticos", 1.3, 0.7, 0.6)
    caja_extra5 = Caja("X5", 150, "Herramientas pesadas", 1.2, 0.8, 0.7)

    camion1.add_caja(caja_extra1)
    camion1.add_caja(caja_extra2)

    camion2.add_caja(caja_extra3)
    camion2.add_caja(caja_extra4)
    camion2.add_caja(caja_extra5)

    camion1.setVelocidad()
    camion1.setRumbo()

    camion2.setVelocidad()
    camion2.setRumbo()

    camion2.claxon()

    print("\n===== ESTADO FINAL DE LOS CAMIONES =====")
    print(camion1)
    print(camion2)