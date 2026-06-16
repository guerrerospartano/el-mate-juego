import sys
import os
import random

# --- IMPORTACIÓN ---
try:
    import pygame
    from fractions import Fraction
except ModuleNotFoundError:
    rutas_usuario = [
        os.path.expanduser(r"~\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages"),
        os.path.expanduser(r"~\.local\lib\python3.14\site-packages"),
        os.path.abspath(".venv/lib/site-packages"),
        os.path.abspath("venv/lib/site-packages")
    ]
    for ruta in rutas_usuario:
        if ruta not in sys.path and os.path.exists(ruta):
            sys.path.append(ruta)
    import pygame
    from fractions import Fraction

# 1. Inicialización de Pygame
pygame.init()

ANCHO = 450
ALTO = 750
ALTO_LISTA_LOGROS = 440  

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("EL MATE JUEGO")

reloj = pygame.time.Clock()

# ==========================================
# 2. PALETA DE COLORES PASTEL, OSCUROS Y CAOS
# ==========================================
PALETA_FONDO_RECORTE = (30, 30, 30)
PALETA_FONDO_MENU    = (40, 43, 48)

PASTEL_AMARILLO      = (255, 253, 162)
PASTEL_ROSA_VIEJO    = (255, 201, 192)
PASTEL_CELESTE_MAR   = (137, 212, 214)
PASTEL_TURQUESA      = (56, 204, 214)
PASTEL_DURAZNO       = (255, 216, 177)
PASTEL_LAVANDA       = (214, 178, 222)
PASTEL_CREMA         = (255, 241, 198)
PASTEL_VERDE_MENTA   = (164, 233, 202)
PASTEL_ROSA_CHICLE   = (251, 169, 193)
PASTEL_GRIS_CLARO    = (238, 236, 233)
PASTEL_CORAL         = (255, 137, 126)

BLANCO = (255, 255, 255)
TEXTO_OSCURO = (50, 50, 50)
TEXTO_DESACTIVADO = (140, 140, 140)

# --- COLORES MODO CAOS ---
CAOS_FONDO       = (43, 43, 43)       
CAOS_PANEL       = (64, 33, 33)       
CAOS_TEXTO_DESAC = (143, 114, 114)    
CAOS_TITULO      = (227, 142, 123)    
CAOS_VIVO        = (222, 49, 72)      
CAOS_ALERTA      = (166, 25, 46)      
CAOS_NARANJA     = (214, 73, 41)      

# ==========================================
# 3. FUENTES Y SISTEMA DE AJUSTE DINÁMICO
# ==========================================
NOMBRES_FUENTES = ['segoeprint', 'comicmath', 'comicsans', 'cursive', 'arial']

def cargar_fuente_cursiva(tamano):
    return pygame.font.SysFont(NOMBRES_FUENTES, tamano, bold=True)

fuente_titulo = cargar_fuente_cursiva(42)
fuente_botones = cargar_fuente_cursiva(26)
fuente_juego = cargar_fuente_cursiva(50) 
fuente_interfaz = cargar_fuente_cursiva(20)
fuente_logros_tit = cargar_fuente_cursiva(24)

def renderizar_con_ajuste(texto, tamano_base, ancho_maximo, color):
    texto_caps = str(texto).upper()
    tamano_actual = tamano_base
    fuente = pygame.font.SysFont(NOMBRES_FUENTES, tamano_actual, bold=True)
    superficie = fuente.render(texto_caps, True, color)
    
    while superficie.get_width() > ancho_maximo and tamano_actual > 12:
        tamano_actual -= 2
        fuente = pygame.font.SysFont(NOMBRES_FUENTES, tamano_actual, bold=True)
        superficie = fuente.render(texto_caps, True, color)
        
    return superficie

# 4. Control de Estados
estado_actual = 'MENU'
operacion_seleccionada = None   
dificultad_seleccionada = None  
es_modo_caos_activo = False 

# 5. Variables del Estado del Juego
num1, num2 = 0, 0
operador_simbolo = "+"
respuesta_correcta = 0
respuesta_usuario = "" 

es_modo_fraccion = False
frac_resp_num_correcta = 0
frac_resp_den_correcta = 0

dif_n1, dif_d1 = 0, 0
dif_n2, dif_d2 = 0, 0
dif_n3, dif_d3 = 0, 0
dif_op1, dif_op2 = "+", "+"

respuesta_usuario_num = ""
respuesta_usuario_den = ""
foco_respuesta = "NUMERADOR" 

score = 0
resueltos = 0
vidas = 3
combo = 1
max_combo_partida = 1  
mensaje_feedback = "" 
feedback_timer = 0
esperando_siguiente = False  
resueltos_esta_partida = 0

# --- CONTROL DE TIEMPO ---
tiempo_inicial_ejercicio = 0
segundos_restantes = 0
tiempo_limite_actual = 15
primer_tiempo_agotado = False  
combo_congelado = False        
tiempo_acumulado_antes_pausa = 0

# --- VARIABLES INTERNAS ESPECÍFICAS MODO CAOS ---
caos_lista_ejercicios = []  
caos_tiempo_castigo_activo = False  
caos_contador_global = 0         # Cuenta total de ejercicios resueltos en la tanda de caos actual
caos_contador_dificil = 0        # Cuenta de ejercicios resueltos en dificultad difícil caos
caos_contador_6s = 0             # Cuenta de ejercicios resueltos bajo el castigo de 6s

# --- Sistema de Récords y Logros ---
ARCHIVO_RECORD = "puntuaciones.txt"
high_score = 0
nombre_record = "NADIE"
resueltos_record = 0
combo_record = 1
caos_high_score = 0              # Récord histórico exclusivo del Modo Caos
nombre_actual_usuario = "" 

logros = {
    "pts_1000": 0, "combo_100": 0,
    "suma_facil": 0, "suma_medio": 0, "suma_dificil": 0,
    "resta_facil": 0, "resta_medio": 0, "resta_dificil": 0,
    "mult_facil": 0, "mult_medio": 0, "mult_dificil": 0,
    "div_facil": 0, "div_medio": 0, "div_dificil": 0,
    "mixto_facil": 0, "mixto_medio": 0, "mixto_dificil": 0,
    "frac_facil": 0, "frac_medio": 0, "frac_dificil": 0,
    # --- NUEVOS LOGROS MODO CAOS ---
    "caos_50_ejercicios": 0,
    "caos_acabar_facil": 0,
    "caos_acabar_medio": 0,
    "caos_10_dificil": 0,
    "caos_6_en_6s": 0,
    "caos_superar_record": 0
}

