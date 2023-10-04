"""
    RoboVac - clean the room
    note: PyGame needs an empty file __init__.py in directory to draw!
    v. 0.90
"""

import random

import pygame
import sys

# modify RoboVac0 or copy and create your own file
from RoboVac1 import RoboVac

BLACK = (0, 0, 0)
GOLD = (200, 0, 0)
WHITE = (200, 200, 200)
GREEN = (0, 200, 0)
BROWN = (165, 42, 42)
ORANGE = (255, 140, 0)
YELLOW = (240, 240, 130)

# load images
RoboVacPic = pygame.image.load("robovac.png")


class Room:
    def __init__(self, level):
        pygame.init()
        self.game_level = level

        # sets up room (size) with blocks and vacuum start position
        # -Robovac is initialized with data structure containing
        #   all room data

        # window  - varies in size
        window_size_list = [360, 390, 420]
        self.window_width = random.choice(window_size_list)
        self.window_height = random.choice(window_size_list)

        # grid max values for width and height
        self.room_blocksize = 30
        self.max_width = (int)(self.window_width / self.room_blocksize)
        self.max_height = (int)(self.window_height / self.room_blocksize)
        # for grid logic
        self.max_x = (self.window_width / self.room_blocksize) - 1
        self.max_y = (self.window_height / self.room_blocksize) - 1

        # blocks - number of blocks depends on game_level
        self.block_list = []

        if self.game_level >= 1:
            self.block_list.append((1, 2, 4, 1))

        if self.game_level >= 2:
            self.block_list.append((1, 2, 4, 1))
            self.block_list.append((3, 2, 1, 4))
            self.block_list.append((1, 2, 4, 2))

        if self.game_level >= 3:
            self.block_list.append((1, 2, 4, 1))
            self.block_list.append((6, 6, 4, 1))
            self.block_list.append((9, 6, 1, 3))
            self.block_list.append((6, 8, 4, 1))

        if self.game_level >= 4:
            self.block_list.append((0, 8, 4, 1))

        if self.game_level >= 5:
            self.block_list.append((10, 10, 4, 1))

        # vacuum random positioning
        x = 0
        y = 0
        dx = 3
        dy = 3  # dist from edge

        intersect = True
        while intersect:
            x = random.randrange(dx, self.max_x)
            y = random.randrange(dy, self.max_y)
            intersect = self.does_pos_intersect_blocks((x, y))
        self.vac_pos = (x, y)  # starting location for vacuum

        # define sets with positions as tuples; useful utilities
        self.clean_set = set()
        self.clean_set.add(self.vac_pos)

        # create set with all tiles
        self.free_tiles_set = set()
        for x in range(self.max_width):
            for y in range(self.max_height):
                self.free_tiles_set.add((x, y))

        # BLOCKS
        # create set of all block positions from block list
        self.block_tiles_set = set()

        for b in self.block_list:
            for x in range(b[0], b[0] + b[2]):
                for y in range(b[1], b[1] + b[3]):
                    self.block_tiles_set.add((x, y))

        self.free_tiles_set = self.free_tiles_set - self.block_tiles_set

        # easily get max number of tiles that need cleaning
        self.max_tiles = len(self.free_tiles_set)

        # other  for display
        self.font = pygame.font.SysFont("Arial", 20)

    def get_room_config(self):
        """
        Returns LIST with all the info RoboVac needs;
              passed to RoboVac constructor
        [ (room_width, room_height), (vac_x, vac_y) [list-of-blocks] ]
         note: list-of-blocks is list of tuples (x,y,width, height)
        """
        room_config_list = [
            (self.max_width, self.max_height),
            self.vac_pos,
            self.block_list,
        ]
        return room_config_list

    # Utility Methods ------
    def add_clean_pos(self, xytuple):
        self.clean_set.add(xytuple)

    def rect_intersect(self, pos, rect):
        rx, ry, width, height = rect
        x, y = pos
        is_intersect = x >= rx and x < (rx + width) and y >= ry and y < (ry + height)
        return is_intersect

    def does_pos_intersect_blocks(self, pos):
        #  check all blocks
        for rect in self.block_list:
            if self.rect_intersect(pos, rect):
                return True
        return False

    def is_ok_next_pos(self, xytuple):
        x, y = xytuple
        if x < 0 & x > self.max_x & y < 0 & y > self.max_y:
            return False
        # check intersect with blocks
        for rect in self.block_list:
            rx, ry, width, height = rect
            if x > rx & x < (rx + width) & y > ry & y < (ry + height):
                return False
        return True

    def __str__(self):
        return (
            f"cpos={self.vac_pos},max_x={self.max_x} \
        max_y={self.max_y}, window:({self.window_width}, "
            f"{self.window_height}) \
         blocksize={self.room_blocksize}  clean={self.clean_set}"
        )


def get_date_time():
    import datetime

    today = datetime.date.today()
    hour = datetime.datetime.now().hour
    min = datetime.datetime.now().minute
    hour_str = f"{hour:02d}"
    min_str = f"{min:02d}"
    return f"{today} {hour_str}:{min_str}"


