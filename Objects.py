# Object file for project

import pygame
from random import randint

pygame.init()

class Scaffold:

    Scaffold_surf = pygame.image.load('Sprites/Scaffold/Scaf2.png')
    Scaffold_surf2 = pygame.image.load('Sprites/Scaffold/Scaf3.png')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 48, 16)
        self.surf = self.Scaffold_surf

    def __repr__(self):
        return f"Scaffold"

    def draw(self, win):
        win.blit(self.surf, self.rect)

    def set_level(self, level):
        # *** Change to proper sprite when have the images
        if level == 1:
            self.surf = self.Scaffold_surf
        elif level == 2:
            self.surf = self.Scaffold_surf2


class Ladder:
    # Ladder object drawn to window
    # (x,y) topleft of objct, rungs is the amount of rungs, builds downwards
    rung_surf = pygame.image.load('Sprites/Rung/RungBruh.png')

    def __init__(self, x: int, y: int, rungs: int):
        self.x = x
        self.y = y
        self.rungs = rungs
        self.rect = pygame.Rect(x, y, 16, 6 * self.rungs)

    def draw(self, win):
        for i in range(1, self.rungs + 1):
            win.blit(self.rung_surf.convert_alpha(), (self.x, self.y + (i * 6)))


class PILE_pumpkin:
    # These pumpkins only serve the purpose of drawing the pile of pumpkins yonkey yong takes from
    pilepumpkin_surf = pygame.image.load('Sprites/RollingPumpkins/StackPump.png')
    pilepumpkin_surf = pygame.transform.rotozoom(pilepumpkin_surf, 0, 2)
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 84, 46)

    def draw(self, window):
        window.blit(self.pilepumpkin_surf, self.rect)


