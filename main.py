import random
import os
import pygame


if not os.path.exists("bs"):
    with open("bs", 'w') as bs_file:
        best_score = 0
        bs_file.write(str(best_score))
else:
    with open("bs", 'r') as bs_file:
        best_score = int(bs_file.read())

pygame.init()


def set_best_score(scr):
    with open("bs", 'w') as f:
        f.write(str(scr))


def generate_pipe_pos(last_pipe_pos: tuple,
                      pipes_dx: int,
                      pipe_dy: int,
                      y_range: tuple,
                      valid_y_range: tuple):
    px, py = last_pipe_pos
    valid_y_min, valid_y_max = valid_y_range
    dy_min, dy_max, step = y_range
    py_min, py_max = py+dy_min, py+dy_max
    if py_min < valid_y_min:
        py_min = valid_y_min
    if py_max > valid_y_max-pipe_dy:
        py_max = valid_y_max-pipe_dy
    new_py = random.randrange(py_min, py_max, step)
    return [px+pipes_dx, new_py]


def generate_numbers_surface(str_number: str, scale):
    digits_width = [digits_sprites[int(digit)].get_width()*scale for digit in str_number]
    digits_height = digits_sprites[0].get_height()*scale
    numbers_surface = pygame.Surface((sum(digits_width), digits_height), pygame.SRCALPHA)
    digit_x_sum = 0
    for i, digit in enumerate(str_number):
        digit_x = digits_width[i-1] if i > 0 else 0
        digit_x_sum += digit_x
        # numbers_surface.fill((222, 0, 0))
        resized_digit = pygame.transform.scale(digits_sprites[int(digit)], (digits_width[i], digits_height))
        numbers_surface.blit(resized_digit, (digit_x_sum, 0))
    return numbers_surface


def generate_lives_surface(lives_count):
    margin = 5
    lives_surface = pygame.Surface((heart_size*lives_count+margin*lives_count, heart_size), pygame.SRCALPHA)
    for i in range(lives_count):
        lives_surface.blit(live_sprite, (i*(heart_size+margin), 0))
    return lives_surface


