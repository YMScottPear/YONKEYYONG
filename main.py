# Donkey kong project
# Scott Steph Amber
# Using pygame to recreate (resurrect Donkey Kong)
import pygame

from Objects import *
from random import randint

#pygame.init()

# ------------------------------
# Important Variables:

# Our window variable, everything drawn to this variable
window = pygame.display.set_mode((512, 448))
pygame.display.set_caption("YONKEY YONG")
# Window icon ***CHANGE LATER***
window_icon = pygame.image.load('Sprites/images.jpg')
pygame.display.set_icon(window_icon)

# Boolean variable, True if our program is still running, false if we end the program
Pro_Running = True

# Framerate of our program
# Arcade is 60fps
frame_rate = 20
# Clock is used to cap framerate
Clock = pygame.time.Clock()

# Primary font to use
prim_font_large = pygame.font.Font('Sprites/Font/Daydream.ttf', 30)
prim_font_small = pygame.font.Font('Sprites/Font/Daydream.ttf', 10)
# Secondary font
sec_font_medium = pygame.font.Font('Sprites/Font/8-bit Arcade In.ttf', 50)
sec_font_small = pygame.font.Font('Sprites/Font/8-bit Arcade In.ttf', 20)

# Refers to the state of the game
game_state = 'intro'
# intro: when the program is first run
# lvl: loads the correct level

# 0 if no level loaded
# 1 if a level is loaded
level_loaded = 0

# Intro Variables
intro_selection = 0

Curr_Level = 1

current_goal = Goal(-100, -100)

#
# Score variables
current_score = 0
current_score_str = f"{current_score:08d}"
highscore = 0
highscore_str = f"{highscore:08d}"

death_se = pygame.mixer.Sound('Sounds/Death.mp3')

