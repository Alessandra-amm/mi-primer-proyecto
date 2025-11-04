import random, time

WIDTH = 600
HEIGHT = 300
TITLE = "Corredor de Alienígenas"
FPS = 30

# Objetos
alien = Actor("stand", (100, 240))
background1 = Actor("background15", (WIDTH // 2, HEIGHT // 2))
background2 = Actor("background15", (WIDTH + WIDTH // 2, HEIGHT // 2))
box = Actor("box", (550, 265))
ghost = Actor("ghost", (550, 115))
go = Actor("go")

# Variables generales
new_image = "stand"
game_over = 0
count = 0
enemy = random.randint(1, 2)
speed = 2
scroll_speed = 0

# Animación
walk_timer = 0
walk_index = 0
walk_frames = ["stand", "right"]

# Disparos y bonus
bullets = []
bonuses = []
shoot_delay = 0.3
last_shot = 0
bonus_effect = None
bonus_timer = 0


def boxes():
    global count, enemy, speed
    if box.x > -20:
        box.x -= speed
        box.angle += 5
    else:
        box.x = WIDTH + 20
        count += 1
        enemy = random.randint(1, 2)
        speed += 1


def ghosts():
    global count, enemy, speed, ghost
    if ghost.x > -20:
        ghost.x -= speed
    else:
        ghost.x = WIDTH + 20
        count += 1
        enemy = random.randint(1, 2)
        speed += 1
        ghost.y = random.randint(80, 100)


def draw():
    background1.draw()
    background2.draw()

    alien.draw()

    if enemy == 1:
        box.draw()
    else:
        ghost.draw()

    # Dibujar disparos
    for b in bullets:
        b.draw()

    # Dibujar bonificaciones
    for bon in bonuses:
        bon.draw()

    screen.draw.text(str(count), pos=(10, 10), color="white", fontsize=30)

    if game_over == 1:
        go.draw()
        screen.draw.text("Press Enter", pos=(230, 180), color="white", fontsize=36)


def update(dt):
    global new_image, count, game_over, speed, scroll_speed
    global walk_timer, walk_index, bonus_timer, bonus_effect

    # Mover enemigos
    if enemy == 1:
        boxes()
    else:
        ghosts()

    # Movimiento lateral (scroll)
    if (keyboard.left or keyboard.a) and game_over == 0:
        scroll_speed = 3
        walk_timer += 1
        if walk_timer % 10 == 0:
            walk_index = (walk_index + 1) % len(walk_frames)
            alien.image = walk_frames[walk_index]

    elif (keyboard.right or keyboard.d) and game_over == 0:
        scroll_speed = -3
        walk_timer += 1
        if walk_timer % 10 == 0:
            walk_index = (walk_index + 1) % len(walk_frames)
            alien.image = walk_frames[walk_index]

    else:
        scroll_speed = 0
        alien.image = "stand"
        walk_timer = 0
        walk_index = 0

    if keyboard.down or keyboard.s:
        alien.image = "duck"
        new_image = "duck"
        alien.y = 250
    elif alien.y >= 240:
        alien.y = 240

    # Scroll infinito del fondo
    background1.x += scroll_speed
    background2.x += scroll_speed

    if background1.right < 0:
        background1.left = background2.right
    if background2.right < 0:
        background2.left = background1.right
    if background1.left > WIDTH:
        background1.right = background2.left
    if background2.left > WIDTH:
        background2.right = background1.left

    # Actualizar disparos
    for b in list(bullets):
        b.x += 10
        if b.x > WIDTH:
            bullets.remove(b)
        else:
            # Colisiones
            if enemy == 1 and b.colliderect(box):
                bullets.remove(b)
                spawn_bonus(box.pos)
                reset_enemy(box)
            elif enemy == 2 and b.colliderect(ghost):
                bullets.remove(b)
                spawn_bonus(ghost.pos)
                reset_enemy(ghost)

    # Actualizar bonificaciones
    for bon in list(bonuses):
        bon.y += 1
        if bon.y > HEIGHT:
            bonuses.remove(bon)
        elif bon.colliderect(alien):
            apply_bonus(bon)
            bonuses.remove(bon)

    # Temporizador del bonus activo
    if bonus_effect and time.time() > bonus_timer:
        bonus_effect = None

    # Reiniciar
    if game_over == 1 and keyboard.RETURN:
        reset_game()

    # Colisión jugador-enemigo
    if alien.colliderect(box) or alien.colliderect(ghost):
        game_over = 1


def reset_enemy(obj):
    """Resetea posición de enemigo y aumenta puntuación"""
    global count, enemy, speed
    obj.x = WIDTH + 20
    count += 1
    speed += 0.5
    enemy = random.randint(1, 2)


def spawn_bonus(pos):
    """Pequeña probabilidad de soltar una bonificación"""
    if random.random() < 0.3:  # 30% de probabilidad
        bon = Actor(random.choice(["bonus_speed", "bonus_live", "bonus_points"]), pos)
        bonuses.append(bon)


def apply_bonus(bon):
    """Aplica el efecto de la bonificación"""
    global bonus_effect, bonus_timer, count, shoot_delay
    if bon.image == "bonus_points":
        count += 10
    elif bon.image == "bonus_speed":
        bonus_effect = "speed"
        bonus_timer = time.time() + 5
    elif bon.image == "bonus_fire":
        bonus_effect = "rapid_fire"
        shoot_delay = 0.15
        bonus_timer = time.time() + 5


def reset_game():
    global game_over, count, speed, bullets, bonuses, shoot_delay
    game_over = 0
    count = 0
    speed = 2
    bullets.clear()
    bonuses.clear()
    shoot_delay = 0.3
    alien.pos = (100, 240)
    box.pos = (550, 265)
    ghost.pos = (550, 105)
    background1.pos = (WIDTH // 2, HEIGHT // 2)
    background2.pos = (WIDTH + WIDTH // 2, HEIGHT // 2)


def shoot_bullet():
    bullet = Actor("bullet", (alien.x + 40, alien.y))
    bullets.append(bullet)


def on_key_down(key):
    if key == keys.SPACE:
        shoot_bullet()
    elif key == keys.UP or key == keys.W:
        alien.y = 50
        animate(alien, tween="bounce_end", duration=2, y=240)
