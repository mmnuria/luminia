import modules.cuia as cuia
import numpy as np

# --------------------------------------------------------------
# FUNCIÓN BASE
# --------------------------------------------------------------
def crear_modelo(ruta):
    modelo = cuia.modeloGLTF(ruta)
    modelo.rotar((np.pi / 2.0, 0, 0))
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
    "A": "media/letras/A.glb",
    "B": "media/letras/B.glb",
    "C": "media/letras/C.glb",
    "D": "media/letras/D.glb",
    "E": "media/letras/E.glb",
    "F": "media/letras/F.glb",
    "G": "media/letras/G.glb",
    "H": "media/letras/H.glb",
    "I": "media/letras/I.glb",
    "J": "media/letras/J.glb",
    "K": "media/letras/K.glb",
    "L": "media/letras/L.glb",
    "M": "media/letras/M.glb",
    "N": "media/letras/N.glb",
    "O": "media/letras/O.glb",
    "P": "media/letras/P.glb",
    "Q": "media/letras/Q.glb",
    "R": "media/letras/R.glb",
    "S": "media/letras/S.glb",
    "T": "media/letras/T.glb",
    "U": "media/letras/U.glb",
    "V": "media/letras/V.glb",
    "W": "media/letras/W.glb",
    "X": "media/letras/X.glb",
    "Y": "media/letras/Y.glb",
    "Z": "media/letras/Z.glb",
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
    "Fishbowl": "media/animales/Fishbowl.glb",
    "Hamster": "media/animales/Hamster.glb",
    "Harp_Seal": "media/animales/Harp_Seal.glb",
    "Horse": "media/animales/Horse.glb",
    "Penguin": "media/animales/Penguin.glb",
    "Pig": "media/animales/Pig.glb",
    "Rabbit": "media/animales/Rabbit.glb",
    "Reindeer": "media/animales/Reindeer.glb",
    "Sheep": "media/animales/Sheep.glb",
    "Snail": "media/animales/Snail.glb",
    "Snowy_Owls": "media/animales/Snowy_Owls.glb",
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
    "0": "media/numeros/0.glb",
    "1": "media/numeros/1.glb",
    "2": "media/numeros/2.glb",
    "3": "media/numeros/3.glb",
    "4": "media/numeros/4.glb",
    "5": "media/numeros/5.glb",
    "6": "media/numeros/6.glb",
    "7": "media/numeros/7.glb",
    "8": "media/numeros/8.glb",
    "9": "media/numeros/9.glb",
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
}

#REVISARLAS, NO EXISTEN AUN
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
