import pygame
import math
import sys
import random

# Inicialización
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Tiro Parabólico")
font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 40)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Constantes físicas
GRAVEDAD = 9.81
ESCALA = 10  # 1 metro = 10 píxeles

# Inputs
input_boxes = {
    "masa": pygame.Rect(100, 50, 140, 32),
    "angulo": pygame.Rect(100, 100, 140, 32),
    "potencia": pygame.Rect(100, 150, 140, 32)
}
inputs = {"masa": "Kg", "angulo": "Grados", "potencia": "Joules"}
active_input = None

def calcular_velocidad_inicial(potencia, masa):
    return math.sqrt((2 * potencia) / masa)

def dibujar_texto(texto, x, y, fuente=font, color=BLACK):
    label = fuente.render(texto, True, color)
    screen.blit(label, (x, y))

def disparar(masa, angulo_deg, energia):
    if masa <= 0:
        return []

    angulo_rad = math.radians(angulo_deg)
    v0 = calcular_velocidad_inicial(energia, masa)
    t = 0
    puntos = []

    base_x, base_y = 50, HEIGHT - 50  # Posición de lanzamiento en píxeles

    while True:
        x = v0 * math.cos(angulo_rad) * t  # x en metros
        y = v0 * math.sin(angulo_rad) * t - 0.5 * GRAVEDAD * t ** 2  # y en metros

        if y < 0:
            break

        pantalla_x = int(x * ESCALA) + base_x
        pantalla_y = HEIGHT - int(y * ESCALA) - (HEIGHT - base_y)

        if pantalla_y > HEIGHT or pantalla_x > WIDTH:
            break

        puntos.append((pantalla_x, pantalla_y))
        t += 0.05  # Más precisión

    return puntos

def pantalla_final(mensaje, reiniciar_visible):
    screen.fill(WHITE)
    dibujar_texto(mensaje, 200, 250, big_font, RED)
    dibujar_texto("Presiona 'Reiniciar' para volver a jugar", 200, 320, font)
    boton_reiniciar = pygame.Rect(300, 380, 200, 40)
    pygame.draw.rect(screen, GREEN, boton_reiniciar)
    dibujar_texto("Reiniciar", 360, 390, font)
    pygame.display.flip()
    return boton_reiniciar

