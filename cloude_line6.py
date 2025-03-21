import pygame
import math
from queue import PriorityQueue
from itertools import permutations

# Initialize Pygame
pygame.init()

# Window setup
width = 800
win = pygame.display.set_mode((width, width))
pygame.display.set_caption("A* Path Finding Algorithm with Waypoints")

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
YELLOW = (255, 255, 0)  # New color for mandatory waypoints

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = BLACK
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def is_waypoint(self):
        return self.color == YELLOW

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_waypoint(self):
        self.color = YELLOW

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def make_navigable(self):
        self.color = WHITE

    def reset(self):
        self.color = BLACK

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not (current.is_start() or current.is_end() or current.is_waypoint()):
            current.make_path()
        draw()

def find_path_between_points(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            return came_from

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not (neighbor.is_start() or neighbor.is_end() or neighbor.is_waypoint()):
                        neighbor.make_navigable()

        draw()

        if current != start and not (current.is_start() or current.is_end() or current.is_waypoint()):
            current.make_navigable()

    return None

def find_path_through_waypoints(draw, grid, start, end, waypoints):
    if not waypoints:
        return find_path_between_points(draw, grid, start, end)

    # Try all possible orders of waypoints
    all_points = [start] + waypoints + [end]
    shortest_path = None
    shortest_length = float('inf')

    # Try each permutation of waypoints
    for waypoint_order in permutations(waypoints):
        current_path = {}
        total_length = 0
        path_valid = True
        points_sequence = [start] + list(waypoint_order) + [end]

        # Find path between consecutive points
        for i in range(len(points_sequence) - 1):
            path = find_path_between_points(draw, grid, points_sequence[i], points_sequence[i + 1])
            if path is None:
                path_valid = False
                break
            current_path.update(path)
            # Calculate path length
            point = points_sequence[i + 1]
            length = 0
            while point in path:
                length += 1
                point = path[point]
            total_length += length

        if path_valid and total_length < shortest_length:
            shortest_length = total_length
            shortest_path = current_path

    if shortest_path:
        reconstruct_path(shortest_path, end, draw)
        return True

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    waypoints = []

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end and spot not in waypoints:
                    start = spot
                    start.make_start()
                elif not end and spot != start and spot not in waypoints:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start and spot not in waypoints:
                    spot.make_navigable()

            elif pygame.mouse.get_pressed()[1]:  # Middle mouse button (wheel)
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if spot != start and spot != end and not spot.is_waypoint():
                    spot.make_waypoint()
                    waypoints.append(spot)

            elif pygame.mouse.get_pressed()[2]:  # Right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if spot.is_waypoint():
                    waypoints.remove(spot)
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    if not find_path_through_waypoints(
                        lambda: draw(win, grid, ROWS, width),
                        grid,
                        start,
                        end,
                        waypoints
                    ):
                        print("No valid path exists through all waypoints!")

    pygame.quit()

if __name__ == "__main__":
    main(win, width)