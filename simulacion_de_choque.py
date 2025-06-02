import pygame
import sys
import math
from particles import Particle

pygame.init()

# Configuración de pantalla
width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulador Partícula-Resorte")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)
RED = (255, 100, 100)

# Parámetros iniciales del resorte y partícula
def reset_particle():
    return Particle(x=100, y=300, vx=slider_values['vx'] * PIXELS_PER_METER, vy=0, radius=15, mass=slider_values['mass'])

k = 50.0  # N/m
x0 = 700  # Posición del anclaje del resorte (en px)
spring_rest_length = 0  # Longitud de reposo del resorte (en px)
dt = 0.02  # Tiempo por frame en segundos
mass = 1.0  # kg
vx_initial = 5.0  # m/s

# Escalas para convertir unidades reales a pixeles
PIXELS_PER_METER = 100

# Crear partícula
slider_values = {
    'k': k,
    'mass': mass,
    'vx': vx_initial
}
particle = reset_particle()

# Fuente
font = pygame.font.SysFont(None, 24)

def draw_spring(surface, start_x, end_x, y, coils=8, amplitude=20):
    """Dibuja una animación de resorte entre dos puntos"""
    if end_x <= start_x:
        return
    step = (end_x - start_x) / coils
    points = []
    for i in range(coils + 1):
        x = start_x + i * step
        offset = amplitude if i % 2 == 0 else -amplitude
        points.append((x, y + offset))
    pygame.draw.lines(surface, YELLOW, False, points, 2)

def draw_slider(surface, x, y, value, min_val, max_val, label):
    pygame.draw.line(surface, WHITE, (x, y), (x + 200, y), 3)
    handle_x = x + int((value - min_val) / (max_val - min_val) * 200)
    pygame.draw.circle(surface, WHITE, (handle_x, y), 8)
    txt = font.render(f"{label}: {value:.2f}", True, WHITE)
    surface.blit(txt, (x, y - 25))
    return handle_x

def handle_slider_event(mouse_x, mouse_y, slider_x, slider_y, min_val, max_val):
    if abs(mouse_y - slider_y) <= 10 and slider_x <= mouse_x <= slider_x + 200:
        return min_val + (mouse_x - slider_x) / 200 * (max_val - min_val)
    return None

def draw_button(surface, rect, text):
    pygame.draw.rect(surface, BLUE, rect)
    label = font.render(text, True, WHITE)
    surface.blit(label, (rect.x + 10, rect.y + 5))

def draw_force_label(surface, force, x, y):
    txt = font.render(f"Fuerza recuperadora: {force:.2f} N", True, RED)
    surface.blit(txt, (x, y))

# Botón de reiniciar
reset_button = pygame.Rect(50, 250, 120, 30)

running = True
sliding = None
restoring_force = 0.0
while running:
    screen.fill((30, 30, 30))
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button.collidepoint(mouse_x, mouse_y):
                particle = reset_particle()
            for i, key in enumerate(slider_values):
                val = handle_slider_event(mouse_x, mouse_y, 50, 50 + i * 60, 0.1 if key != 'vx' else 0.0, 100.0)
                if val is not None:
                    sliding = key
                    slider_values[key] = val
        elif event.type == pygame.MOUSEBUTTONUP:
            sliding = None
        elif event.type == pygame.MOUSEMOTION and sliding:
            val = handle_slider_event(mouse_x, mouse_y, 50, 50 + list(slider_values.keys()).index(sliding) * 60,
                                      0.1 if sliding != 'vx' else 0.0, 100.0)
            if val is not None:
                slider_values[sliding] = val

    # Aplicar valores actualizados
    k = slider_values['k']
    particle.mass = slider_values['mass']

    # Movimiento normal
    particle.move(dt)

    # Colisión con el resorte sin fricción, rebote ideal
    restoring_force = 0.0
    if particle.x + particle.radius >= x0:
        penetration = (particle.x + particle.radius) - x0
        restoring_force = -k * (penetration / PIXELS_PER_METER)
        acceleration = restoring_force / particle.mass
        particle.vx += acceleration * dt * PIXELS_PER_METER

    # Dibujar sliders
    for i, (key, value) in enumerate(slider_values.items()):
        draw_slider(screen, 50, 50 + i * 60, value, 0.1 if key != 'vx' else 0.0, 100.0, key + (" (SI)"))

    # Dibujar botón de reinicio
    draw_button(screen, reset_button, "Reiniciar")

    # Dibujar el resorte deformado
    draw_spring(screen, x0, particle.x + particle.radius, particle.y)

    # Mostrar fuerza recuperadora
    draw_force_label(screen, restoring_force, 50, 300)

    # Dibujar la partícula
    particle.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