#  Utility Functions for Drawing (PyGame) -----------------------
def draw_tile(room, x, y):
    x_draw = x * room.room_blocksize
    y_draw = y * room.room_blocksize
    rect = pygame.Rect(x_draw, y_draw, room.room_blocksize, room.room_blocksize)
    # draw rect
    pygame.draw.rect(SCREEN, GREEN, rect, 0)  # 0 means fill!!
    pygame.draw.rect(SCREEN, WHITE, rect, 1)


def draw_all_tiles(room):
    for r_tuple in room.clean_set:
        x, y = r_tuple
        draw_tile(room, x, y)
    # draw vacuum
    draw_vac(room)


def draw_blocks(room):
    for rect in room.block_list:
        x, y, w, h = rect
        x_draw = x * room.room_blocksize
        y_draw = y * room.room_blocksize
        rect = pygame.Rect(
            x_draw, y_draw, room.room_blocksize * w, room.room_blocksize * h
        )
        # draw rect
        pygame.draw.rect(SCREEN, ORANGE, rect, 0)  # 0 means fill!!


def draw_vac(room):
    # draw RoboVac at it's current location
    global SCREEN, RoboVacPic
    global GOLD
    x, y = room.vac_pos
    blocksize = room.room_blocksize
    SCREEN.blit(RoboVacPic, (x * blocksize, y * blocksize))
    pygame.display.flip()


def drawGrid(room):
    # draw basic room grid..
    for x in range(0, room.window_width, room.room_blocksize):
        for y in range(0, room.window_height, room.room_blocksize):
            rect = pygame.Rect(x, y, room.room_blocksize, room.room_blocksize)
            pygame.draw.rect(SCREEN, WHITE, rect, 1)


def main(game_level):
    global SCREEN

    # max # game cycles allowed robot
    max_cycles = 400

    # create the room - pass in the level
    room = Room(game_level)

    # create the Robot Vacuum AI : pass in configuration
    config_list = room.get_room_config()
    robo_vac = RoboVac(config_list)

    # set up the screen display ----------------
    SCREEN = pygame.display.set_mode((room.window_width, room.window_height))
    SCREEN.fill(BLACK)

    drawGrid(room)  # draws grid - white outlines; black bkgnd
    draw_vac(room)  # draw vac at initial random pos
    draw_blocks(room)

    pygame.display.update()

    ## CONTROL GAME SPEED   ** OK to change  **
    delay_time = 100
    # game delay in milliseconds between cycles

    move_count = 5  # track number of moves

    # GAME LOOP ---------
    while True:
        if (move_count % 50) == 0:
            print(f"Move Count: {move_count}")

        # check if done..
        if len(room.clean_set) == room.max_tiles or move_count > max_cycles:
            result_str = " SUCCESS!"
            if move_count > max_cycles:
                result_str = " OUT OF TIME"
            print(
                f"--------------------------------------\n"
                f"RESULTS ***** {result_str}\n"
                f"{robo_vac.name} ID={robo_vac.id} {get_date_time()}"
                f"\nLevel: {room.game_level}  Coverage: "
                f"{((len(room.clean_set)/room.max_tiles)*100):.1f}%\n"
                f"Cycles: {move_count} Tiles Cleaned: "
                f"{len(room.clean_set)} Max Tiles: {room.max_tiles}"
                f"Total Tiles {room.max_tiles}\n"
                f"Efficiency: {(room.max_tiles/move_count):.2f}"
            )
            # results to logfile
            result_str = (
                f"{get_date_time()} {robo_vac.id}"
                f" {robo_vac.name} "
                f" L{room.game_level} "
                f"Coverage:{((len(room.clean_set)/room.max_tiles)):.2f} "
                f"Eff:{(room.max_tiles/move_count):.2f}\n"
            )
            print(result_str)
            f = open("log.txt", "a")
            f.write(result_str)
            f.close()

            pygame.quit()
            sys.exit()

        else:  # play game  -------------------------
            move_count += 1
            pygame.display.update()

            # CALL ROBO VAC --Returns Direction based on location
            dir = robo_vac.get_next_move(room.vac_pos)
            #  ###################################################

            # Determine if direction results in legal move
            # IF YES, update robot position, else pos remains same

            x, y = room.vac_pos  # current position
            # adjust based on direction only if new pos inside room
            if dir == 0:
                if y > 0:
                    y = y - 1
            elif dir == 1:
                if x < room.max_x:
                    x = x + 1
            elif dir == 2:
                if y < room.max_y:
                    y = y + 1
            elif dir == 3:
                if x > 0:
                    x = x - 1

            if (x, y) == room.vac_pos:  # tried to go beyond room
                print(f"dir={dir}  BLOCKED: WALL")
            elif (x, y) in room.block_tiles_set:
                print(f"dir={dir} BLOCKED: FURNITURE")
            else:
                room.vac_pos = (x, y)  # update vacuum position
                room.add_clean_pos(room.vac_pos)  # track new clean tile
                draw_all_tiles(room)

            # draw vacuum
            draw_vac(room)

            pygame.display.flip()
            pygame.display.update()

            # CONTROLS GAME SPEED
            pygame.time.delay(delay_time)

            # REQUIRED for PyGame - close window,stop game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    """set your game level -----
    0 = no blocks
    1 = 1 block
    2 = 4 blocks
    3 = 8 blocks
    4 = 9 blocks
    5 = 10 blocks
    """

    game_level = 5  # OK to change this from easy to more complex

    # calls main with the game level & runs the simulation
    main(game_level)