# La tupla ahora incluye un cuarto parámetro: True si es un logro caótico (para pintarlo diferente)
INFO_LOGROS = [
    ("MENTE BRILLANTE", "ALCANZAR 1000 PUNTOS EN UNA PARTIDA", "pts_1000", False),
    ("IMPARABLE", "LOGRAR UN COMBO DE X100", "combo_100", False),
    
    # LOGROS DE CAOS NUEVOS (Se marcan con True al final)
    ("SOBREVIVIENTE DEL CAOS", "RESOLVER 50 EJERCICIOS EN MODO CAOS", "caos_50_ejercicios", True),
    ("DOMADOR FACIL", "COMPLETAR LA FASE FACIL DEL MODO CAOS", "caos_acabar_facil", True),
    ("DOMADOR MEDIO", "COMPLETAR LA FASE MEDIA DEL MODO CAOS", "caos_acabar_medio", True),
    ("MENTE EXTRAORDINARIA", "RESOLVER 10 EJERCICIOS EN DIFICIL CAOS", "caos_10_dificil", True),
    ("VELOCIDAD ABSOLUTA", "RESOLVER 6 EJERCICIOS EN EL MÓDULO DE 6S", "caos_6_en_6s", True),
    ("NUEVA LEYENDA CAOTICA", "SUPERAR TU RECORD ACTUAL EN MODO CAOS", "caos_superar_record", True),

    ("AS DE LA SUMA: NOVATO", "RESOLVER 35 SUMAS EN FACIL", "suma_facil", False),
    ("AS DE LA SUMA: EXPERTO", "RESOLVER 30 SUMAS EN MEDIO", "suma_medio", False),
    ("AS DE LA SUMA: MAESTRO", "RESOLVER 25 SUMAS EN DIFICIL", "suma_dificil", False),
    ("CAZADOR DE RESTAS: NOVATO", "RESOLVER 35 RESTAS EN FACIL", "resta_facil", False),
    ("CAZADOR DE RESTAS: EXPERTO", "RESOLVER 30 RESTAS EN MEDIO", "resta_medio", False),
    ("CAZADOR DE RESTAS: MAESTRO", "RESOLVER 25 RESTAS EN DIFICIL", "resta_dificil", False),
    ("MULTIPLICADOR: NOVATO", "RESOLVER 35 MULTIPLICACIONES EN FACIL", "mult_facil", False),
    ("MULTIPLICADOR: EXPERTO", "RESOLVER 30 MULTIPLICACIONES EN MEDIO", "mult_medio", False),
    ("MULTIPLICADOR: MAESTRO", "RESOLVER 25 MULTIPLICACIONES EN DIFICIL", "mult_dificil", False),
    ("DIVISOR DEL REY: NOVATO", "RESOLVER 35 DIVISIONES EN FACIL", "div_facil", False),
    ("DIVISOR DEL REY: EXPERTO", "RESOLVER 30 DIVISIONES EN MEDIO", "div_medio", False),
    ("DIVISOR DEL REY: MAESTRO", "RESOLVER 25 DIVISIONES EN DIFICIL", "div_dificil", False),
    ("CAOS MIXTO: NOVATO", "RESOLVER 35 MIXTOS EN FACIL", "mixto_facil", False),
    ("CAOS MIXTO: EXPERTO", "RESOLVER 30 MIXTOS EN MEDIO", "mixto_medio", False),
    ("CAOS MIXTO: MAESTRO", "RESOLVER 25 MIXTOS EN DIFICIL", "mixto_dificil", False),
    ("FRACCIONARIO: NOVATO", "RESOLVER 35 FRACCIONES EN FACIL", "frac_facil", False),
    ("FRACCIONARIO: EXPERTO", "RESOLVER 30 FRACCIONES EN MEDIO", "frac_medio", False),
    ("FRACCIONARIO: MAESTRO", "RESOLVER 25 FRACCIONES EN DIFICIL", "frac_dificil", False),
]

def cargar_record():
    global high_score, nombre_record, resueltos_record, combo_record, logros, caos_high_score
    if os.path.exists(ARCHIVO_RECORD):
        try:
            with open(ARCHIVO_RECORD, "r", encoding="utf-8") as f:
                lineas = f.readlines()
                if len(lineas) >= 5:
                    nombre_record = lineas[0].strip().upper()
                    high_score = int(lineas[1].strip())
                    resueltos_record = int(lineas[2].strip())
                    combo_record = int(lineas[3].strip())
                    caos_high_score = int(lineas[4].strip())
                for i, linea in enumerate(lineas[5:]):
                    if i < len(INFO_LOGROS):
                        logros[INFO_LOGROS[i][2]] = int(linea.strip())
        except Exception:
            pass

def guardar_record():
    try:
        with open(ARCHIVO_RECORD, "w", encoding="utf-8") as f:
            f.write(f"{nombre_record.upper()}\n{high_score}\n{resueltos_record}\n{combo_record}\n{caos_high_score}\n")
            for item in INFO_LOGROS:
                f.write(f"{logros[item[2]]}\n")
    except Exception as e:
        print("Error al guardar:", e)

cargar_record()

# ==========================================
# FUNCIONES AUXILIARES DE RENDERIZADO
# ==========================================
def dibujar_texto(texto, fuente, color, x, y, centro=False, ancho_max=ANCHO-40, tam_base=24):
    superficie = renderizar_con_ajuste(texto, tam_base, ancho_max, color)
    rectangulo = superficie.get_rect()
    if centro: rectangulo.center = (x, y)
    else: rectangulo.topleft = (x, y)
    pantalla.blit(superficie, rectangulo)

