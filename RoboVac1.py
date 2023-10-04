"""
create robot vacuum that cleans all the floors of a grid.
main creates an instance of RoboVac (your code) and provides:
- grid size
- loc of robovac
- list of x,y,w,h tuples are instance of rectangluar blocks

goal: visit all tiles
exec will : create instance and in game loop call : nextMove()  ??
"""
import random
from queue import PriorityQueue


class RoboVac:
    def __init__(self, config_list):
        self.room_width, self.room_height = config_list[0]
        self.pos = config_list[1]  # starting position of vacuum
        self.current_pos = (self.pos[0], self.pos[1])

        self.obstacles = set()
        self.unvisited_blocks = set()
        self.priority_queue = PriorityQueue()
        # Creates unvisited blocks set; adds every block in grid to set
        self.initialize_unvisited_blocks()

        # Holds previous state
        self.prev_pos = (-1, -1)
        self.prev_direction = -1

        # Loop Avoider: how many times RoboVac has visited a block
        # (key: position, value: count of times visited)
        self.loop_avoider = {}

        # Consecutive Visited: how many times RoboVac has consecutively
        # visited already visited blocks
        self.consecutive_visited = 0

        # Seek Mode: sets mode to seek a corner or random unvisited block
        self.seek_mode = False

        # Next Unvisited: position of corner or random unvisited block
        self.next_unvisited = (-1, -1)

        # Loop avoider queue: used to move RoboVac in certain direction multiple times
        self.loop_avoider_queue = PriorityQueue()

        # Adds positions of all walls to obstacle list
        self.initialize_walls()

        # fill in with your info
        self.name = "Sanjee Yogeswaran"
        self.id = "47514289"

    ########################################################################
    # Creates a set with all blocks in the grid given width and height
    ########################################################################
    def initialize_unvisited_blocks(self):
        # Initialize the set of unvisited blocks
        for x in range(self.room_width):
            for y in range(self.room_height):
                self.unvisited_blocks.add((x, y))

    def initialize_walls(self):
        for x in range(self.room_width):
            self.obstacles.add((x, self.room_height))
            self.obstacles.add((x, -1))

        for y in range(self.room_height):
            self.obstacles.add((-1, y))
            self.obstacles.add((self.room_width, y))

    ########################################################################
    # A* heuristic using Manhattan distance
    # This algorithm checks against all unvisited blocks
    ########################################################################
    def heuristic(self, position):
        # Heuristic: Manhattan distance to the closest unvisited block
        min_distance = float("inf")
        for block in self.unvisited_blocks:
            distance = abs(position[0] - block[0]) + abs(position[1] - block[1])
            min_distance = min(min_distance, distance)
        return min_distance

    ########################################################################
    # Modified heuristic using Manhattan distance
    # This algorithm checks against a specific block
    # Param target_block is expected to be a random unvisited block or corner
    ########################################################################
    def heuristic2(self, position, target_block):
        # Heuristic: Manhattan distance to a target block
        distance = abs(position[0] - target_block[0]) + abs(
            position[1] - target_block[1]
        )
        return distance

    def get_next_move(self, current_pos):
        # Define possible directions: north, east, south, west
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # Define coordinates for all four corners
        corners = [
            (0, 0),
            (0, self.room_width - 1),
            (self.room_height - 1, 0),
            (self.room_width - 1, self.room_height - 1),
        ]

        # Loop avoider queue algorithm
        # RoboVac moves up to 4 times in a certain direction to avoid obstacles
        if not self.loop_avoider_queue.empty():
            priority, next_pos, direction = self.loop_avoider_queue.get()
            if next_pos in self.unvisited_blocks:
                self.unvisited_blocks.remove(next_pos)
                self.consecutive_visited = 0
                self.loop_avoider_queue = PriorityQueue()
                self.seek_mode = False
            # Keep counter of consecutive moves to visited blocks
            else:
                self.consecutive_visited += 1
            self.prev_pos = next_pos
            self.prev_direction = direction
            return direction

        # Logic if RoboVac has not moved(hit an obstacle or wall)
        if self.prev_pos == current_pos:
            # Detect obstacles on the fly if RoboVac didn't move position
            obstacle = (
                self.prev_pos[0] + directions[self.prev_direction][0],
                self.prev_pos[1] + directions[self.prev_direction][1],
            )
            print(f"added obstacle {obstacle}")
            self.obstacles.add(obstacle)
            self.consecutive_visited += 1

        self.prev_pos = current_pos

        # If RoboVac is spending too much time on already visited blocks,
        # start seek mode for a corner or random unvisited block
        if self.consecutive_visited >= 8 and not self.seek_mode:
            self.consecutive_visited = 0
            self.next_unvisited = (-1, -1)
            for corner in random.sample(corners, 4):
                if corner in self.unvisited_blocks:
                    self.next_unvisited = corner
            if self.next_unvisited == (-1, -1):
                self.next_unvisited = random.choice(list(self.unvisited_blocks))
            self.seek_mode = True

        ########################################################################
        # Seek mode: where a random unvisited block or corner is selected
        ########################################################################
        while self.seek_mode:
            # If RoboVac is unable to get close enough
            # to the corner or unvisited block with 8 moves,
            # there may be an obstacle in the way;
            # pick another corner or random unvisited block
            if self.consecutive_visited >= 8:
                self.next_unvisited = (-1, -1)
                for corner in random.sample(corners, 4):
                    if corner in self.unvisited_blocks:
                        self.next_unvisited = corner
                if self.next_unvisited == (-1, -1):
                    self.next_unvisited = random.choice(list(self.unvisited_blocks))
                # Reset consecutive counter, so that algorithm
                # tries different coordinates every 8 moves
                self.consecutive_visited = 0
            print(f"seeking {self.next_unvisited}")
            # Reset priority queue for seek mode
            self.priority_queue = PriorityQueue()
            # Loop through every move in all 4 directions
            for dx, dy in directions:
                next_x = current_pos[0] + dx
                next_y = current_pos[1] + dy

                # Check if the next position is within the grid boundaries
                if 0 <= next_x < self.room_width and 0 <= next_y < self.room_height:
                    next_pos = (next_x, next_y)

                    ########################################################################
                    # Heuristic calculations for seek mode
                    ########################################################################
                    # Check if the next position is not an obstacle
                    if next_pos not in self.obstacles:
                        # Calculate distance to selected corner or random unvisited block
                        # This is a modification of the A* heuristic where
                        # previously visited positions are allowed
                        priority = self.heuristic2(next_pos, self.next_unvisited)
                        self.priority_queue.put(
                            (priority, next_pos, directions.index((dx, dy)))
                        )

                        # Also if an adjacent block that is unvisited
                        # (heuristic function validates unvisited)
                        # has priority(distance) == 0, move there
                        priority = self.heuristic(next_pos)
                        if priority == 0:
                            self.priority_queue.put(
                                (priority, next_pos, directions.index((dx, dy)))
                            )
            # Pick lowest distance to unvisited block
            if not self.priority_queue.empty():
                priority, next_pos, direction = self.priority_queue.get()
                # Remove the visited block from the set of unvisited blocks
                # Turn off seek mode if RoboVac hits an unvisited block
                if next_pos in self.unvisited_blocks:
                    self.unvisited_blocks.remove(next_pos)
                    self.consecutive_visited = 0
                    self.seek_mode = False
                # Keep counter of consecutive moves to already visited blocks
                else:
                    self.consecutive_visited += 1
                ########################################################################
                # Loop avoider algorithm
                # If the next position has been visited equal or more than 4 times,
                # start moving randomly to get out of obstacle
                ########################################################################
                if next_pos not in self.loop_avoider:
                    self.loop_avoider[next_pos] = 1
                else:
                    self.loop_avoider[next_pos] += 1

                # Check if the next position has been visited equal or more than 4 times
                if self.loop_avoider[next_pos] >= 4:
                    while True:
                        # pick a direction that doesn't collide with an obstacle
                        random_direction = random.choice(directions)
                        next_pos = (
                            current_pos[0] + random_direction[0],
                            current_pos[1] + random_direction[1],
                        )
                        if next_pos not in self.obstacles:
                            print(
                                f"loop avoider direction: {directions.index(random_direction)}"
                            )
                            break

                    # If we visit an unvisited block, break out of seek mode
                    # and use normal A* search instead
                    if next_pos in self.unvisited_blocks:
                        self.consecutive_visited = 0
                        self.seek_mode = False
                    else:
                        self.consecutive_visited += 1
                    # To avoid loops, we move RoboVac in a certain direction 3 times
                    # by adding moves in the same direction 2 times to loop avoider queue
                    # and returning that direction 1 time
                    for i in range(1, 4):
                        next_pos = (
                            current_pos[0] + random_direction[0] * i,
                            current_pos[1] + random_direction[1] * i,
                        )
                        if next_pos not in self.obstacles:
                            self.loop_avoider_queue.put(
                                (0, next_pos, directions.index(random_direction))
                            )
                            self.loop_avoider[next_pos] = 0
                    print("loop avoider activated")
                    return directions.index(random_direction)
                ########################################################################
                # End Loop Avoider Algorithm
                ########################################################################
                # If not loop avoider,
                # move in direction towards corner or random unvisited block
                self.prev_direction = direction
                return direction

        ########################################################################
        # End Seek Mode Code
        ########################################################################
        # Define normal A* search sequence here
        ########################################################################

        # Reset priority queue for regular A* search
        self.priority_queue = PriorityQueue()
        for dx, dy in directions:
            next_x = current_pos[0] + dx
            next_y = current_pos[1] + dy

            # Check if the next position is within the grid boundaries
            if 0 <= next_x < self.room_width and 0 <= next_y < self.room_height:
                next_pos = (next_x, next_y)

                # Check if the next position is not an obstacle and not visited
                # Calculate the distance(priority) based on the Manhattan distance
                if next_pos not in self.obstacles and next_pos in self.unvisited_blocks:
                    priority = self.heuristic(next_pos)
                    self.priority_queue.put(
                        (priority, next_pos, directions.index((dx, dy)))
                    )

        # Choose the direction and next position with the lowest distance(priority)
        if not self.priority_queue.empty():
            priority, next_pos, direction = self.priority_queue.get()

            # Remove the visited block from the set of unvisited blocks
            if next_pos in self.unvisited_blocks:
                self.unvisited_blocks.remove(next_pos)
                self.consecutive_visited = 0
            else:
                self.consecutive_visited += 1

            self.prev_direction = direction
            return direction

        # If no valid move is found, pick random direction to move in
        # Random direction must not be in obstacles
        while True:
            random_direction = directions.index(random.choice(directions))
            next_x = current_pos[0] + directions[random_direction][0]
            next_y = current_pos[1] + directions[random_direction][1]
            if (next_x, next_y) not in self.obstacles:
                break
        if (next_x, next_y) in self.unvisited_blocks:
            self.unvisited_blocks.remove((next_x, next_y))
            self.consecutive_visited = 0
        else:
            self.consecutive_visited += 1
        self.prev_direction = random_direction
        print("main random")
        return random_direction