fps = 60
screen = pygame.display.set_mode(vsync=True, flags=pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
win_size = win_width, win_height = screen.get_size()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
pygame.display.set_caption("FlappyBird")

bird_h = win_height//22.5
bird_w = round(bird_h*1.5)
bird_x, bird_y = 700, (win_height//2 - bird_h//2)
bird_v = 10
bird_angle = 0
free_fly_direction = 1

base_v = 5
base_height = win_height//6
base_width = round(base_height*13.5)
base_pos = [0, base_width, base_width*2]

pipe_width = win_width // 16
pipe_height = 6*pipe_width
distance_between_pipes = win_height // 3.5
pipes_x_difference = pipe_width + win_width // 7
pipes_y_range = -round(0.7*distance_between_pipes), round(0.7*distance_between_pipes), distance_between_pipes//10
valid_pipe_y = valid_pipe_y_min, valid_pipe_y_max = 60, win_height-base_height-60
pipes_pos = [[win_width+pipe_width, 200]]

heart_size = win_height//18
digit_scale = (base_height-30)/(36*2)

background_day_sprite = pygame.image.load("sprites\\background-day.png").convert()
background_day_sprite = pygame.transform.scale(background_day_sprite, (win_width, win_height))
background_night_sprite = pygame.image.load("sprites\\background-night.png").convert()
background_night_sprite = pygame.transform.scale(background_night_sprite, (win_width, win_height))
background_sprites = [background_day_sprite, background_night_sprite]
background_frame_count = 0
background_sprite = background_sprites[background_frame_count]

pipe_green_sprite_bottom = pygame.image.load("sprites/pipe_green.png").convert_alpha()
pipe_green_sprite_bottom = pygame.transform.scale(pipe_green_sprite_bottom, (pipe_width, pipe_height))
pipe_green_sprite_top = pygame.transform.rotate(pipe_green_sprite_bottom, 180)
pipe_red_sprite_bottom = pygame.image.load("sprites/pipe_red.png").convert_alpha()
pipe_red_sprite_bottom = pygame.transform.scale(pipe_red_sprite_bottom, (pipe_width, pipe_height))
pipe_red_sprite_top = pygame.transform.rotate(pipe_red_sprite_bottom, 180)
pipe_sprites = [[pipe_green_sprite_top, pipe_green_sprite_bottom], [pipe_red_sprite_top, pipe_red_sprite_bottom]]
pipe_sprite = pipe_sprites[background_frame_count]

base_sprite = pygame.image.load("sprites\\base.png").convert()
base_sprite = pygame.transform.scale(base_sprite, (base_width, base_height))
live_sprite = pygame.image.load("sprites\\heart.png").convert_alpha()
live_sprite = pygame.transform.scale(live_sprite, (heart_size, heart_size))

bird_yellow_flap_anim = [pygame.image.load("sprites\\yellow_bird\\downflap.png").convert_alpha(),
                         pygame.image.load("sprites\\yellow_bird\\midflap.png").convert_alpha(),
                         pygame.image.load("sprites\\yellow_bird\\upflap.png").convert_alpha()]
bird_yellow_flap_anim = [pygame.transform.scale(frame, (bird_w, bird_h)) for frame in bird_yellow_flap_anim]
current_bird_yellow_frame = bird_yellow_flap_anim[0]
bird_blue_flap_anim = [pygame.image.load("sprites\\blue_bird\\downflap.png").convert_alpha(),
                       pygame.image.load("sprites\\blue_bird\\midflap.png").convert_alpha(),
                       pygame.image.load("sprites\\blue_bird\\upflap.png").convert_alpha()]
bird_blue_flap_anim = [pygame.transform.scale(frame, (bird_w, bird_h)) for frame in bird_blue_flap_anim]
current_bird_blue_frame = bird_blue_flap_anim[0]
bird_anim_sprites = [bird_yellow_flap_anim, bird_blue_flap_anim]
bird_flap_anim = bird_anim_sprites[background_frame_count]

digits_sprites = [pygame.image.load(f"sprites\\numbers\\{i}.png").convert_alpha() for i in range(10)]
digits_sprites = [pygame.transform.scale(i, (i.get_width()*digit_scale, i.get_height()*digit_scale)) for i in digits_sprites]

sound_wing = pygame.mixer.Sound("audio\\wing.wav")
sound_wing.set_volume(0.2)
sound_hit = pygame.mixer.Sound("audio\\hit.wav")
sound_hit.set_volume(0.2)
sound_point = pygame.mixer.Sound("audio\\point.wav")
sound_point.set_volume(0.2)

fall_ticks = 0
flap_ticks = 0
fall_angle = 0
score = 0
score_value = 1
lives = 3
is_flap = False
is_play = False
is_dead = False
is_run = True
while is_run:
    clock.tick(fps)
    current_tick = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                is_run = False

            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                if not is_play:
                    is_play = True
                    is_dead = False
                sound_wing.play()
                is_flap = True
                fall_ticks = 0
                flap_ticks = 0

    screen.blit(background_sprite, (0, 0))

    if is_dead:
        if lives > 0:
            is_play = True
        else:
            score = 0
            background_frame_count = 0
            lives = 3
            set_best_score(best_score)
            is_play = False
        bird_y = (win_height//2 - bird_h//2)
        bird_angle = 0
        free_fly_direction = -1
        background_sprite = background_sprites[background_frame_count % 2]
        pipe_sprite = pipe_sprites[background_frame_count % 2]
        bird_flap_anim = bird_anim_sprites[background_frame_count % 2]
        pipes_pos = [[win_width + pipe_width, 200]]
        is_dead = False

    if is_play:
        if score > best_score:
            best_score = score

        if is_flap and flap_ticks <= 30:
            bird_y -= 3*bird_v/(flap_ticks+1)
            flap_ticks += 1
            bird_angle = 30
            current_bird_frame = bird_flap_anim[0]
        else:
            current_bird_frame = bird_flap_anim[2]
        bird_y += bird_v*fall_ticks/50
        fall_ticks += 1

        bird_angle -= 1
        if bird_angle <= -90:
            bird_angle = -90

        for pipe_pos_i, pipe_pos in enumerate(pipes_pos):
            pipe_x, bottom_of_top_pipe = pipe_pos
            pipes_pos[pipe_pos_i][0] -= base_v
            if pipe_x <= -6*pipe_width:
                pipes_pos.pop(pipe_pos_i)
            if pipes_pos[-1][0] <= win_width+100:
                pipes_pos.append(
                    generate_pipe_pos(last_pipe_pos=pipe_pos,
                                      pipes_dx=pipes_x_difference,
                                      pipe_dy=distance_between_pipes,
                                      y_range=pipes_y_range,
                                      valid_y_range=valid_pipe_y)
                )
            screen.blit(pipe_sprite[0], [pipe_x, -(pipe_height - bottom_of_top_pipe)])
            screen.blit(pipe_sprite[1], [pipe_x, bottom_of_top_pipe + distance_between_pipes])

    else:
        current_bird_frame = bird_flap_anim[current_tick//fps % 3]
        if int(bird_y) == win_height // 2 - bird_h//2 - 10:
            free_fly_direction = -1
        elif int(bird_y) == win_height // 2 - bird_h//2 + 10:
            free_fly_direction = 1
        bird_y -= free_fly_direction

    current_bird_frame = pygame.transform.rotate(current_bird_frame, bird_angle)
    bird_w, bird_h = current_bird_frame.get_size()

    if bird_y+bird_w >= win_height-base_height:
        sound_hit.play()
        lives -= 1
        is_dead = True

    for bs_x_i, bs_x in enumerate(base_pos):
        if bs_x <= -2*base_width:
            base_pos.pop(bs_x_i)
            base_pos.append(max(base_pos)+base_width)
            # print(backgrounds_pos)
        base_pos[bs_x_i] -= base_v
        screen.blit(base_sprite, (bs_x, win_height-win_height//6))

    for pipe_x, bottom_of_top_pipe in pipes_pos:
        if pipe_x+pipe_width+bird_w >= bird_x+bird_w >= pipe_x:
            # pygame.draw.rect(screen, (0, 0, 0), ((bird_x, bird_y), (bird_w, bird_h)))
            if bird_y <= bottom_of_top_pipe or bird_y+bird_h >= bottom_of_top_pipe+distance_between_pipes:
                sound_hit.play()
                lives -= 1
                is_dead = True

        if (pipe_x+pipe_width) - ((pipe_x+pipe_width) % base_v) == 700:
            score += score_value
            if score % 10 == 0:
                sound_point.play()
            if score % 50 == 0:
                background_frame_count += 1
            if score % 100 == 0:
                lives += 1

            score_value = 1 + (background_frame_count % 2)
            background_sprite = background_sprites[background_frame_count % 2]
            pipe_sprite = pipe_sprites[background_frame_count % 2]
            bird_flap_anim = bird_anim_sprites[background_frame_count % 2]

    # screen.blit(font.render(f"{lives=} \\ {best_score=} \\ {is_play=}", True, (0, 0, 0)), (0, 0))
    score_surface = generate_numbers_surface(str(score), 1)
    best_score_surface = generate_numbers_surface(str(best_score), 0.5)
    score_width, score_height = score_surface.get_size()
    best_score_width, best_score_height = best_score_surface.get_size()
    screen.blit(score_surface, (10, win_height - best_score_height - 10 - score_height - 10))
    screen.blit(best_score_surface, (10, win_height - best_score_height - 10))
    screen.blit(generate_lives_surface(lives), (10, 10))
    screen.blit(current_bird_frame, (bird_x, bird_y))
    pygame.display.update()

# print([i[0]+pipe_width for i in pipes_pos])