def dibujar_fraccion(num_str, den_str, x, y, color_num=BLANCO, color_den=BLANCO, ancho_linea=40):
    t_num = renderizar_con_ajuste(num_str, 46, ancho_linea + 15, color_num)
    t_den = renderizar_con_ajuste(den_str, 46, ancho_linea + 15, color_den)
    ancho_bloque = max(ancho_linea, t_num.get_width(), t_den.get_width())
    
    x_num = x + (ancho_bloque // 2) - (t_num.get_width() // 2)
    pantalla.blit(t_num, (x_num, y))
    
    y_linea = y + t_num.get_height() + 4
    color_linea = CAOS_NARANJA if es_modo_caos_activo else BLANCO
    pygame.draw.line(pantalla, color_linea, (x - 5, y_linea), (x + ancho_bloque + 5, y_linea), width=3)
    
    x_den = x + (ancho_bloque // 2) - (t_den.get_width() // 2)
    y_den = y_linea + 8
    pantalla.blit(t_den, (x_den, y_den))

def crear_boton(texto, x, y, ancho, alto, color_base, color_texto, radio=14, tam_letra=26):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, ancho, alto)
    pygame.draw.rect(pantalla, color_base, rect, border_radius=radio)
    pygame.draw.rect(pantalla, PASTEL_GRIS_CLARO, rect, width=2, border_radius=radio)
    
    superficie_texto = renderizar_con_ajuste(texto, tam_letra, ancho - 16, color_texto)
    rect_txt = superficie_texto.get_rect(center=rect.center)
    pantalla.blit(superficie_texto, rect_txt)
    
    return rect.collidepoint(mouse_pos)

# ==========================================
# GESTIÓN Y LÓGICA DEL MODO CAOS
# ==========================================
def preparar_cola_modo_caos():
    """Genera la lista estructurada de ejercicios en orden estricto para el Modo Caos."""
    global caos_lista_ejercicios, caos_tiempo_castigo_activo, caos_contador_global, caos_contador_dificil, caos_contador_6s
    caos_tiempo_castigo_activo = False
    caos_contador_global = 0
    caos_contador_dificil = 0
    caos_contador_6s = 0
    caos_lista_ejercicios = []
    
    # 1. Bloque Fácil (10 ejercicios, de 2 en 2, 15 segundos base)
    for op in ['SUMA', 'RESTA', 'MULTIPLICAR', 'DIVISION', 'FRACCION']:
        caos_lista_ejercicios.append(('FACIL', op, 15))
        caos_lista_ejercicios.append(('FACIL', op, 15))
        
    # 2. Bloque Medio (10 ejercicios, de 2 en 2, 12 segundos base)
    for op in ['SUMA', 'RESTA', 'MULTIPLICAR', 'DIVISION', 'FRACCION']:
        caos_lista_ejercicios.append(('MEDIO', op, 12))
        caos_lista_ejercicios.append(('MEDIO', op, 12))
        
    # 3. Bloque Difícil Infinito (De 1 en 1, 10 segundos base)
    operaciones_posibles = ['SUMA', 'RESTA', 'MULTIPLICAR', 'DIVISION', 'FRACCION']
    for _ in range(100):
        op_aleatoria = random.choice(operaciones_posibles)
        caos_lista_ejercicios.append(('DIFICIL', op_aleatoria, 10))

# ==========================================
# GENERACIÓN DE EJERCICIOS
# ==========================================
def generar_ejercicio():
    global num1, num2, operador_simbolo, respuesta_correcta, respuesta_usuario
    global es_modo_fraccion, esperando_siguiente, tiempo_inicial_ejercicio, segundos_restantes, tiempo_limite_actual
    global frac_resp_num_correcta, frac_resp_den_correcta
    global respuesta_usuario_num, respuesta_usuario_den, foco_respuesta
    global dif_n1, dif_d1, dif_n2, dif_d2, dif_n3, dif_d3, dif_op1, dif_op2
    global combo_congelado, tiempo_acumulado_antes_pausa, primer_tiempo_agotado
    global dificultad_seleccionada, operacion_seleccionada, caos_lista_ejercicios
    
    respuesta_usuario = "" 
    respuesta_usuario_num, respuesta_usuario_den = "", ""
    foco_respuesta = "NUMERADOR"
    es_modo_fraccion = False
    esperando_siguiente = False 
    tiempo_acumulado_antes_pausa = 0
    primer_tiempo_agotado = False
    
    if es_modo_caos_activo:
        if len(caos_lista_ejercicios) == 0:
            for _ in range(10): caos_lista_ejercicios.append(('DIFICIL', random.choice(['SUMA', 'RESTA', 'MULTIPLICAR', 'DIVISION', 'FRACCION']), 10))
            
        dif_actual, op_actual, t_base = caos_lista_ejercicios.pop(0)
        dificultad_seleccionada = dif_actual
        operacion_seleccionada = op_actual
        
        if caos_tiempo_castigo_activo:
            tiempo_limite_actual = 6
        else:
            tiempo_limite_actual = t_base
    else:
        if combo_congelado:
            tiempo_limite_actual = 10
        else:
            tiempos = {'FACIL': 15, 'MEDIO': 20, 'DIFICIL': 25}
            tiempo_limite_actual = tiempos.get(dificultad_seleccionada, 30)
            
        op_actual = operacion_seleccionada
    
    tiempo_inicial_ejercicio = pygame.time.get_ticks()
    segundos_restantes = tiempo_limite_actual
    
    rangos = {'FACIL': (1, 99), 'MEDIO': (1, 9999), 'DIFICIL': (1, 999999)}
    min_n, max_n = rangos.get(dificultad_seleccionada, (1, 99))

    if op_actual == 'MIXTO':
        op_actual = random.choice(['SUMA', 'RESTA', 'MULTIPLICAR', 'DIVISION'])

    if op_actual == 'FRACCION':
        es_modo_fraccion = True
        if dificultad_seleccionada == 'FACIL':
            den = random.randint(2, 99)
            n1, n2 = random.randint(1, 99), random.randint(1, 99)
            operador_simbolo = random.choice(["+", "-"])
            if operador_simbolo == "-" and n1 < n2: n1, n2 = n2, n1  
            num1, num2 = n1, n2  
            frac_resp_den_correcta = den
            frac_resp_num_correcta = (n1 + n2) if operador_simbolo == "+" else (n1 - n2)
        elif dificultad_seleccionada == 'MEDIO':
            operador_simbolo = random.choice(["+", "-", "x"])
            if operador_simbolo == "x":
                den = random.randint(2, 12)
                num1, num2 = random.randint(1, 12), random.randint(1, 12)
                frac_resp_den_correcta = den * den
                frac_resp_num_correcta = num1 * num2
            else:
                den = random.randint(2, 99)
                num1, num2 = random.randint(1, 99), random.randint(1, 99)
                if operador_simbolo == "-" and num1 < num2: num1, num2 = num2, num1
                frac_resp_den_correcta = den
                frac_resp_num_correcta = (num1 + num2) if operador_simbolo == "+" else (num1 - num2)
        else: 
            dif_n1, dif_c, dif_n3 = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
            dif_d1, dif_d, dif_d3 = random.randint(2, 5), random.randint(2, 5), random.randint(2, 5)
            dif_n2, dif_d2 = dif_c, dif_d
            dif_op1 = random.choice(["+", "-", "x", "/"])
            dif_op2 = random.choice(["x", "/"]) if dif_op1 in ["+", "-"] else random.choice(["+", "-"])
            
            f1, f2, f3 = Fraction(dif_n1, dif_d1), Fraction(dif_n2, dif_d2), Fraction(dif_n3, dif_d3)
            if dif_op1 in ["x", "/"] and dif_op2 in ["+", "-"]:
                res_izq = f1 * f2 if dif_op1 == "x" else f1 / f2
                final = res_izq + f3 if dif_op2 == "+" else res_izq - f3
            elif dif_op2 in ["x", "/"] and dif_op1 in ["+", "-"]:
                res_der = f2 * f3 if dif_op2 == "x" else f2 / f3
                final = f1 + res_der if dif_op1 == "+" else f1 - res_der
            else:
                res_izq = f1 + f2 if dif_op1 == "+" else f1 - f2 if dif_op1 == "-" else f1 * f2 if dif_op1 == "x" else f1 / f2
                final = res_izq + f3 if dif_op2 == "+" else res_izq - f3 if dif_op2 == "-" else res_izq * f3 if dif_op2 == "x" else res_izq / f3
            frac_resp_num_correcta = final.numerator
            frac_resp_den_correcta = final.denominator
    else:
        if op_actual == 'SUMA':
            num1, num2 = random.randint(min_n, max_n), random.randint(min_n, max_n)
            operador_simbolo, respuesta_correcta = "+", num1 + num2
        elif op_actual == 'RESTA':
            num1, num2 = random.randint(min_n, max_n), random.randint(min_n, max_n)
            if num1 < num2: num1, num2 = num2, num1
            operador_simbolo, respuesta_correcta = "-", num1 - num2
        elif op_actual == 'MULTIPLICAR':
            operador_simbolo = "x"
            if dificultad_seleccionada == 'FACIL': num1, num2 = random.randint(1, 99), random.randint(1, 9)
            elif dificultad_seleccionada == 'MEDIO': num1, num2 = random.randint(1, 999), random.randint(1, 999)
            else: num1, num2 = random.randint(1, 9999), random.randint(1, 9999)
            respuesta_correcta = num1 * num2
        elif op_actual == 'DIVISION':
            operador_simbolo = "/"
            limites_div = {'FACIL': (9, 99, 99), 'MEDIO': (99, 999, 9999), 'DIFICIL': (999, 9999, 99999)}
            max_num2, max_resp, max_num1 = limites_div[dificultad_seleccionada]
            num2 = random.randint(2, max_num2)
            respuesta_correcta = random.randint(1, max_resp)
            while (respuesta_correcta * num2) > max_num1: respuesta_correcta = random.randint(1, max_resp)
            num1 = respuesta_correcta * num2

def aplicar_penalizacion_puntos():
    global score
    if es_modo_caos_activo: return  
    penalizaciones = {'FACIL': 10, 'MEDIO': 20, 'DIFICIL': 30}
    score = max(0, score - penalizaciones.get(dificultad_seleccionada, 10))

def aplicar_penalizacion_saltar():
    global score
    if es_modo_caos_activo: return  
    penalizaciones = {'FACIL': 1, 'MEDIO': 3, 'DIFICIL': 5}
    score = max(0, score - penalizaciones.get(dificultad_seleccionada, 1))

def verificar_respuesta():
    global score, resueltos, vidas, combo, max_combo_partida, mensaje_feedback, feedback_timer, esperando_siguiente, resueltos_esta_partida
    global caos_contador_global, caos_contador_dificil, caos_contador_6s, logros
    if esperando_siguiente: return

    try:
        if es_modo_fraccion:
            if dificultad_seleccionada in ['FACIL', 'MEDIO']:
                if respuesta_usuario == "": return
                num_user, den_user = int(respuesta_usuario), frac_resp_den_correcta
            else:
                if respuesta_usuario_num == "" or respuesta_usuario_den == "": return
                num_user, den_user = int(respuesta_usuario_num), int(respuesta_usuario_den)
            es_valido = (num_user * frac_resp_den_correcta == frac_resp_num_correcta * den_user)
        else:
            if respuesta_usuario == "": return
            es_valido = (int(respuesta_usuario) == respuesta_correcta)

        if es_valido:
            if es_modo_caos_activo:
                caos_contador_global += 1
                
                # Control de logros por fases superadas
                if caos_contador_global == 10: logros["caos_acabar_facil"] = 1
                if caos_contador_global == 20: logros["caos_acabar_medio"] = 1
                if caos_contador_global >= 50: logros["caos_50_ejercicios"] = 1
                
                if dificultad_seleccionada == 'DIFICIL':
                    caos_contador_dificil += 1
                    if caos_contador_dificil >= 10: logros["caos_10_dificil"] = 1
                    
                if caos_tiempo_castigo_activo:
                    caos_contador_6s += 1
                    if caos_contador_6s >= 6: logros["caos_6_en_6s"] = 1
                    
                    if combo >= 10: score += 50
                    else: score += 25
                    combo += 1
                else:
                    if combo >= 4: score += 10
                    else: score += 3
                    combo += 1
                    
                if score > caos_high_score and caos_high_score > 0:
                    logros["caos_superar_record"] = 1
            else:
                if combo_congelado:
                    valores_castigo = {'FACIL': 2, 'MEDIO': 4, 'DIFICIL': 6}
                    score += valores_castigo.get(dificultad_seleccionada, 2)
                else:
                    puntos_base = {'FACIL': (3, 9), 'MEDIO': (5, 15), 'DIFICIL': (7, 21)}
                    base, con_combo = puntos_base.get(dificultad_seleccionada, (3, 9))
                    score += con_combo if combo > 1 else base
                    combo += 3  

            if combo > max_combo_partida: max_combo_partida = combo
            resueltos += 1
            resueltos_esta_partida += 1
            mensaje_feedback = "CORRECTO"
        else:
            vidas -= 1
            aplicar_penalizacion_puntos()
            combo = 1 
            mensaje_feedback = f"ERROR ({frac_resp_num_correcta}/{frac_resp_den_correcta})" if es_modo_fraccion else f"ERROR (ERA {respuesta_correcta})"
            
        feedback_timer = pygame.time.get_ticks() 
        esperando_siguiente = True 
    except ValueError:
        pass

def chequear_y_guardar_logros():
    global logros
    if score >= 1000: logros["pts_1000"] = 1
    if max_combo_partida >= 100: logros["combo_100"] = 1
    if es_modo_caos_activo: return 
    
    dicc_operaciones = {'SUMA': 'suma', 'RESTA': 'resta', 'MULTIPLICAR': 'mult', 'DIVISION': 'div', 'MIXTO': 'mixto', 'FRACCION': 'frac'}
    dicc_dificultades = {'FACIL': (35, 'facil'), 'MEDIO': (30, 'medio'), 'DIFICIL': (25, 'dificil')}
    
    op_clave = dicc_operaciones.get(operacion_seleccionada)
    dif_info = dicc_dificultades.get(dificultad_seleccionada)
    
    if op_clave and dif_info:
        meta_resueltos, dif_clave = dif_info
        if resueltos_esta_partida >= meta_resueltos:
            logros[f"{op_clave}_{dif_clave}"] = 1

def finalizar_y_guardar_partida():
    global high_score, nombre_record, resueltos_record, combo_record, caos_high_score
    chequear_y_guardar_logros()
    
    if es_modo_caos_activo:
        if score > caos_high_score:
            caos_high_score = score
    else:
        if score > high_score:
            high_score = score
            nombre_record = nombre_actual_usuario.upper() if nombre_actual_usuario.strip() != "" else "ANONIMO"
            resueltos_record = resueltos
            combo_record = max_combo_partida
            
    guardar_record()
    reiniciar_juego()

def reiniciar_juego():
    global score, resueltos, resueltos_esta_partida, vidas, combo, max_combo_partida, estado_actual, esperando_siguiente, mensaje_feedback, nombre_actual_usuario
    global primer_tiempo_agotado, combo_congelado, tiempo_acumulado_antes_pausa, es_modo_caos_activo, caos_tiempo_castigo_activo
    score, resueltos, resueltos_esta_partida, vidas, combo, max_combo_partida = 0, 0, 0, 3, 1, 1
    mensaje_feedback = ""
    nombre_actual_usuario = ""
    esperando_siguiente = False
    primer_tiempo_agotado = False
    combo_congelado = False
    es_modo_caos_activo = False
    caos_tiempo_castigo_activo = False
    tiempo_acumulado_antes_pausa = 0
    estado_actual = 'MENU'

# ==========================================
# VISTAS / PANTALLAS 
# ==========================================
def pantalla_menu():
    pantalla.fill(PALETA_FONDO_MENU) 
    dibujar_texto("EL MATE JUEGO", fuente_titulo, PASTEL_TURQUESA, ANCHO // 2, 90, centro=True, ancho_max=400, tam_base=44)
    dibujar_texto(f"TOP: {high_score} PTS ({nombre_record}) | CAOS TOP: {caos_high_score}", fuente_interfaz, PASTEL_CREMA, ANCHO // 2, 155, centro=True, ancho_max=420, tam_base=18)
    
    crear_boton("JUGAR", 115, 220, 220, 52, PASTEL_VERDE_MENTA, TEXTO_OSCURO)
    crear_boton("MODO CAOS", 115, 305, 220, 52, CAOS_VIVO, BLANCO)  
    crear_boton("SCORE", 115, 390, 220, 52, PASTEL_CELESTE_MAR, TEXTO_OSCURO)
    crear_boton("LOGROS", 115, 475, 220, 52, PASTEL_LAVANDA, TEXTO_OSCURO)
    crear_boton("SALIR", 115, 560, 220, 52, PASTEL_CORAL, TEXTO_OSCURO)

def pantalla_modo_caos_info():
    pantalla.fill(CAOS_FONDO)
    dibujar_texto("MODO CAOS", fuente_titulo, CAOS_TITULO, ANCHO // 2, 70, centro=True, ancho_max=400, tam_base=44)
    
    pygame.draw.rect(pantalla, CAOS_PANEL, (35, 130, 380, 460), border_radius=16)
    pygame.draw.rect(pantalla, CAOS_NARANJA, (35, 130, 380, 460), width=2, border_radius=16)
    
    dibujar_texto("INSTRUCCIONES:", fuente_logros_tit, CAOS_NARANJA, ANCHO // 2, 165, centro=True, ancho_max=340, tam_base=26)
    
    dibujar_texto("• UNA SOLA VIDA", fuente_interfaz, BLANCO, 60, 215, ancho_max=330, tam_base=20)
    dibujar_texto("• SOLO 15 SEGUNDOS", fuente_interfaz, BLANCO, 60, 255, ancho_max=330, tam_base=20)
    dibujar_texto("• SOLO 3 PTS POR CADA ACIERTO", fuente_interfaz, BLANCO, 60, 295, ancho_max=330, tam_base=20)
    dibujar_texto("• CADA VEZ SUBE LA DIFICULTAD", fuente_interfaz, BLANCO, 60, 335, ancho_max=330, tam_base=20)
    dibujar_texto("• Y EL TIEMPO DISMINUYE", fuente_interfaz, BLANCO, 60, 375, ancho_max=330, tam_base=20)
    dibujar_texto("• COMBO POR X2", fuente_interfaz, BLANCO, 60, 415, ancho_max=330, tam_base=20)
    
    lineas = [
        "SI DEJAS QUE SE TE ACABE EL TIEMPO UNA VEZ,",
        "NO PIERDES LA VIDA, PERO AHORA SOLO",
        "TENDRAS 6S PARA TODO. PERO GANARAS 25",
        "POR CADA ACIERTO Y TU MULTIPLICADOR POR 10."
    ]
    y_adv = 465
    for linea in lineas:
        dibujar_texto(linea, fuente_interfaz, CAOS_TEXTO_DESAC, ANCHO // 2, y_adv, centro=True, ancho_max=340, tam_base=15)
        y_adv += 20

    dibujar_texto("BUENA SUERTE...", fuente_botones, CAOS_ALERTA, ANCHO // 2, 560, centro=True, ancho_max=340, tam_base=24)
    
    crear_boton("¡EMPEZAR EL CAOS!", 75, 625, 300, 52, CAOS_VIVO, BLANCO)
    crear_boton("< VOLVER", 25, 25, 110, 35, PASTEL_GRIS_CLARO, TEXTO_OSCURO, radio=8, tam_letra=18)

def pantalla_modos():
    pantalla.fill(PALETA_FONDO_MENU)
    dibujar_texto("MODOS DE JUEGO", fuente_titulo, PASTEL_AMARILLO, ANCHO // 2, 85, centro=True, ancho_max=400, tam_base=42)
    crear_boton("< VOLVER", 25, 25, 110, 38, PASTEL_ROSA_VIEJO, TEXTO_OSCURO, radio=8)
    
    colores_botones = [PASTEL_CELESTE_MAR, PASTEL_DURAZNO, PASTEL_LAVANDA, PASTEL_VERDE_MENTA, PASTEL_ROSA_CHICLE, PASTEL_CREMA]
    coordenadas = [(50, 180), (240, 180), (50, 330), (240, 330), (50, 480), (240, 480)]
    opciones = ["SUMA", "RESTA", "MULTIPLICAR", "DIVISION", "MIXTO", "FRACCION"]
    
    for i, (op, x, y) in enumerate(zip(opciones, [c[0] for c in coordenadas], [c[1] for c in coordenadas])):
        crear_boton(op, x, y, 160, 115, colores_botones[i], TEXTO_OSCURO)

def pantalla_dificultad():
    pantalla.fill(PALETA_FONDO_MENU) 
    dibujar_texto("DIFICULTAD", fuente_titulo, PASTEL_LAVANDA, ANCHO // 2, 100, centro=True, ancho_max=400, tam_base=42)
    crear_boton("< VOLVER", 25, 25, 110, 38, PASTEL_GRIS_CLARO, TEXTO_OSCURO, radio=8)
    
    crear_boton("FACIL", 75, 240, 300, 75, PASTEL_VERDE_MENTA, TEXTO_OSCURO)
    crear_boton("MEDIO", 75, 360, 300, 75, PASTEL_DURAZNO, TEXTO_OSCURO)
    crear_boton("DIFICIL", 75, 480, 300, 75, PASTEL_CORAL, TEXTO_OSCURO)

def pantalla_juego_en_curso():
    global estado_actual, vidas, segundos_restantes, esperando_siguiente, mensaje_feedback, feedback_timer, combo, tiempo_limite_actual
    global primer_tiempo_agotado, combo_congelado, score, tiempo_acumulado_antes_pausa, caos_tiempo_castigo_activo
    
    pantalla.fill(CAOS_FONDO if es_modo_caos_activo else PALETA_FONDO_MENU) 
    
    if esperando_siguiente and pygame.time.get_ticks() - feedback_timer > 1200:
        if vidas <= 0: estado_actual = 'GAME_OVER' 
        else: generar_ejercicio()

    if not esperando_siguiente:
        tiempo_transcurrido = ((pygame.time.get_ticks() - tiempo_inicial_ejercicio) // 1000) + tiempo_acumulado_antes_pausa
        segundos_restantes = max(0, tiempo_limite_actual - tiempo_transcurrido)
        
        if segundos_restantes <= 0:
            if es_modo_caos_activo:
                if not caos_tiempo_castigo_activo:
                    caos_tiempo_castigo_activo = True
                    combo = 1
                    mensaje_feedback = "¡MÓDULO DE 6S ACTIVADO!"
                else:
                    vidas -= 1
                    combo = 1
                    mensaje_feedback = "¡TIEMPO AGOTADO!"
            else:
                if not primer_tiempo_agotado:
                    score = max(0, score - 10)
                    primer_tiempo_agotado = True
                    combo_congelado = True  
                    mensaje_feedback = "¡TIEMPO! COMBO BLOQUEADO"
                else:
                    vidas -= 1
                    aplicar_penalizacion_puntos()
                    combo = 1
                    combo_congelado = False
                    mensaje_feedback = "¡TIEMPO AGOTADO!"
                
            feedback_timer = pygame.time.get_ticks()
            esperando_siguiente = True

    color_boton_pausa = CAOS_PANEL if es_modo_caos_activo else PASTEL_CELESTE_MAR
    color_txt_pausa = BLANCO if es_modo_caos_activo else TEXTO_OSCURO
    crear_boton("II", 30, 45, 50, 50, color_boton_pausa, color_txt_pausa, radio=10)
    
    color_reloj = CAOS_TITULO if es_modo_caos_activo else (PASTEL_AMARILLO if segundos_restantes > 4 else PASTEL_CORAL)
    dibujar_texto(f"⏱️ {segundos_restantes}S", fuente_titulo, color_reloj, ANCHO // 2, 75, centro=True, ancho_max=180, tam_base=44)
    
    dibujar_texto(f"RESUELTO: {resueltos}", fuente_interfaz, CAOS_TITULO if es_modo_caos_activo else PASTEL_DURAZNO, 300, 60, ancho_max=140, tam_base=20)
    dibujar_texto(f"SCORE: {score}", fuente_interfaz, BLANCO, 30, 130, ancho_max=150, tam_base=22)
    dibujar_texto(f"VIDAS: {vidas}", fuente_interfaz, CAOS_VIVO if es_modo_caos_activo else PASTEL_CORAL, 340, 130, ancho_max=100, tam_base=22)
    
    if es_modo_caos_activo:
        tipo_caos_txt = f"CAOS {dificultad_seleccionada}"
        dibujar_texto(tipo_caos_txt, fuente_interfaz, CAOS_NARANJA, ANCHO // 2, 25, centro=True, ancho_max=400, tam_base=18)
    elif combo_congelado and not esperando_siguiente:
        dibujar_texto("⚠️ COMBO BLOQUEADO (SIN X3)", fuente_interfaz, PASTEL_CORAL, ANCHO // 2, 25, centro=True, ancho_max=400, tam_base=18)

    # --- RENDERIZADO DE OPERACIONES MATEMÁTICAS ---
    if not es_modo_fraccion:
        if operador_simbolo == "/":
            txt_dividendo = fuente_juego.render(f"{num1}", True, BLANCO)
            txt_divisor = fuente_juego.render(f"{num2}", True, BLANCO)
            x_dividendo, y_operacion = 110, 260
            pantalla.blit(txt_dividendo, (x_dividendo, y_operacion))
            x_linea_vertical = x_dividendo + txt_dividendo.get_width() + 15
            color_divisor_linea = CAOS_NARANJA if es_modo_caos_activo else BLANCO
            pygame.draw.line(pantalla, color_divisor_linea, (x_linea_vertical, y_operacion - 10), (x_linea_vertical, y_operacion + 110), width=4)
            x_divisor = x_linea_vertical + 15
            pantalla.blit(txt_divisor, (x_divisor, y_operacion))
            y_linea_horizontal = y_operacion + txt_divisor.get_height() + 5
            x_fin_linea_horizontal = x_divisor + max(txt_divisor.get_width() + 20, 120)
            pygame.draw.line(pantalla, color_divisor_linea, (x_linea_vertical, y_linea_horizontal), (x_fin_linea_horizontal, y_linea_horizontal), width=4)
            mostrar_respuesta = respuesta_usuario if respuesta_usuario != "" else "?"
            dibujar_texto(mostrar_respuesta, fuente_juego, PASTEL_VERDE_MENTA, x_divisor, y_linea_horizontal + 15, ancho_max=150, tam_base=50)
        else:
            EJE_ALINEACION_DERECHA = 280
            txt_n1 = fuente_juego.render(f"{num1}", True, BLANCO)
            txt_n2 = fuente_juego.render(f"{num2}", True, BLANCO)
            pantalla.blit(txt_n1, (EJE_ALINEACION_DERECHA - txt_n1.get_width(), 230))
            pantalla.blit(txt_n2, (EJE_ALINEACION_DERECHA - txt_n2.get_width(), 285))
            dibujar_texto(operador_simbolo, fuente_juego, BLANCO, EJE_ALINEACION_DERECHA - txt_n2.get_width() - 45, 285, ancho_max=50, tam_base=50)
            
            if operador_simbolo == "+":
                str_n1, str_n2 = str(num1)[::-1], str(num2)[::-1]
                acarreo_actual, columnas_escritas = 0, len(respuesta_usuario)
                for i in range(max(len(str_n1), len(str_n2))):
                    d1 = int(str_n1[i]) if i < len(str_n1) else 0
                    d2 = int(str_n2[i]) if i < len(str_n2) else 0
                    suma_columna = d1 + d2 + acarreo_actual
                    acarreo_actual = suma_columna // 10 if suma_columna >= 10 else 0
                    if acarreo_actual > 0 and i < columnas_escritas:
                        dibujar_texto(str(acarreo_actual), fuente_interfaz, CAOS_TITULO if es_modo_caos_activo else PASTEL_CREMA, EJE_ALINEACION_DERECHA - (i + 2) * 24, 190, ancho_max=20, tam_base=18)

            color_base_barra = CAOS_NARANJA if es_modo_caos_activo else BLANCO
            pygame.draw.line(pantalla, color_base_barra, (140, 350), (310, 350), width=4)
            
            mostrar_respuesta = "?" if respuesta_usuario == "" else respuesta_usuario
            superficie_resp = renderizar_con_ajuste(mostrar_respuesta, 50, 160, PASTEL_VERDE_MENTA)
            
            pantalla.blit(superficie_resp, (EJE_ALINEACION_DERECHA - superficie_resp.get_width(), 370))
    else:
        if dificultad_seleccionada in ['FACIL', 'MEDIO']:
            dibujar_fraccion(str(num1), str(num2 if operador_simbolo == "x" else frac_resp_den_correcta), 95, 250, ancho_linea=45)
            dibujar_texto(operador_simbolo, fuente_juego, BLANCO, 175, 275, ancho_max=40, tam_base=48)
            dibujar_fraccion(str(num2), str(num1 if operador_simbolo == "x" else frac_resp_den_correcta), 220, 250, ancho_linea=45)
            dibujar_texto("=", fuente_juego, BLANCO, 295, 275, ancho_max=40, tam_base=48)
            dibujar_fraccion(respuesta_usuario if respuesta_usuario != "" else "?", str(frac_resp_den_correcta), 345, 250, color_num=PASTEL_VERDE_MENTA, color_den=PASTEL_GRIS_CLARO, ancho_linea=50)
        else:
            dibujar_fraccion(str(dif_n1), str(dif_d1), 35, 250, ancho_linea=35)
            dibujar_texto(dif_op1, fuente_juego, BLANCO, 95, 275, ancho_max=35, tam_base=44)
            dibujar_fraccion(str(dif_n2), str(dif_d2), 140, 250, ancho_linea=35)
            dibujar_texto(dif_op2, fuente_juego, BLANCO, 200, 275, ancho_max=35, tam_base=44)
            dibujar_fraccion(str(dif_n3), str(dif_d3), 245, 250, ancho_linea=35)
            dibujar_texto("=", fuente_juego, BLANCO, 305, 275, ancho_max=35, tam_base=44)
            c_num = PASTEL_VERDE_MENTA if foco_respuesta == "NUMERADOR" else BLANCO
            c_den = PASTEL_VERDE_MENTA if foco_respuesta == "DENOMINADOR" else BLANCO
            dibujar_fraccion(respuesta_usuario_num if respuesta_usuario_num != "" else "?", respuesta_usuario_den if respuesta_usuario_den != "" else "?", 355, 250, color_num=c_num, color_den=c_den, ancho_linea=55)

    if esperando_siguiente: 
        color_feed = PASTEL_VERDE_MENTA if "CORRECTO" in mensaje_feedback else (CAOS_VIVO if es_modo_caos_activo else PASTEL_CORAL)
        dibujar_texto(mensaje_feedback, fuente_titulo, color_feed, ANCHO // 2, 510, centro=True, ancho_max=400, tam_base=40)

    crear_boton("SALTAR", 40, 650, 150, 50, CAOS_PANEL if es_modo_caos_activo else PASTEL_ROSA_VIEJO, BLANCO if es_modo_caos_activo else TEXTO_OSCURO)
    color_combo_txt = CAOS_NARANJA if es_modo_caos_activo else PASTEL_LAVANDA
    dibujar_texto(f"COMBO: X{combo}", fuente_interfaz, color_combo_txt, 260, 665, ancho_max=150, tam_base=22)

def pantalla_pausa():
    pantalla.fill(CAOS_FONDO if es_modo_caos_activo else PALETA_FONDO_RECORTE) 
    dibujar_texto("JUEGO EN PAUSA", fuente_titulo, CAOS_TITULO if es_modo_caos_activo else PASTEL_DURAZNO, ANCHO // 2, 120, centro=True, ancho_max=400, tam_base=44)
    dibujar_texto("¡ATENCION! PERDERAS TU PROGRESO ACTUAL", fuente_interfaz, CAOS_TEXTO_DESAC if es_modo_caos_activo else TEXTO_DESACTIVADO, ANCHO // 2, 185, centro=True, ancho_max=410, tam_base=18)
    
    crear_boton("MENU", 100, 260, 250, 52, PASTEL_GRIS_CLARO, TEXTO_OSCURO)
    
    if es_modo_caos_activo:
        crear_boton("---", 100, 340, 250, 52, CAOS_PANEL, CAOS_TEXTO_DESAC)
        crear_boton("---", 100, 420, 250, 52, CAOS_PANEL, CAOS_TEXTO_DESAC)
    else:
        crear_boton("DIFICULTAD", 100, 340, 250, 52, PASTEL_GRIS_CLARO, TEXTO_OSCURO)
        crear_boton("MODOS DE JUEGO", 100, 420, 250, 52, PASTEL_GRIS_CLARO, TEXTO_OSCURO)
        
    crear_boton("SALIR", 100, 500, 250, 52, PASTEL_CORAL, TEXTO_OSCURO)
    crear_boton("VOLVER AL JUEGO", 100, 620, 250, 55, CAOS_VIVO if es_modo_caos_activo else PASTEL_VERDE_MENTA, BLANCO if es_modo_caos_activo else TEXTO_OSCURO)

def pantalla_game_over():
    pantalla.fill(PALETA_FONDO_RECORTE)
    dibujar_texto("¡FIN DEL JUEGO!", fuente_titulo, PASTEL_CORAL, ANCHO // 2, 120, centro=True, ancho_max=400, tam_base=44)
    dibujar_texto(f"TU PUNTUACION: {score}", fuente_juego, BLANCO, ANCHO // 2, 205, centro=True, ancho_max=400, tam_base=48)
    
    if (es_modo_caos_activo and score > caos_high_score) or (not es_modo_caos_activo and score > high_score): 
        dibujar_texto("¡NUEVO RECORD ALCANZADO!", fuente_interfaz, PASTEL_AMARILLO, ANCHO // 2, 280, centro=True, ancho_max=400, tam_base=22)
    else: 
        dibujar_texto(f"RECORD ACTUAL: {high_score} POR {nombre_record}", fuente_interfaz, TEXTO_DESACTIVADO, ANCHO // 2, 280, centro=True, ancho_max=400, tam_base=18)
        
    dibujar_texto("ESCRIBE TU NOMBRE:", fuente_interfaz, BLANCO, ANCHO // 2, 370, centro=True, ancho_max=300, tam_base=20)
    pygame.draw.rect(pantalla, PALETA_FONDO_MENU, (75, 410, 300, 55), border_radius=10)
    pygame.draw.rect(pantalla, PASTEL_CELESTE_MAR, (75, 410, 300, 55), width=2, border_radius=10)
    
    mostrar_nombre = nombre_actual_usuario.upper() if nombre_actual_usuario != "" else "ESCRIBE AQUI..."
    color_nombre = BLANCO if nombre_actual_usuario != "" else TEXTO_DESACTIVADO
    dibujar_texto(mostrar_nombre, fuente_botones, color_nombre, ANCHO // 2, 437, centro=True, ancho_max=280, tam_base=26)
    
    dibujar_texto("PRESIONA ENTER PARA GUARDAR Y SALIR", fuente_interfaz, TEXTO_DESACTIVADO, ANCHO // 2, 515, centro=True, ancho_max=400, tam_base=16)
    crear_boton("MENU PRINCIPAL", 100, 590, 250, 55, PASTEL_GRIS_CLARO, TEXTO_OSCURO)

def pantalla_ver_score():
    pantalla.fill(PALETA_FONDO_MENU) 
    dibujar_texto("RECORD MAXIMO", fuente_titulo, PASTEL_AMARILLO, ANCHO // 2, 90, centro=True, ancho_max=400, tam_base=42)
    pygame.draw.line(pantalla, BLANCO, (80, 135), (370, 135), width=2)
    pygame.draw.rect(pantalla, PALETA_FONDO_RECORTE, (50, 175, 350, 335), border_radius=16)
    
    dibujar_texto("JUGADOR:", fuente_interfaz, TEXTO_DESACTIVADO, 80, 205, ancho_max=150, tam_base=18)
    dibujar_texto(f"{nombre_record}", fuente_botones, BLANCO, 80, 230, ancho_max=290, tam_base=26)
    dibujar_texto("PUNTUACIÓN NORMAL:", fuente_interfaz, TEXTO_DESACTIVADO, 80, 290, ancho_max=200, tam_base=18)
    dibujar_texto(f"{high_score} PUNTOS", fuente_juego, PASTEL_VERDE_MENTA, 80, 315, ancho_max=290, tam_base=46)
    
    # Añadido del récord caos a la visualización
    dibujar_texto(f"RÉCORD MODO CAOS: {caos_high_score} PTS", fuente_botones, CAOS_TITULO, 80, 395, ancho_max=320, tam_base=24)
    
    dibujar_texto("EJERCICIOS RESUELTOS:", fuente_interfaz, TEXTO_DESACTIVADO, 80, 445, ancho_max=250, tam_base=18)
    dibujar_texto(f"{resueltos_record} ACIERTOS", fuente_botones, BLANCO, 80, 470, ancho_max=290, tam_base=26)
    
    crear_boton("< VOLVER AL MENÚ", 100, 590, 250, 55, PASTEL_GRIS_CLARO, TEXTO_OSCURO)

desplazamiento_logros = 0 

def pantalla_ver_logros():
    global desplazamiento_logros
    pantalla.fill(PALETA_FONDO_MENU) 
    dibujar_texto("LOGROS Y TROFEOS", fuente_titulo, PASTEL_LAVANDA, ANCHO // 2, 55, centro=True, ancho_max=400, tam_base=42)
    
    ancho_lista = 390
    superficie_lista = pygame.Surface((ancho_lista, len(INFO_LOGROS) * 75)) 
    superficie_lista.fill(PALETA_FONDO_MENU)
    
    for i, (titulo, desc, clave, es_caos) in enumerate(INFO_LOGROS):
        y_pos = i * 72
        desbloqueado = logros[clave] == 1
        
        # --- NUEVA LÓGICA DE COLORES DEL MODO CAOS PARA SUS TROFEOS ---
        if es_caos:
            color_caja = CAOS_PANEL if desbloqueado else PALETA_FONDO_RECORTE
            color_borde = CAOS_VIVO if desbloqueado else CAOS_TEXTO_DESAC
            c_tit = CAOS_TITULO if desbloqueado else TEXTO_DESACTIVADO
            c_desc = BLANCO if desbloqueado else CAOS_TEXTO_DESAC
            texto_titulo = f"🔥 {titulo}".upper() if desbloqueado else f"🔒 CAOS BLOQUEADO"
        else:
            # Colores Pastel tradicionales para logros comunes
            color_caja = PASTEL_ROSA_CHICLE if desbloqueado else PALETA_FONDO_RECORTE
            color_borde = PASTEL_LAVANDA if desbloqueado else PASTEL_GRIS_CLARO
            c_tit = TEXTO_OSCURO if desbloqueado else TEXTO_DESACTIVADO
            c_desc = PALETA_FONDO_MENU if desbloqueado else PASTEL_GRIS_CLARO
            texto_titulo = f"🏆 {titulo}".upper() if desbloqueado else f"🔒 BLOQUEADO"
        
        pygame.draw.rect(superficie_lista, color_caja, (0, y_pos, ancho_lista, 65), border_radius=12)
        pygame.draw.rect(superficie_lista, color_borde, (0, y_pos, ancho_lista, 65), width=2, border_radius=12)
        
        sup_t = renderizar_con_ajuste(texto_titulo, 24, ancho_lista - 30, c_tit)
        sup_d = renderizar_con_ajuste(desc, 18, ancho_lista - 30, c_desc)
        
        superficie_lista.blit(sup_t, (15, y_pos + 10))
        superficie_lista.blit(sup_d, (15, y_pos + 36))
        
    pantalla.blit(superficie_lista, (30, 115), (0, desplazamiento_logros, ancho_lista, ALTO_LISTA_LOGROS))
    
    dibujar_texto("USA LAS FLECHAS ARRIBA / ABAJO PARA NAVEGAR", fuente_interfaz, TEXTO_DESACTIVADO, ANCHO // 2, 595, centro=True, ancho_max=420, tam_base=16)
    crear_boton("< VOLVER AL MENÚ", 100, 635, 250, 55, PASTEL_GRIS_CLARO, TEXTO_OSCURO)

# ==========================================
# BUCLE PRINCIPAL Y EVENTOS CENTRALIZADOS
# ==========================================
ejecutando = True
while ejecutando:
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if estado_actual == 'MENU':
                if pygame.Rect(115, 220, 220, 52).collidepoint(pos): estado_actual = 'MODOS'
                elif pygame.Rect(115, 305, 220, 52).collidepoint(pos): estado_actual = 'MODO_CAOS_INFO' 
                elif pygame.Rect(115, 390, 220, 52).collidepoint(pos): estado_actual = 'PANTALLA_SCORE'
                elif pygame.Rect(115, 475, 220, 52).collidepoint(pos): estado_actual = 'PANTALLA_LOGROS'; desplazamiento_logros = 0
                elif pygame.Rect(115, 560, 220, 52).collidepoint(pos): ejecutando = False
            elif estado_actual == 'MODO_CAOS_INFO':
                if pygame.Rect(75, 625, 300, 52).collidepoint(pos): 
                    es_modo_caos_activo = True
                    vidas = 1
                    score = 0
                    resueltos = 0
                    combo = 1
                    preparar_cola_modo_caos()
                    generar_ejercicio()
                    estado_actual = 'JUEGO'
                elif pygame.Rect(25, 25, 110, 35).collidepoint(pos): 
                    estado_actual = 'MENU'
            elif estado_actual == 'PANTALLA_SCORE':
                if pygame.Rect(100, 590, 250, 55).collidepoint(pos): estado_actual = 'MENU'
            elif estado_actual == 'PANTALLA_LOGROS':
                if pygame.Rect(100, 635, 250, 55).collidepoint(pos): estado_actual = 'MENU'
            elif estado_actual == 'MODOS':
                if pygame.Rect(25, 25, 110, 38).collidepoint(pos): estado_actual = 'MENU'
                else:
                    coordenadas = [(50, 180), (240, 180), (50, 330), (240, 330), (50, 480), (240, 480)]
                    opciones = ["SUMA", "RESTA", "MULTIPLICAR", "DIVISION", "MIXTO", "FRACCION"]
                    for op, (x, y) in zip(opciones, coordenadas):
                        if pygame.Rect(x, y, 160, 115).collidepoint(pos): operacion_seleccionada = op; estado_actual = 'DIFICULTAD'
            elif estado_actual == 'DIFICULTAD':
                if pygame.Rect(25, 25, 110, 38).collidepoint(pos): estado_actual = 'MODOS'
                elif pygame.Rect(75, 240, 300, 75).collidepoint(pos): dificultad_seleccionada, estado_actual = 'FACIL', 'JUEGO'; generar_ejercicio()
                elif pygame.Rect(75, 360, 300, 75).collidepoint(pos): dificultad_seleccionada, estado_actual = 'MEDIO', 'JUEGO'; generar_ejercicio()
                elif pygame.Rect(75, 480, 300, 75).collidepoint(pos): dificultad_seleccionada, estado_actual = 'DIFICIL', 'JUEGO'; generar_ejercicio()
            elif estado_actual == 'JUEGO':
                if pygame.Rect(40, 650, 150, 50).collidepoint(pos) and not esperando_siguiente:
                    aplicar_penalizacion_saltar() 
                    generar_ejercicio()           
                elif pygame.Rect(30, 45, 50, 50).collidepoint(pos): 
                    tiempo_acumulado_antes_pausa += (pygame.time.get_ticks() - tiempo_inicial_ejercicio) // 1000
                    estado_actual = 'PAUSA'
            elif estado_actual == 'PAUSA':
                if pygame.Rect(100, 260, 250, 52).collidepoint(pos): reiniciar_juego() 
                elif pygame.Rect(100, 340, 250, 52).collidepoint(pos) and not es_modo_caos_activo: reiniciar_juego(); estado_actual = 'DIFICULTAD' 
                elif pygame.Rect(100, 420, 250, 52).collidepoint(pos) and not es_modo_caos_activo: reiniciar_juego(); estado_actual = 'MODOS' 
                elif pygame.Rect(100, 500, 250, 52).collidepoint(pos): ejecutando = False 
                elif pygame.Rect(100, 620, 250, 55).collidepoint(pos): 
                    tiempo_inicial_ejercicio = pygame.time.get_ticks()
                    estado_actual = 'JUEGO'
            elif estado_actual == 'GAME_OVER':
                if pygame.Rect(100, 590, 250, 55).collidepoint(pos):
                    finalizar_y_guardar_partida()

        elif evento.type == pygame.KEYDOWN:
            if estado_actual == 'PANTALLA_LOGROS':
                if evento.key == pygame.K_DOWN: desplazamiento_logros = min(desplazamiento_logros + 40, (len(INFO_LOGROS) * 72) - ALTO_LISTA_LOGROS)
                elif evento.key == pygame.K_UP: desplazamiento_logros = max(desplazamiento_logros - 40, 0)
            
            elif estado_actual == 'JUEGO' and not esperando_siguiente:
                if es_modo_fraccion and dificultad_seleccionada == 'DIFICIL':
                    if evento.key == pygame.K_RETURN:
                        if respuesta_usuario_num != "" and respuesta_usuario_den != "": verificar_respuesta()
                        else: foco_respuesta = "DENOMINADOR"
                    elif evento.key == pygame.K_SLASH: foco_respuesta = "DENOMINADOR" if foco_respuesta == "NUMERADOR" else "NUMERADOR"
                    elif evento.key == pygame.K_BACKSPACE:
                        if foco_respuesta == "NUMERADOR": respuesta_usuario_num = respuesta_usuario_num[:-1]
                        else: respuesta_usuario_den = respuesta_usuario_den[:-1]
                    elif evento.unicode.isdigit():
                        if foco_respuesta == "NUMERADOR" and len(respuesta_usuario_num) < 6: respuesta_usuario_num += evento.unicode
                        elif foco_respuesta == "DENOMINADOR" and len(respuesta_usuario_den) < 6: respuesta_usuario_den += evento.unicode
                else:
                    if evento.key == pygame.K_RETURN: 
                        verificar_respuesta()
                    elif evento.key == pygame.K_BACKSPACE: 
                        respuesta_usuario = respuesta_usuario[:-1]
                    elif evento.unicode.isdigit() and len(respuesta_usuario) < 8:
                        if operador_simbolo in ["+", "-", "x"]:
                            respuesta_usuario = evento.unicode + respuesta_usuario
                        else:
                            respuesta_usuario += evento.unicode
                    elif evento.key == pygame.K_MINUS and len(respuesta_usuario) == 0: 
                        respuesta_usuario += "-"
            
            elif estado_actual == 'GAME_OVER':
                if evento.key == pygame.K_RETURN:
                    finalizar_y_guardar_partida()
                elif evento.key == pygame.K_BACKSPACE: nombre_actual_usuario = nombre_actual_usuario[:-1]
                else:
                    if len(nombre_actual_usuario) < 14 and evento.unicode.isprintable(): nombre_actual_usuario += evento.unicode.upper()

    # Renderizado estructural de estados
    if estado_actual == 'MENU': pantalla_menu()
    elif estado_actual == 'MODO_CAOS_INFO': pantalla_modo_caos_info() 
    elif estado_actual == 'MODOS': pantalla_modos()
    elif estado_actual == 'DIFICULTAD': pantalla_dificultad()
    elif estado_actual == 'JUEGO': pantalla_juego_en_curso()
    elif estado_actual == 'PAUSA': pantalla_pausa()
    elif estado_actual == 'GAME_OVER': pantalla_game_over()
    elif estado_actual == 'PANTALLA_SCORE': pantalla_ver_score()
    elif estado_actual == 'PANTALLA_LOGROS': pantalla_ver_logros()

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()
