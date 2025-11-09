import utils.operaciones as operaciones
import numpy as np

# --------------------------------------------------------------
# FUNCIÓN BASE
# --------------------------------------------------------------
def crear_modelo(ruta):
    modelo = operaciones.modeloGLTF(ruta)
    modelo.rotar((np.pi / 2.0, 0, 0))
    
    # Escala según el tipo de modelo en la ruta
    if "mascota" in ruta.lower():
        modelo.escalar(0.05)
    elif "castillos" in ruta.lower():
        modelo.escalar(0.10)
    else:
        modelo.escalar(0.15)
    
    modelo.flotar()
    
    animaciones = modelo.animaciones()
    if animaciones:
        modelo.animar(animaciones[0])
    
    return modelo


# --------------------------------------------------------------
# RUTAS DE LOS MODELOS
# --------------------------------------------------------------
# Letras
rutas_letras = {
    "A": "media/letras/A_nuevo.glb",
    "B": "media/letras/B_nuevo.glb",
    "C": "media/letras/C_nuevo.glb",
    "D": "media/letras/D_nuevo.glb",
    "E": "media/letras/E_nuevo.glb",
    "F": "media/letras/F_nuevo.glb",
    "G": "media/letras/G_nuevo.glb",
    "H": "media/letras/H_nuevo.glb",
    "I": "media/letras/I_nuevo.glb",
    "J": "media/letras/J_nuevo.glb",
    "K": "media/letras/K_nuevo.glb",
    "L": "media/letras/L_nuevo.glb",
    "M": "media/letras/M_nuevo.glb",
    "N": "media/letras/N_nuevo.glb",
    "O": "media/letras/O_nuevo.glb",
    "P": "media/letras/P_nuevo.glb",
    "Q": "media/letras/Q_nuevo.glb",
    "R": "media/letras/R_nuevo.glb",
    "S": "media/letras/S_nuevo.glb",
    "T": "media/letras/T_nuevo.glb",
    "U": "media/letras/U_nuevo.glb",
    "V": "media/letras/V_nuevo.glb",
    "W": "media/letras/W_nuevo.glb",
    "X": "media/letras/X_nuevo.glb",
    "Y": "media/letras/Y_nuevo.glb",
    "Z": "media/letras/Z_nuevo.glb",
}

# Animales
rutas_animales = {
    "Bee": "media/animales/Bee.glb",
    "Bird": "media/animales/Bird.glb",
    "BowheadWhale": "media/animales/BowheadWhale.glb",
    "Butterfly": "media/animales/Butterfly.glb",
    "Cat": "media/animales/Cat.glb",
    "Chicken": "media/animales/Chicken.glb",
    "Cool_Pose": "media/animales/Cool_Pose.glb",
    "Cow": "media/animales/Cow.glb",
    "Dog": "media/animales/Dog.glb",
    "Hamster": "media/animales/Hamster.glb",
    "Harp_Seal": "media/animales/Harp_Seal.glb",
    "Horse": "media/animales/Horse.glb",
    "Penguin": "media/animales/Penguin.glb",
    "Pig": "media/animales/Pig.glb",
    "Reindeer": "media/animales/Reindeer.glb",
    "Sheep": "media/animales/Sheep.glb",
    "Snail": "media/animales/Snail.glb",
    "Snowy_Owls": "media/animales/Snowy_Owls.glb",
    "Beluga_Whale": "media/animales/Beluga_Whale.glb",
    "Crab": "media/animales/Crab.glb",
    "Fish": "media/animales/Fish.glb",
    "Jellyfish": "media/animales/Jellyfish.glb",
    "Seashell": "media/animales/Seashell.glb",
    "Starfish": "media/animales/Starfish.glb",
}

# Frutas
rutas_frutas = {
    "Apple": "media/frutas/Apple.glb",
    "Avocado": "media/frutas/Avocado.glb",
    "Banana": "media/frutas/Banana.glb",
    "Blueberry": "media/frutas/Blueberry.glb",
    "Cherry": "media/frutas/Cherry.glb",
    "Dragon_Fruit": "media/frutas/Dragon_Fruit.glb",
    "Grape": "media/frutas/Grape.glb",
    "Kiwi": "media/frutas/Kiwi.glb",
    "Lemon": "media/frutas/Lemon.glb",
    "Mango": "media/frutas/Mango.glb",
    "Melon": "media/frutas/Melon.glb",
    "Orange": "media/frutas/Orange.glb",
    "Papaya": "media/frutas/Papaya.glb",
    "Pear": "media/frutas/Pear.glb",
    "Pineapple": "media/frutas/Pineapple.glb",
    "Strawberry": "media/frutas/Strawberry.glb",
    "Watermelon": "media/frutas/Watermelon.glb",
}

