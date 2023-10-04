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
        self.block_list = config_list[2]  # blocks list (x,y,width,ht)

        self.obstacles = set()
        self.current_pos = (self.pos[0], self.pos[1])
        self.unvisited_blocks = set()
        # Record coordinates for all blocks(obstacles)
        for block in self.block_list:
            print(block)
            self.add_obstacle(block)
        self.priority_queue = PriorityQueue()
        self.initialize_unvisited_blocks()

        self.loop_avoider = {}

        # fill in with your info
        self.name = "Sanjee Yogeswaran"
        self.id = "47514289"

    def initialize_unvisited_blocks(self):
        # Initialize the set of unvisited blocks
        for x in range(self.room_width):
            for y in range(self.room_height):
                if (x, y) not in self.obstacles:
                    self.unvisited_blocks.add((x, y))

    def add_obstacle(self, obstacle):
        # Add an obstacle to the set of obstacles
        x, y, width, height = obstacle
        for i in range(x, x + width):
            for j in range(y, y + height):
                self.obstacles.add((i, j))

    def heuristic(self, position):
        # Heuristic: Manhattan distance to the closest unvisited block
        min_distance = float("inf")
        for block in self.unvisited_blocks:
            distance = abs(position[0] - block[0]) + abs(position[1] - block[1])
            min_distance = min(min_distance, distance)
        return min_distance

    def get_next_move(self, current_pos):
        # Define possible directions: north, east, south, west
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # Create a priority queue for A* search
        priority_queue = PriorityQueue()

        for dx, dy in directions:
            next_x = current_pos[0] + dx
            next_y = current_pos[1] + dy

            # Check if the next position is within the grid boundaries
            if 0 <= next_x <= self.room_width and 0 <= next_y < self.room_height:
                next_pos = (next_x, next_y)

                # Check if the next position is not an obstacle
                if next_pos not in self.obstacles:
                    # Calculate the priority based on the heuristic
                    priority = self.heuristic(next_pos)
                    priority_queue.put((priority, next_pos, directions.index((dx, dy))))

        # Choose the cell with the highest priority (based on the heuristic)
        if not priority_queue.empty():
            _, next_pos, direction = priority_queue.get()
            # Remove the visited block from the set of unvisited blocks
            if next_pos in self.unvisited_blocks:
                self.unvisited_blocks.remove(next_pos)

            if next_pos not in self.loop_avoider:
                self.loop_avoider[next_pos] = 1
            else:
                self.loop_avoider[next_pos] += 1

            if self.loop_avoider[next_pos] >= 4:
                return directions.index(random.choice(directions))

            return direction

        # If no valid move is found, stay in the current position (backtrack)
        return directions.index(random.choice(directions))