class Player(pygame.sprite.Sprite):
    # temp_player_surf = pygame.Surface((26, 32))
    # temp_player_surf.fill('green')

    still_surf = pygame.image.load('Sprites/MrSkele/MS-centre.png')
    walk_r1 = pygame.image.load('Sprites/MrSkele/MS-right.png')
    walk_r1 = pygame.transform.rotozoom(walk_r1, 0, 0.6)
    walk_r2 = pygame.image.load('Sprites/MrSkele/MS-right2.png')
    walk_r2 = pygame.transform.rotozoom(walk_r2, 0, 0.6)

    walk_r3 = pygame.image.load('Sprites/MrSkele/MS-right4.png')
    walk_r3 = pygame.transform.rotozoom(walk_r3, 0, 0.6)
    walk_right_frames = [walk_r1, walk_r2, walk_r3]
    walk_l1 = pygame.transform.flip(walk_r1, True, False)
    walk_l2 = pygame.transform.flip(walk_r2, True, False)

    walk_l3 = pygame.transform.flip(walk_r3, True, False)
    walk_left_frames = [walk_l1, walk_l2, walk_l3]
    still_surf = pygame.transform.rotozoom(still_surf, 0, 0.5)

    r_jump = pygame.image.load('Sprites/MrSkele/MS-right3.png')
    r_jump = pygame.transform.rotozoom(r_jump, 0, 0.6)
    l_jump = pygame.transform.flip(r_jump, True, False)

    jump_se = pygame.mixer.Sound('Sounds/Jump Sound Effect.mp3')

    def __init__(self):
        super().__init__()
        self.image = self.still_surf
        self.rect = pygame.Rect(50, 360, 14, 36)
        self.gravity = 0
        self.in_air = True
        self.is_jump = False

        # Animation variables
        self.anim_index = 0
        # -1 for left, 0 for still, 1 for right
        self.dir = 0

        # Jump timer variables
        self.jump_timer = 0
        self.can_jump = True
        self.score_timer = 0

        # Ladder climbing variables
        self.can_climb = False
        # is ON ladder
        self.is_ladder = False
        self.can_descend = False
        self.top_ladder = False

        # death variables
        self.is_dead = False

    def animate(self):
        if self.is_dead:
            self.image = pygame.surface.Surface((1, 1))
        else:
            self.anim_index += 0.1
            if self.anim_index > 3:
                self.anim_index = 0
            if self.dir == 0:
                self.image = self.still_surf
            elif self.dir == -1:
                if self.in_air:
                    self.image = self.l_jump
                else:
                    self.image = self.walk_left_frames[int(self.anim_index)]
            elif self.dir == 1:
                if self.in_air:
                    self.image = self.r_jump
                else:
                    self.image = self.walk_right_frames[int(self.anim_index)]

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] and not self.is_ladder:
            self.rect.x += 3
            self.dir = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT] and not self.is_ladder:
            self.rect.x -= 3
            self.dir = -1
        if keys[pygame.K_SPACE] and not self.in_air and self.can_jump:
            self.gravity = -9
            self.in_air = True
            self.is_jump = True
            self.jump_timer = 1
            self.jump_se.play()
            #self.jump_se.play(start=1)
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and (self.can_climb or self.is_ladder):
            self.rect.y -= 5
            self.gravity = 0
            self.is_ladder = True
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and (self.is_ladder or self.can_descend):
            self.rect.y += 5
            self.gravity = 0
            self.is_ladder = True
        if not(keys[pygame.K_d] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_LEFT]):
            self.dir = 0

    def apply_gravity(self):
        if not self.is_ladder:
            if self.in_air:
                self.gravity += 1
                self.rect.y += self.gravity
            else:
                self.gravity = 0
            if self.rect.y >= 400:
                self.rect.y = 400
                self.in_air = False

    def scaf_collision(self, scaf: Scaffold) -> int:
        # First check if gravity is positive. This is done to prevent players sticking to scaffolds when jumping
        # from under
        # FIX LATER!!
        keys = pygame.key.get_pressed()
        if self.gravity >= 0 and not( (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.top_ladder ):
            if (scaf.rect.left <= self.rect.right <= scaf.rect.right) or (
                    scaf.rect.left <= self.rect.left <= scaf.rect.right) or (
                    scaf.rect.left <= self.rect.centerx <= scaf.rect.right):
                if scaf.rect.centery >= self.rect.bottom >= scaf.rect.top:
                    self.rect.bottom = scaf.rect.top
                    self.gravity = 0
                    self.in_air = False
                    self.is_jump = False
                    return 1
        return 0

    def is_climb(self, ladder: Ladder) -> bool:
        if self.rect.colliderect(ladder.rect) and not self.is_jump:
            return True
        else:
            return False

    def is_descend(self, ladder: Ladder, window) -> int:
        temp_rect = pygame.rect.Rect(self.rect.x + 4, self.rect.y + 32, 10, 20)

        if temp_rect.colliderect(ladder.rect):
            self.can_descend = True
            if self.rect.centery <= ladder.rect.top:
                self.top_ladder = True
            else:
                self.top_ladder = False
            return 1
        else:
            self.top_ladder = False
            self.can_descend = False
            return 0

    def jump_over(self, pump) -> bool:
        temp = pygame.rect.Rect(self.rect.x + 5, self.rect.y + 36, 4, 14)
        if temp.colliderect(pump.rect) and self.score_timer == 0:
            self.score_timer += 0.1
            return True
        else:
            return False

    def update(self):
        self.animate()
        if not self.is_dead:
            self.player_input()
            self.apply_gravity()
            if 0 < self.score_timer < 1:
                self.score_timer += 0.1
            if self.score_timer >= 1:
                self.score_timer = 0

            if self.rect.left <= 0:
                self.rect.left = 0
            if self.rect.right >= 512:
                self.rect.right = 512
            if 0 < self.jump_timer < 10:
                self.jump_timer += 1
                self.can_jump = False
            elif self.jump_timer >= 10:
                self.jump_timer = 0
                self.can_jump = True


class Yonkey(pygame.sprite.Sprite):
    # Replace with assets
    yonk_surf = pygame.image.load('Sprites/Yonkey/YonkRegular.png')
    yonk_throw_down = pygame.image.load('Sprites/Yonkey/YonkeyPumpkinThrowDown.png')
    yonk_pick_L = pygame.image.load('Sprites/Yonkey/YonkPickup.png')
    yonk_pick_R = pygame.transform.flip(yonk_pick_L, True, False)
    yonk_above_head = pygame.image.load('Sprites/Yonkey/YonkeyPumpkinAboveHead.png')

    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y
        self.image = self.yonk_surf
        self.rect = pygame.Rect(x, y, 42, 62)

        # animation vars
        # Anim states, n: neutral, t: taunt
        self.anim_state = 'n'
        self.anim_timer: float = 0
        self.taunt_frames = [pygame.image.load('Sprites/Yonkey/YonkeyDAB.png').convert_alpha(),
                             pygame.image.load('Sprites/Yonkey/YonkeyDABrev.png').convert_alpha()]
        self.throw_right_frames = [self.yonk_pick_L, self.yonk_above_head, self.yonk_pick_R]

        self.throw_down_frames = [self.yonk_pick_L, self.yonk_above_head, self.yonk_throw_down]

    def reset_pos(self):
        self.x = self.rect.x
        self.y = self.rect.y

    # This method will be triggered by the event, will cause Yonkey to taunt
    def taunt(self):
        self.anim_state = "t"
        self.rect.y -= 4

    def animate(self):
        if self.anim_state == 'n':
            self.image = self.yonk_surf
        elif self.anim_state == 't':
            self.anim_timer += 0.1
            t_index = int(self.anim_timer) % 2
            self.image = self.taunt_frames[t_index]

            if t_index == 0:
                self.rect.x = self.x - 4
            elif t_index == 1:
                self.rect.x = self.x - 18

            if self.anim_timer >= 4:
                self.anim_timer = 0
                self.anim_state = 'n'
                self.rect.x = self.x
                self.rect.y = self.y
        elif self.anim_state == 'tr':
            self.anim_timer += 0.05
            t_index = int(self.anim_timer) % 3
            self.image = self.throw_right_frames[t_index]

            if t_index == 0:
                self.rect.x = self.x - 22
                self.rect.y = self.y + 6
            elif t_index == 1:
                self.rect.y = self.y - 33
                self.rect.x = self.x - 2
            elif t_index == 2:
                self.rect.x = self.x - 4
                self.rect.y = self.y + 4

            if self.anim_timer >= 2.9:
                self.anim_timer = 0
                self.anim_state = 'n'
                self.rect.x = self.x
                self.rect.y = self.y
        elif self.anim_state == 'td':
            self.anim_timer += 0.05
            t_index = int(self.anim_timer) % 3
            self.image = self.throw_down_frames[t_index]

            if t_index == 0:
                self.rect.x = self.x - 22
                self.rect.y = self.y + 6
            elif t_index == 1:
                self.rect.y = self.y - 33
                self.rect.x = self.x - 2
            elif t_index == 2:
                self.rect.x = self.x - 8
                self.rect.y = self.y - 8

            if self.anim_timer > 2.9:
                self.anim_timer = 0
                self.anim_state = 'n'
                self.rect.x = self.x
                self.rect.y = self.y

    # This method will be triggered by the event, will cause Yonkey to throw barrel to the right
    def throw_pump_left(self):
        pass

    def throw_pump_right(self):
        self.anim_state = 'tr'

    # This method will be triggered by the event, will cause Yonkey to throw barrel downwards
    def throw_pump_down(self):
        self.anim_state = 'td'

    def update(self):
        self.animate()


# This class if for the Pumpkin enemy thrown downwards from Yonkey
# This enemy travels straight downwards
# If contacts with "mario", mario dies.
class Fall_Pumpkin:
    # Replace with asset
    pumpface = pygame.image.load('Sprites/RollingPumpkins/PumpkinFace.png')
    pumptop = pygame.image.load('Sprites/RollingPumpkins/FallPumpTop.png')
    pumptop = pygame.transform.rotozoom(pumptop, 0, 2)
    pumpback = pygame.image.load('Sprites/RollingPumpkins/FallPumpBack.png')
    pumpback = pygame.transform.rotozoom(pumpback, 0, 2)
    pumpbot = pygame.image.load('Sprites/RollingPumpkins/FallPumpBottom.png')
    pumpbot = pygame.transform.rotozoom(pumpbot, 0, 2)

    anim_frames = [pumpface, pumptop, pumpback, pumpbot]

    def __init__(self, x: int, y: int):
        self.surf = self.pumpface
        self.rect = pygame.Rect(x, y, 28, 28)
        self.gravity = 0
        self.anim_time = 0

    def animate(self):
        self.anim_time += 0.3
        index = int(self.anim_time) % 4
        self.surf = self.anim_frames[index]

    def apply_gravity(self):
        self.gravity += 2
        if self.gravity > 10:
            self.gravity = 10
        self.rect.y += self.gravity

    def update(self):
        self.apply_gravity()
        self.animate()


class Enemy_Pumpkin:
    # !!! animation looks very choppy
    # if have time try to rotate pumpkin by fractional turn
    # Replace with asset
    roll_pump_surf = pygame.image.load('Sprites/RollingPumpkins/PumpkinFace.png')
    rlp90 = pygame.transform.rotate(roll_pump_surf, 90)
    rlp180 = pygame.transform.flip(roll_pump_surf, False, True)
    rlp270 = pygame.transform.rotate(roll_pump_surf, 270)

    def __init__(self, x: int, y: int):
        self.surf = self.roll_pump_surf
        self.rect = pygame.Rect(x, y, 25, 25)
        self.in_air = True
        self.gravity = 0
        self.ladder_timer = 0

        # direction variable, 1 for right, 0 for left
        self.dir_right = 1
        self.dir_store = 0

        # animation variables
        self.roll_frames = [self.roll_pump_surf, self.rlp90, self.rlp180, self.rlp270]
        self.anim_index = 0

    def change_direction(self):
        if self.dir_right == 1:
            self.dir_right = 0
        else:
            self.dir_right = 1

    def apply_gravity(self):
        if self.in_air:
            self.gravity += 0.8
            self.rect.y += self.gravity
        else:
            self.gravity = 0

    def roll_right(self):
        self.anim_index += 0.5
        if self.anim_index >= 4:
            self.anim_index = 0
        self.surf = self.roll_frames[int(self.anim_index)]

        self.dir_store = 0
        self.rect.x += 4

    def roll_left(self):
        self.anim_index -= 0.5
        if self.anim_index <= 0:
            self.anim_index = 3
        self.surf = self.roll_frames[int(self.anim_index)]

        self.dir_store = 1
        self.rect.x -= 4

    def scaf_collision(self, scaf: Scaffold):
        temp = pygame.rect.Rect(self.rect.x + 10, self.rect.y + 20, 10, 15)
        if temp.colliderect(scaf.rect) and self.dir_right != 2:
            self.rect.bottom = scaf.rect.top
            self.gravity = 0
            self.in_air = False
            return 1
        else:
            return 0

    def wall_collision(self):
        if self.rect.right >= 512:
            self.dir_right = 0
        elif self.rect.left <= 0 and not self.rect.top >= 380:
            self.dir_right = 1

    def can_descend(self, ladder: Ladder):
        temp = pygame.rect.Rect(self.rect.x + 10, self.rect.y + 26, 2, 4)
        if temp.colliderect(ladder.rect):
            roll = randint(0, 8)
            if roll == 0:
                self.dir_right = 2
                self.ladder_timer += 0.05

    def update(self):
        if self.ladder_timer > 0:
            self.ladder_timer += 0.1
        if self.ladder_timer >= 1:
            self.ladder_timer = 0
            self.dir_right = self.dir_store
        self.wall_collision()
        if self.dir_right == 1:
            self.roll_right()
        elif self.dir_right == 0:
            self.roll_left()
        elif self.dir_right == 2:
            pass
        self.apply_gravity()


class IntroArrow:
    def __init__(self, x: int, y: int):
        self.gold_col = (218, 165,32)
        self.x = x
        self.y = y
        self._piece1 = pygame.surface.Surface((30, 10))
        self._piece2 = pygame.surface.Surface((5, 30))
        self._piece3 = pygame.surface.Surface((5, 20))
        self._piece1.fill(self.gold_col)
        self._piece2.fill(self.gold_col)
        self._piece3.fill(self.gold_col)
        self._p1_rect = pygame.rect.Rect(x, y + 10, 30, 10)
        self._p2_rect = pygame.rect.Rect(x + 17, y, 5, 30)
        self._p3_rect = pygame.rect.Rect(x + 22, y + 5, 5, 20)
        #self.timer = 0
        #self._pieces = [self._piece1, self._piece2, self._piece3]

    def draw(self, window):
        # can add pulse feature, if have time

        window.blit(self._piece1, self._p1_rect)
        window.blit(self._piece2, self._p2_rect)
        window.blit(self._piece3, self._p3_rect)

    def switch_selection(self, selection: int):
        if selection == 0:
            self.y = 250
        elif selection == 1:
            self.y = 300
        elif selection == 2:
            self.y = 350
        self._p1_rect = pygame.rect.Rect(self.x, self.y + 10, 30, 10)
        self._p2_rect = pygame.rect.Rect(self.x + 17, self.y, 5, 30)
        self._p3_rect = pygame.rect.Rect(self.x + 22, self.y + 5, 5, 20)


class Intro:
    def __init__(self):
        self.selection = 0
        self.sel1 = pygame.rect.Rect(100, 240, 422, 50)
        self.sel2 = pygame.rect.Rect(100, 290, 422, 50)
        #self.sel3 = pygame.rect.Rect(100, 290, 422, 50)
        self.timer = 0

    def input(self, arrow):
        keys = pygame.key.get_pressed()
        if self.timer == 0:
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.timer += 1
                self.selection += 1
                if self.selection >= 2:
                    self.selection = 1
                arrow.switch_selection(self.selection)
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.timer += 1
                self.selection -= 1
                if self.selection <= 0:
                    self.selection = 0
                arrow.switch_selection(self.selection)
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                if self.selection == 0:
                    return 'level_intro'
                elif self.selection == 1:
                    return 'quit'
        if self.timer > 0:
            self.timer += 1
        if self.timer >= 5:
            self.timer = 0
        return ''


class Goal:
    def __init__(self, x: int, y: int):
        self.rect = pygame.rect.Rect(x, y, 50, 10)
        self.surf = pygame.surface.Surface((50, 10))
        self.surf.fill('white')

    def draw(self, window):
        window.blit(self.surf, self.rect)


class DeadSkele:
    surf1 = pygame.image.load('Sprites/MrSkele/SkeleDie1.png')
    surf1 = pygame.transform.rotozoom(surf1, 0, 1.5)
    surf2 = pygame.image.load('Sprites/MrSkele/SkeleDie2.png')
    surf2 = pygame.transform.rotozoom(surf2, 0, 1.5)
    surf3 = pygame.image.load('Sprites/MrSkele/SkeleDie3.png')
    surf3 = pygame.transform.rotozoom(surf3, 0, 1.5)
    surf4 = pygame.image.load('Sprites/MrSkele/SkeleDie4.png')
    surf4 = pygame.transform.rotozoom(surf4, 0, 1.5)
    surfs = [surf1, surf2, surf3, surf4]

    def __init__(self, x: int, y: int):
        self.surf = self.surf1
        self.rect = pygame.rect.Rect(x, y, 35, 35)
        self.index = 0

    def next_frame(self):
        self.index += 1
        if self.index >= 3:
            self.index = 3
        self.surf = self.surfs[self.index]

    def draw(self, win):
        win.blit(self.surf, self.rect)


class Ghosty:
    temp_surf = pygame.image.load('Sprites/Ghosty/Ghosty.png')

    def __init__(self, x: int, y: int):
        self.surf = self.temp_surf
        self.rect = self.temp_surf.get_rect(midbottom=(x, y))

    def draw(self, win):
        win.blit(self.surf, self.rect)