# Verduras
rutas_verduras = {
    "Broccoli": "media/verduras/Broccoli.glb",
    "Carrot": "media/verduras/Carrot.glb",
    "Corn": "media/verduras/Corn.glb",
    "Cucumber": "media/verduras/Cucumber.glb",
    "cauliflower": "media/verduras/cauliflower.glb",
    "green_leek": "media/verduras/green_leek.glb",
    "Green_Peas": "media/verduras/Green_Peas.glb",
    "mushroom": "media/verduras/mushroom.glb",
    "Onion": "media/verduras/Onion.glb",
    "Pumpkin": "media/verduras/Pumpkin.glb",
    "Spinach": "media/verduras/Spinach.glb",
    "Vegetable": "media/verduras/Vegetable.glb",
}

# Números
rutas_numeros = {
    "0": "media/numeros/0_nuevo.glb",
    "1": "media/numeros/1_nuevo.glb",
    "2": "media/numeros/2_nuevo.glb",
    "3": "media/numeros/3_nuevo.glb",
    "4": "media/numeros/4_nuevo.glb",
    "5": "media/numeros/5_nuevo.glb",
    "6": "media/numeros/6_nuevo.glb",
    "7": "media/numeros/7_nuevo.glb",
    "8": "media/numeros/8_nuevo.glb",
    "9": "media/numeros/9_nuevo.glb",
}

# Mascotas
rutas_mascota = {
    "Bear": "media/mascota/Bear.glb",
    "Cat": "media/mascota/Cat.glb",
    "Chicken": "media/mascota/Chicken.glb",
    "Crocodile": "media/mascota/Crocodile.glb",
    "Deer": "media/mascota/Deer.glb",
    "Dragon": "media/mascota/Dragon.glb",
    "Duck": "media/mascota/Duck.glb",
    "Eagle": "media/mascota/Eagle.glb",
    "Fish": "media/mascota/Fish.glb",
    "Flamingo": "media/mascota/Flamingo.glb",  
    "Fox": "media/mascota/Fox.glb",
    "Giraffe": "media/mascota/Giraffe.glb",        
    "Gorilla": "media/mascota/Gorilla.glb",        
    "Hippo": "media/mascota/Hippo.glb",
    "Koala": "media/mascota/Koala.glb",
    "Lion": "media/mascota/Lion.glb",
    "Monkey": "media/mascota/Monkey.glb",
    "Octopus": "media/mascota/Octopus.glb",
    "Owl": "media/mascota/Owl.glb",
    "Panda": "media/mascota/Panda.glb",
    "Penguin": "media/mascota/Penguin.glb",     
    "Raccoon": "media/mascota/Raccoon.glb",        
    "Rabbit": "media/mascota/Rabbit.glb",
    "Rat": "media/mascota/Rat.glb",
    "Seel": "media/mascota/Seel.glb",
    "Shark": "media/mascota/Shark.glb",
    "Tiger": "media/mascota/Tiger.glb",
    "Zebra": "media/mascota/Zebra.glb",
    "sami": "media/mascota/sami.glb",
    "tina_unicornio": "media/mascota/tina_unicornio.glb",
    "Bee": "media/mascota/Bee.glb",
    "Butterfly": "media/mascota/Butterfly.glb",
    "Horn_beetle": "media/mascota/Horn_beetle.glb",
}

#Castillos
rutas_castillos = {
    "letras_color": "media/castillos/castillo_letras.glb",
    "letras_bn": "media/castillos/castillo_letras.glb",
    "animales_color": "media/castillos/castillo_animales.glb",
    "animales_bn": "media/castillos/castillo_animales.glb",
    "fruta_y_verdura_color": "media/castillos/castillo_frutas_verduras.glb",
    "fruta_y_verdura_bn": "media/castillos/castillo_frutas_verduras.glb",
    "numeros_color": "media/castillos/castillo_numeros.glb",
    "numeros_bn": "media/castillos/castillo_numeros.glb",
    "final_color": "media/castillos/castillo_final.glb",
    "final_bn": "media/castillos/castillo_final.glb",
}

def obtener_ruta_por_categoria(categoria, nombre, desbloqueado=True):
    rutas = {
        "letras": rutas_letras,
        "animales": rutas_animales,
        "frutas": rutas_frutas,
        "verduras": rutas_verduras,
        "numeros": rutas_numeros,
        "mascota": rutas_mascota,
        "castillo": rutas_castillos,
    }
    dic = rutas.get(categoria, {})
    if categoria == "castillo":
        suffix = "_color" if desbloqueado else "_bn"
        return dic.get(nombre + suffix, "")
    return dic.get(nombre if categoria != "numeros" else str(nombre), "")

# --------------------------------------------------------------
# CREAR FUNCIONES DINÁMICAMENTE
# --------------------------------------------------------------

globals().update({
    f"crear_modelo_{nombre}": (lambda ruta=ruta: crear_modelo(ruta))
    for nombre, ruta in {**rutas_letras, **rutas_animales, **rutas_frutas, **rutas_verduras, **rutas_numeros, **rutas_mascota, **rutas_castillos}.items()
})