def main():
    global active_input, inputs

    clock = pygame.time.Clock()
    disparo = False
    puntos_disparo = []
    resultado = ""
    vidas = 5
    aciertos = 0

    # Objetivo en metros
    objetivo_x_m = random.uniform(35, 70)  # metros desde el cañón
    objetivo_y_m = random.uniform(3, 30)   # altura en metros sobre el suelo

    estado_juego = "jugando"
    boton_reiniciar = None

    while True:
        screen.fill(WHITE)

        # Dibujar campos de entrada
        for key, box in input_boxes.items():
            color = GREEN if active_input == key else BLACK
            pygame.draw.rect(screen, color, box, 2)
            txt_surface = font.render(inputs[key], True, BLACK)
            screen.blit(txt_surface, (box.x + 5, box.y + 5))
            dibujar_texto(key.capitalize(), box.x - 80, box.y + 5)

        # Botón de disparo
        boton = pygame.Rect(100, 200, 140, 32)
        pygame.draw.rect(screen, BLUE, boton)
        dibujar_texto("Disparar", 130, 205)

        # Mostrar vidas y puntos
        dibujar_texto(f"Vidas: {vidas}", 600, 50)
        dibujar_texto(f"Aciertos: {aciertos}/5", 600, 80)

        # --- DIBUJAR CAÑONCITO ---
        base_x, base_y = 50, HEIGHT - 50  # Posición de lanzamiento
        pygame.draw.circle(screen, (80, 80, 80), (base_x, base_y), 18)  # Base del cañón

        # Dibuja el tubo del cañón según el ángulo ingresado (si es válido)
        try:
            angulo = float(inputs["angulo"])
        except:
            angulo = 45  # Valor por defecto si no hay ángulo válido

        # Calcula la dirección del cañón
        longitud_canon = 40
        rad = math.radians(angulo)
        punta_x = int(base_x + longitud_canon * math.cos(rad))
        punta_y = int(base_y - longitud_canon * math.sin(rad))
        pygame.draw.line(screen, (60, 60, 60), (base_x, base_y), (punta_x, punta_y), 8)

        # Dibujar objetivo (si no ha terminado el juego)
        if estado_juego == "jugando":
            objetivo_x = int(objetivo_x_m * ESCALA) + base_x
            objetivo_y = HEIGHT - int(objetivo_y_m * ESCALA) - (HEIGHT - base_y)
            objetivo_ancho = int(1 * ESCALA)   # 1 metro de ancho
            objetivo_alto = int(4 * ESCALA)    # 4 metros de alto
            pygame.draw.rect(screen, RED, (objetivo_x, objetivo_y, objetivo_ancho, objetivo_alto))
            # Mostrar distancia y altura en metros
            dibujar_texto(f"Distancia: {objetivo_x_m:.1f} m",  350,  70)
            dibujar_texto(f"Altura: {objetivo_y_m:.1f} m",   350,  50)

        # Evento
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif estado_juego == "final":
                if event.type == pygame.MOUSEBUTTONDOWN and boton_reiniciar and boton_reiniciar.collidepoint(event.pos):
                    # Reiniciar juego
                    vidas = 5
                    aciertos = 0
                    resultado = ""
                    puntos_disparo = []
                    inputs = {"masa": "Kg", "angulo": "Grados", "potencia": "Joules"}
                    estado_juego = "jugando"
                    objetivo_x_m = random.uniform(35, 75)
                    objetivo_y_m = random.uniform(2, 10)
                    continue

            elif estado_juego == "jugando":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for key, box in input_boxes.items():
                        if box.collidepoint(event.pos):
                            active_input = key
                            break
                    else:
                        active_input = None

                    if boton.collidepoint(event.pos):
                        try:
                            masa = float(inputs["masa"])
                            angulo = float(inputs["angulo"])
                            potencia = float(inputs["potencia"])
                            puntos_disparo = disparar(masa, angulo, potencia)
                            disparo = True
                            resultado = ""
                        except:
                            resultado = "Entrada inválida"

                elif event.type == pygame.KEYDOWN and active_input:
                    if event.key == pygame.K_RETURN:
                        active_input = None
                    elif event.key == pygame.K_BACKSPACE:
                        inputs[active_input] = inputs[active_input][:-1]
                    else:
                        inputs[active_input] += event.unicode
                        
        # Animar disparo
        if disparo and puntos_disparo:
            punto = puntos_disparo.pop(0)
            radio_proyectil = 5  # Más pequeño para mayor precisión
            pygame.draw.circle(screen, BLACK, punto, radio_proyectil)
            # (Opcional) Dibuja el centro del proyectil
            # pygame.draw.circle(screen, (0, 255, 0), punto, 2)

            # Precisión mejorada: colisión círculo-rectángulo
            # Calcula el rectángulo del objetivo y la posición del proyectil
            objetivo_x = int(objetivo_x_m * ESCALA) + base_x
            objetivo_y = HEIGHT - int(objetivo_y_m * ESCALA) - (HEIGHT - base_y)
            objetivo_ancho = int(1 * ESCALA)
            objetivo_alto = int(4 * ESCALA)
            objetivo_rect = pygame.Rect(objetivo_x, objetivo_y, objetivo_ancho, objetivo_alto)
            px, py = punto

            # Encuentra el punto más cercano del rectángulo al centro del círculo
            closest_x = max(objetivo_rect.left, min(px, objetivo_rect.right))
            closest_y = max(objetivo_rect.top, min(py, objetivo_rect.bottom))
            dist_sq = (px - closest_x) ** 2 + (py - closest_y) ** 2

            if dist_sq <= radio_proyectil ** 2:
                resultado = "¡Le diste al objetivo!"
                disparo = False
                aciertos += 1
                puntos_disparo = []

                # Reposicionar el objetivo después de un acierto (en metros)
                objetivo_x_m = random.uniform(35, 70)
                objetivo_y_m = random.uniform(2, 30)

        elif disparo and not puntos_disparo:
            if resultado == "":
                resultado = "Fallaste el disparo"
                vidas -= 1
                disparo = False

        # Mostrar resultado
        if resultado:
            dibujar_texto(resultado, 100, 250)

        # Fin del juego
        if estado_juego == "jugando" and (aciertos >= 5 or vidas <= 0):
            estado_juego = "final"
            if aciertos >= 5:
                boton_reiniciar = pantalla_final("¡Ganaste!", True)
            else:
                boton_reiniciar = pantalla_final("¡Perdiste!", True)

            # Esperar a que el usuario pulse el botón de reinicio
            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and boton_reiniciar.collidepoint(event.pos):
                        # Reiniciar variables
                        vidas = 5
                        aciertos = 0
                        resultado = ""
                        puntos_disparo = []
                        inputs = {"masa": "Kg", "angulo": "Grados", "potencia": "Joules"}
                        estado_juego = "jugando"
                        objetivo_x_m = random.uniform(35, 70)
                        objetivo_y_m = random.uniform(3, 30)
                        esperando = False
                pygame.time.delay(10)
            continue

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