bg_music = pygame.mixer.music.load('Sounds/HauntedHouseBG.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Lives
lives = 3

# -----------------------------
# Player attributes

player_char = Player()
P_GS = pygame.sprite.GroupSingle()
P_GS.add(player_char)


def jump_over_pumpkin(player_group, pumpkin):
    global current_score
    p = player_group.sprite
    if p.jump_over(pumpkin):
        current_score += 100


# ------------------------------
# Program Functions:

# All events must be checked in this function!
def check_events():
    global Pro_Running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Pro_Running = False

        if event.type == Yonkey_Action:
            Yonkey_action_event(YonkeyYong)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
            #print(event.pos)

# -----------------------------
# Score I/O


def get_high_score():
    file = open('ScoreData.txt', 'rt')
    score = file.read()
    file.close()
    score = int(score)
    return score


def write_new_highscore():
    global highscore
    file = open('ScoreData.txt', 'wt')
    file.write(f"{highscore:08d}")
    file.close()

# -----------------------------
def game_state_to_load():
    global Curr_Level, current_score
    global Pro_Running, loaded_lvl
    if game_state == 'intro':
        intro_actions()
        Curr_Level = 1
        current_score = 0
    elif game_state == 'level_intro':
        level_intro()
    elif game_state == 'level1':
        if level_loaded == 0:
            init_lvl1()
        else:
            level1_actions()
    elif game_state == 'dead':
        death_seq()
    elif game_state == 'game_over':
        game_over_seq()
    elif game_state == 'win':
        game_win_seq()
    elif game_state == 'quit':
        Pro_Running = False


def intro_actions():
    global game_state, lives
    tempstate = intro_objs[0].input(intro_arrow)
    if tempstate == '':
        tempstate = game_state
    game_state = tempstate
    if game_state == "level_intro":
        lives = 3
    intro_state_draw()


def init_lvl1():
    global loaded_lvl, level_loaded, lvl_objs, scaf_objs, current_goal
    loaded_lvl = 1
    level_loaded = 1

    lvl_objs, scaf_objs = load_lvl1()
    set_scaffold_to_level()

    P_GS.sprite.rect.midbottom = (20, 420)
    P_GS.sprite.gravity = 0
    P_GS.sprite.in_air = False
    P_GS.sprite.__init__()

    YonkeyYong.sprite.rect.midbottom = (80, 105)
    YonkeyYong.sprite.reset_pos()

    current_goal = Goal(235, 40)
    #current_goal = Goal(60, 400)
    lvl_objs.append(Ghosty(215, 50))


def level1_actions():
    global highscore, current_score
    window.fill('black')

    draw_map()

    # Draw Yonkey (temp)
    YonkeyYong.update()
    YonkeyYong.draw(window)

    # Enemy triggers
    throw_right()
    throw_down()

    # Draw enemies (temp)
    for item in rolling_pumpkins:
        item.update()
        pumpkin_ladder(item)
        pump_scaf_collision(item, scaf_objs)
        enem_pump_player_collision(item, P_GS)
        jump_over_pumpkin(P_GS, item)
        window.blit(item.surf, item.rect)

    for item in fall_pumpkins:
        item.update()
        window.blit(item.surf, item.rect)
        fall_pump_collision(item, P_GS)

    pumpkin_despawn()

    player_ladder_collision(P_GS, ladder_objs)

    P_GS.update()
    player_scaf_collision(P_GS, scaf_objs)
    P_GS.draw(window)

    #current_goal.draw(window)

    goal_check(P_GS)
    game_win_seq()

    death_seq()

    highscore = update_highscore(current_score, highscore)



def update_highscore(score_count, high_score):
    # Import highscore from previous game
    if score_count >= high_score:
        return score_count
    else:
        return high_score


def goal_check(player: pygame.sprite.GroupSingle):
    global game_win_trigger
    p = player.sprite
    if p.rect.colliderect(current_goal.rect):
        game_win_trigger = 1


# -----------------------------
# game win seq
game_win_trigger = 0
game_win_timer = 0


def game_win_seq():
    # REMOVE PUMPKINS
    global game_state, game_win_trigger, game_win_timer, Curr_Level, lvl_objs, current_score, highscore
    global rolling_pumpkins, fall_pumpkins
    if game_win_trigger == 1:
        game_state = 'win'
        if game_win_timer == 0:
            YonkeyYong.sprite.rect.x = YonkeyYong.sprite.x
            YonkeyYong.sprite.rect.y = YonkeyYong.sprite.y
        game_win_timer += 1
        highscore = update_highscore(current_score, highscore)

        yonkey_anim_x = [1, 1, 1, 2, 3, 5, 8, 8, 10, 15, 14, 13, 13, 8, 8, 5, 5, 3, 3, 2,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        yonkey_anim_y = [0, 2, 4, -4, -6, -9, -16, -16, -13, -10, -8, -7, -6, -3, 2, 4, 10, 20, 14, 0,
                         0, 0, 0, 0, 0, 0, -2, -4, -5, -6, -7, -8, -8, -12, -12, -12, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ghosty_anim_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ghosty_anim_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, -2, -4, -5, -6, -7, -8, -8, -12, -12, -12, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        window.fill('black')
        draw_map()
        YonkeyYong.sprite.image = YonkeyYong.sprite.yonk_surf
        YonkeyYong.draw(window)

        YonkeyYong.sprite.rect.x += yonkey_anim_x[game_win_timer]
        YonkeyYong.sprite.rect.y += yonkey_anim_y[game_win_timer]

        lvl_objs[-1].rect.x += ghosty_anim_x[game_win_timer]
        lvl_objs[-1].rect.y += ghosty_anim_y[game_win_timer]
        lvl_objs[-1].draw(window)

        P_GS.draw(window)

        if game_win_timer > 48:
            game_state = 'level_intro'
            Curr_Level += 1
            game_win_trigger = 0
            game_win_timer = 0
            unload_lvl()
            dead_objs.clear()
            rolling_pumpkins.clear()
            fall_pumpkins.clear()
            current_score += 5000
            highscore = update_highscore(current_score, highscore)


# -----------------------------
# Death Sequence
death_trigger = 0
death_anim_timer = 0

dead_objs = []


def death_seq():
    global death_trigger, death_anim_timer, dead_objs, game_state, rolling_pumpkins, fall_pumpkins, lives
    p = P_GS.sprite
    if death_trigger == 1:
        lives -= 1
        dead_objs.append(DeadSkele(p.rect.x, p.rect.y))
        game_state = "dead"
        death_se.play()
        death_trigger = 2
        rolling_pumpkins.clear()
        fall_pumpkins.clear()
    elif death_trigger == 2:
        p.is_dead = True

        window.fill('black')
        draw_map()

        P_GS.update()
        P_GS.draw(window)

        YonkeyYong.draw(window)

        death_anim_timer += 0.05

        if int(death_anim_timer + 0.05) > int(death_anim_timer):
            dead_objs[0].next_frame()

        dead_objs[0].draw(window)

        if death_anim_timer > 5:
            death_trigger = 0
            death_anim_timer = 0
            p.is_dead = False
            unload_lvl()
            dead_objs.clear()
            if lives > 0:
                game_state = "level_intro"
            else:
                game_state = "game_over"


game_over_timer = 0
game_over_text = prim_font_large.render("GAME OVER", False, (255, 255, 255))
score_txt_go = sec_font_medium.render(f"Score {current_score:08d}", False, (255, 255, 255))
new_high_score = prim_font_large.render("NEW HIGH SCORE", False, (128, 43, 43))


def game_over_seq():
    global game_over_timer, game_state, highscore, current_score

    game_over_timer += 0.05

    score_txt_go = sec_font_medium.render(f"Score {current_score:08d}", False, (255, 255, 255))

    window.fill('black')
    window.blit(game_over_text, (120, 100))
    window.blit(score_txt_go, (100, 160))
    if current_score >= highscore:
        window.blit(new_high_score, (85, 200))

    if game_over_timer > 5:
        # make actual intro
        game_state = 'intro'
        game_over_timer = 0
        if current_score >= highscore:
            highscore = current_score


# -----------------------------
# Intro sequence
intro_objs = []

# Background will be black
# Grey bar appears across background
intro_grey_bar = pygame.surface.Surface((512, 100))
intro_grey_bar.fill((50, 50, 50))
intro_gb_rect = intro_grey_bar.get_rect(midbottom=(256, 460))

# Title Text
intro_title = prim_font_large.render("Yonkey Yong", False, (168, 43, 43))

# Choice box
intro_choicebox_hor = pygame.surface.Surface((422, 10))
intro_choicebox_vert = pygame.surface.Surface((10, 150))
intro_choicebox_vert.fill((168, 43, 43))
intro_choicebox_hor.fill((168, 43, 43))

# Arrow
intro_arrow = IntroArrow(75, 250)

# Texts
start_game_txt = sec_font_medium.render("Start Game", False, (240, 240, 240))
# replace with somth idk
option2 = sec_font_medium.render("Option 2", False, (240, 240, 240))
intro_quit = sec_font_medium.render("Quit", False, (240, 240, 240))
hs_txt = sec_font_medium.render(f"Highscore {int(highscore):08d}", False, (240, 240, 240))


def intro_state_draw():
    window.fill('black')

    window.blit(intro_grey_bar, intro_gb_rect)
    intro_gb_rect.y -= 3
    if intro_gb_rect.y < -100:
        intro_gb_rect.y = 460

    hs_txt = sec_font_medium.render(f"Highscore {int(highscore):08d}", False, (240, 240, 240))

    window.blit(intro_title, (80, 100))

    window.blit(intro_choicebox_vert, (50, 200))
    window.blit(intro_choicebox_vert, (462, 200))
    window.blit(intro_choicebox_hor, (50, 200))
    window.blit(intro_choicebox_hor, (50, 350))
    window.blit(hs_txt, (50, 10))

    intro_arrow.draw(window)

    window.blit(start_game_txt, (160, 240))
    #window.blit(option2, (160, 290))
    window.blit(intro_quit, (160, 290))


# -----------------------------
# Level intros
level_intro_timer = 0

hs_text = prim_font_large.render(f"HighScore {highscore_str}", False, (168, 43, 43))
score_text = sec_font_medium.render(f"Score {current_score_str}", False, (255, 255, 255))
lvl_text = prim_font_large.render(f"Level {Curr_Level}", False, (255, 255, 255))
live_text = sec_font_medium.render(f"Lives {lives}", False, (255, 255, 255))

yonkey_taunt1 = pygame.image.load('Sprites/Yonkey/YonkeyDAB.png')
yonkey_taunt2 = pygame.image.load('Sprites/Yonkey/YonkeyDABrev.png')
yonkey_taunt_rect = yonkey_taunt1.get_rect(midbottom=(120, 220))
yonkey_taunt1 = pygame.transform.rotozoom(yonkey_taunt1, 0, 3.5)
yonkey_taunt2 = pygame.transform.rotozoom(yonkey_taunt2, 0, 3.5)
yonkey_taunts = [yonkey_taunt1, yonkey_taunt2]


def level_intro():
    global game_state, level_intro_timer, hs_text, score_text, lvl_text, live_text

    if level_intro_timer == 0:
        hs = f"{highscore:08d}"
        hs_text = sec_font_medium.render(f"HighScore {hs}", False, (168, 43, 43))
        st = f"{current_score:08d}"
        score_text = sec_font_medium.render(f"Score {st}", False, (255, 255, 255))
        lt = str(Curr_Level)
        lvl_text = sec_font_medium.render(f" level {lt}", False, (255, 255, 255))
        live_text = sec_font_medium.render(f"Lives {lives}", False, (255, 255, 255))

    window.fill('black')

    level_intro_timer += 0.05
    window.blit(hs_text, (60, 10))
    window.blit(score_text, (148, 40))
    window.blit(lvl_text, (314, 70))
    window.blit(live_text, (340, 100))

    yonk_index = int(level_intro_timer) % 2
    if yonk_index == 0:
        yonkey_taunt_rect.x -= 14
    if yonk_index == 1:
        yonkey_taunt_rect.x -= 70
    curr_surf_yonkey = yonkey_taunts[yonk_index]
    window.blit(curr_surf_yonkey, yonkey_taunt_rect)
    if yonk_index == 0:
        yonkey_taunt_rect.x += 14
    if yonk_index == 1:
        yonkey_taunt_rect.x += 70

    if level_intro_timer >= 5:
        game_state = 'level1'
        level_intro_timer = 0


# -----------------------------
# Enemies

# YonkeyObj is the variable holding the action YonkeyYong enemy object
# YonkeyYong is the GroupSingle variable
YonkeyObj = Yonkey(70, 96)
YonkeyYong = pygame.sprite.GroupSingle()
YonkeyYong.add(YonkeyObj)

# This is an event attached to a timer that triggers Yonkey to do one of his actions
Yonkey_Action = pygame.USEREVENT + 1
pygame.time.set_timer(Yonkey_Action, randint(4000, 5500))


# This function is triggered by a timer causing an event to occur
# This function will randomly pick an action for Yonkey to do
def Yonkey_action_event(YonkeyGP):
    global rolling_pumpkins
    global rolling_pumpkins
    global right_throw_trigger, down_throw_trigger

    # Y is just the actual YonkeyYong object, removed from the group
    Y = YonkeyGP.sprite

    trigger = 0
    if game_state == 'level1':
        trigger = randint(0, 11)
    if trigger < 5:
        if loaded_lvl == 1:
            Y.throw_pump_right()
            right_throw_trigger = 1
    # MAKE SURE THIS IS POSSIBLE FOR LEVEL 2 AS WELL
    elif 5 <= trigger <= 8:
        Y.throw_pump_down()
        down_throw_trigger = 1
    else:
        Y.taunt()


# These global variables are currently spawned and are in separate lists to check with collision with
# player and environment
rolling_pumpkins = []
fall_pumpkins = []

right_throw_timer = 0
right_throw_trigger = 0


def throw_right():
    global right_throw_timer, rolling_pumpkins, right_throw_trigger
    if right_throw_trigger:
        if right_throw_timer < 6:
            right_throw_timer += 0.1
        elif right_throw_timer >= 6:
            rolling_pumpkins.append(Enemy_Pumpkin(105, 55))
            right_throw_timer = 0
            right_throw_trigger = 0


down_throw_timer = 0
down_throw_trigger = 0


def throw_down():
    global YonkeyYong
    global down_throw_timer, down_throw_trigger, fall_pumpkins
    Y = YonkeyYong.sprite

    if down_throw_trigger:
        if down_throw_timer < 6:
            down_throw_timer += 0.1
        else:
            down_throw_timer = 0
            down_throw_trigger = 0
            fall_pumpkins.append(Fall_Pumpkin(Y.rect.x + 9, Y.rect.bottom + 5))


def pump_scaf_collision(pumpkin: Enemy_Pumpkin, scaffolds: list) -> None:
    above_scaf = 0

    for scaf in scaffolds:
        above_scaf += pumpkin.scaf_collision(scaf)
    if above_scaf == 0:
        pumpkin.in_air = True


def fall_pump_collision(pumpkin: Fall_Pumpkin, player: pygame.sprite.GroupSingle):
    global death_trigger
    p = player.sprite
    if pumpkin.rect.colliderect(p.rect):
        death_trigger = 1


def enem_pump_player_collision(pumpkin: Enemy_Pumpkin, player: pygame.sprite.GroupSingle):
    global death_trigger
    p = player.sprite
    if pumpkin.rect.colliderect(p.rect):
        death_trigger = 1


def pumpkin_despawn():
    global fall_pumpkins, rolling_pumpkins

    for pumpkin in fall_pumpkins:
        if pumpkin.rect.y >= 500:
            fall_pumpkins.pop(fall_pumpkins.index(pumpkin))
    for pumpkin in rolling_pumpkins:
        if pumpkin.rect.y >= 500:
            rolling_pumpkins.pop(rolling_pumpkins.index(pumpkin))


# -----------------------------
# Maps

# Global variables, these are the objects currently loaded in the ma[
# scaf_objs is seperate to check with player collision
# *************** THIS HAS BEEN CHANGES REMEBER
loaded_lvl = 0
lvl_objs = []
scaf_objs = []
ladder_objs = []

# Level one, add tuples of the top_left corners of the scaffold blocks to add
lvl1_scaffolds = [(0, 100), (48, 100), (96, 100), (144, 100), (192, 100), (240, 100), (288, 100), (336, 100),
                  (384, 100), (512, 153), (560, 153), (416, 157), (464, 157), (320, 159), (368, 159), (224, 161),
                  (272, 161), (128, 163), (176, 163), (80, 165), (0, 217), (48, 217), (96, 219), (144, 219),
                  (192, 221), (240, 221), (288, 223), (336, 223), (384, 225), (512, 282), (560, 282), (416, 284),
                  (464, 284), (320, 286), (368, 286), (224, 288), (272, 288), (128, 290), (176, 290), (80, 292),
                  (0, 344), (48, 344), (96, 346), (144, 346), (192, 348), (240, 348), (288, 350), (336, 350),
                  (384, 352), (0, 418), (48, 418), (96, 418), (144, 418), (192, 418), (240, 418), (288, 418),
                  (336, 418), (384, 416), (432, 414), (480, 412), (200, 55), (248, 55)]

lvl1_ladders = [(328, 159, 2), (390, 352, 10), (384, 100, 9), (96, 290, 8), (332, 286, 2), (407, 225, 9),
                (224, 160, 10), (82, 166, 8), (198, 223, 2), (198, 275, 3), (280, 52, 7)
                ]
lvl1_pumpkins = [(-10, 57)]

# Level two, same as lvl 1, add tuples of the topleft of the objects you want to create to each list
lvl2_scaffolds = []
lvl2_ladders = []
lvl2_barrels = []


# Player Ladder workings

# This function checks if the player is colliding wiht any ladder
# if so the player will have the ability to climb
def player_ladder_collision(player_GS: pygame.sprite.GroupSingle, ladder_list: list):
    p = player_GS.sprite
    coll_ladder = []
    count = 0
    for ladder in ladder_list:
        count += p.is_descend(ladder, window)
        if p.is_climb(ladder):
            p.can_climb = True
            coll_ladder.append(ladder)
        if count > 0:
            break

    if len(coll_ladder) == 0:
        p.can_climb = False
        p.is_ladder = False


def pumpkin_ladder(pumpkin: Enemy_Pumpkin):
    for ladder in ladder_objs:
        pumpkin.can_descend(ladder)


# Function to turn the lvls lists into proper objects
def create_objlist_for_levels(scafs, ladders, barrls):
    objects = []
    scaffold_objs = []
    for item in scafs:
        objects.append(Scaffold(item[0], item[1]))
        scaffold_objs.append(Scaffold(item[0], item[1]))
    for item in ladders:
        objects.append(Ladder(item[0], item[1], item[2]))
        ladder_objs.append(Ladder(item[0], item[1], item[2]))
    for item in barrls:
        objects.append(PILE_pumpkin(item[0], item[1]))
        pass
    return objects, scaffold_objs


def load_lvl1():
    lvl_objs, scaf_objs = create_objlist_for_levels(lvl1_scaffolds, lvl1_ladders, lvl1_pumpkins)
    return lvl_objs, scaf_objs


def load_lvl2():
    global lvl_objs
    global scaf_objs

    lvl_objs, scaf_objs = create_objlist_for_levels(lvl2_scaffolds, lvl2_ladders, lvl2_barrels)


# This functioin unloads all objects that build a map
# *** Does not remove enemies or mario, must make another function to do so.
def unload_lvl():
    global lvl_objs, scaf_objs, level_loaded

    lvl_objs.clear()
    scaf_objs.clear()
    level_loaded = 0


def set_scaffold_to_level():
    index = Curr_Level % 2
    index += 1
    for item in lvl_objs:
        if repr(item) == "Scaffold":
            item.set_level(index)


# Creates all objects and draws the level map to screen
# will be called every frame
def draw_map():
    global window
    global lvl_objs

    for obj in lvl_objs:
        obj.draw(window)

    hs_dis = prim_font_small.render(f"HighScore {int(highscore):08d}", False, (168, 43, 43))
    score_dis = sec_font_small.render(f"Score {current_score:08d}", False, (255, 255, 255))
    lvl_dis = prim_font_small.render(f"Lvl {Curr_Level}", False, (255, 255, 255))
    live_dis = sec_font_small.render(f"Life {lives}", False, (255, 255, 255))

    window.blit(hs_dis, (10, 0))
    window.blit(score_dis, (370, 0))
    window.blit(lvl_dis, (460, 15))
    window.blit(live_dis, (10, 10))


# This function is used to check if the player is above a rect and moves the player accordingly
# parameter is the player GroupSingle object
def player_scaf_collision(player, scaf_objs):
    p_sprite = player.sprite

    above_scaf = 0
    for scaf in scaf_objs:
        above_scaf += p_sprite.scaf_collision(scaf)
    if above_scaf == 0:
        p_sprite.in_air = True


# -----------------------------
# Temporary stuff


# **** Use this testing stuff
# -----------------------------
highscore = get_high_score()
intro_objs.append(Intro())
# Main function of program:
while Pro_Running:
    # Cycle through our events
    check_events()

    game_state_to_load()

    # updating our screen
    pygame.display.flip()

    # Frames per second
    Clock.tick(frame_rate)
write_new_highscore()
pygame.quit()
