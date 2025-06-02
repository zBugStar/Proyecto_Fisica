import pygame
import random
import math
from particles import Particle

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Partículas 2D")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --------- Simulación Principal ---------
def main_simulation():
    NUM_PARTICLES = 10
    MAX_SPEED = 300
    particles = []
    while len(particles) < NUM_PARTICLES:
        radius = random.randint(10, 20)
        mass = radius ** 2
        x = random.randint(radius, WIDTH - radius)
        y = random.randint(radius, HEIGHT - radius)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        new_particle = Particle(x, y, vx, vy, radius, mass)
        overlap = False
        for p in particles:
            dx = p.x - new_particle.x
            dy = p.y - new_particle.y
            distance = math.hypot(dx, dy)
            if distance < p.radius + new_particle.radius:
                overlap = True
                break
        if not overlap:
            particles.append(new_particle)

    def resolve_collision(p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dist = math.hypot(dx, dy)
        min_dist = p1.radius + p2.radius
        if dist < min_dist and dist != 0:
            nx = dx / dist
            ny = dy / dist
            overlap = 0.5 * (min_dist - dist + 1)
            p1.x -= nx * overlap
            p1.y -= ny * overlap
            p2.x += nx * overlap
            p2.y += ny * overlap
            tx = -ny
            ty = nx
            v1n = p1.vx * nx + p1.vy * ny
            v1t = p1.vx * tx + p1.vy * ty
            v2n = p2.vx * nx + p2.vy * ny
            v2t = p2.vx * tx + p2.vy * ty
            v1n_post = (v1n * (p1.mass - p2.mass) + 2 * p2.mass * v2n) / (p1.mass + p2.mass)
            v2n_post = (v2n * (p2.mass - p1.mass) + 2 * p1.mass * v1n) / (p1.mass + p2.mass)
            p1.vx = v1n_post * nx + v1t * tx
            p1.vy = v1n_post * ny + v1t * ty
            p2.vx = v2n_post * nx + v2t * tx
            p2.vy = v2n_post * ny + v2t * ty

    def total_kinetic_energy(particles):
        return sum(0.5 * p.mass * (p.vx**2 + p.vy**2) for p in particles)

    button_rect = pygame.Rect(WIDTH - 210, 10, 200, 40)
    running = True
    substeps = 3

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    run_spring_simulation()

        for _ in range(substeps):
            step_dt = dt / substeps
            for p in particles:
                p.move(step_dt)
                p.wall_collision(WIDTH, HEIGHT)
                speed = math.hypot(p.vx, p.vy)
                if speed > MAX_SPEED:
                    scale = MAX_SPEED / speed
                    p.vx *= scale
                    p.vy *= scale
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    resolve_collision(particles[i], particles[j])

        screen.fill((0, 0, 0))
        for p in particles:
            p.draw(screen)
        ke = total_kinetic_energy(particles)
        text = font.render(f"Energía Cinética: {ke:.2f}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        pygame.draw.rect(screen, (50, 150, 250), button_rect)
        button_text = font.render("Simulación con resortes", True, (255, 255, 255))
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))
        pygame.display.flip()

# --------- Simulación con Resortes ---------
def run_spring_simulation():
    class Slider:
        def __init__(self, x, y, w, min_val, max_val, value, label, unit):
            self.rect = pygame.Rect(x, y, w, 20)
            self.min_val = min_val
            self.max_val = max_val
            self.value = value
            self.dragging = False
            self.label = label
            self.unit = unit

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                mx = event.pos[0]
                rel_x = max(self.rect.left, min(mx, self.rect.right))
                self.value = self.min_val + (rel_x - self.rect.left) / self.rect.width * (self.max_val - self.min_val)

        def draw(self, surface):
            pygame.draw.rect(surface, (180, 180, 180), self.rect)
            slider_x = self.rect.left + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width
            pygame.draw.circle(surface, (100, 200, 255), (int(slider_x), self.rect.centery), 8)
            label_surface = font.render(f"{self.label}: {self.value:.1f} {self.unit}", True, (255, 255, 255))
            surface.blit(label_surface, (self.rect.left, self.rect.top - 20))

    fixed_point = [WIDTH // 2, 100]  # Fijo arriba
    particle = Particle(fixed_point[0], fixed_point[1] + 150, 0, 0, 15, 20)
    rest_length = 150
    g = 9.81 * 100  # gravedad "escalada" visualmente (pixeles ≈ cm)
    
    # Sliders con unidades SI
    k_slider = Slider(20, HEIGHT - 80, 200, 10, 500, 100, "Constante k", "N/m")
    mass_slider = Slider(20, HEIGHT - 40, 200, 1, 100, particle.mass, "Masa", "kg")

    oscillation_count = 0
    previous_above = None
    equilibrium_y = fixed_point[1] + rest_length
    trail = []
    max_trail_length = 100

    # Botones
    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 60)
    pause_button_rect = pygame.Rect(WIDTH // 2 + 250, HEIGHT - 60, 120, 40)
    reset_button_rect = pygame.Rect(WIDTH // 2 + 100, HEIGHT - 60, 120, 40)
    simulation_started = False
    paused = False

    running = True
    last_cross = None  # Para evitar dobles conteos

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            k_slider.handle_event(event)
            mass_slider.handle_event(event)
            if not simulation_started:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button_rect.collidepoint(event.pos):
                        simulation_started = True
                        paused = False
                        oscillation_count = 0
                        previous_above = None
                        last_cross = None
                        particle.mass = mass_slider.value
                        particle.vy = 0
                        particle.y = fixed_point[1] + rest_length
                        trail.clear()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pause_button_rect.collidepoint(event.pos):
                        paused = not paused
                    if reset_button_rect.collidepoint(event.pos):
                        oscillation_count = 0
                        previous_above = None
                        last_cross = None
                        particle.mass = mass_slider.value
                        particle.vy = 0
                        particle.y = fixed_point[1] + rest_length
                        trail.clear()
                        paused = False

        screen.fill((0, 0, 0))

        if not simulation_started:
            # Dibuja la partícula en reposo (posición de equilibrio)
            particle.mass = mass_slider.value
            k = k_slider.value
            particle.y = fixed_point[1] + rest_length
            particle.vy = 0

            pygame.draw.line(screen, (255, 255, 255), fixed_point, (particle.x, particle.y), 2)
            pygame.draw.circle(screen, (255, 0, 0), fixed_point, 10)
            particle.draw(screen)
            k_slider.draw(screen)
            mass_slider.draw(screen)
            pygame.draw.rect(screen, (50, 200, 50), start_button_rect)
            text = font.render("Iniciar simulación", True, (255, 255, 255))
            screen.blit(text, (start_button_rect.x + 25, start_button_rect.y + 18))
            screen.blit(font.render("Ajusta los valores y presiona el botón", True, (255, 255, 255)), (10, 10))
            pygame.display.flip()
            continue

        # --- Simulación física ---
        if not paused:
            particle.mass = mass_slider.value
            k = k_slider.value

            dy = particle.y - fixed_point[1]
            dist = dy
            force = -k * (dist - rest_length)  # Fuerza de resorte (Hooke)
            force += particle.mass * g         # Gravedad
            ay = force / particle.mass
            particle.vy += ay * dt
            particle.y += particle.vy * dt

            # Conteo de oscilaciones: cuenta cada cruce por el equilibrio (ambos sentidos)
            is_above = particle.y < equilibrium_y
            if previous_above is not None and is_above != previous_above:
                # Solo cuenta si no es el mismo cruce que el anterior
                if last_cross != is_above:
                    oscillation_count += 1
                    last_cross = is_above
            previous_above = is_above

            # Rebote si toca el fondo
            if particle.y + particle.radius > HEIGHT:
                particle.y = HEIGHT - particle.radius
                particle.vy *= -0.8

            # Guardar trayectoria
            trail.append((int(particle.x), int(particle.y)))
            if len(trail) > max_trail_length:
                trail.pop(0)

        # Dibujar resorte y partícula
        pygame.draw.line(screen, (255, 255, 255), fixed_point, (particle.x, particle.y), 2)
        pygame.draw.circle(screen, (255, 0, 0), fixed_point, 10)
        if len(trail) > 1:
            pygame.draw.lines(screen, (0, 255, 255), False, trail, 2)
        particle.draw(screen)
        k_slider.draw(screen)
        mass_slider.draw(screen)

        # Botones de pausa y reinicio
        pygame.draw.rect(screen, (200, 200, 50), pause_button_rect)
        pause_text = font.render("Pausar" if not paused else "Reanudar", True, (0, 0, 0))
        screen.blit(pause_text, (pause_button_rect.x + 10, pause_button_rect.y + 10))

        pygame.draw.rect(screen, (200, 50, 50), reset_button_rect)
        reset_text = font.render("Reiniciar", True, (255, 255, 255))
        screen.blit(reset_text, (reset_button_rect.x + 15, reset_button_rect.y + 10))

        screen.blit(font.render("ESC para volver", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Oscilaciones: {oscillation_count}", True, (255, 255, 255)), (10, 70))
        pygame.display.flip()
    


# --------- Iniciar ---------
main_simulation()
pygame.quit()
