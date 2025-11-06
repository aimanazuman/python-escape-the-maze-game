import pygame
import math
import random
from collections import defaultdict
from constants import (
    ENEMY_SIZE, ENEMY_SPEED, ENEMY_COLOR, TILE_SIZE,
    ENEMY_CHASE_DISTANCE, ENEMY_LOSE_DISTANCE
)


class Enemy:
    """Grid-based enemy with improved pathfinding, perfect tile LoS, ping-pong fix,
    and smarter patrol memory. Kept in the original code style so it plugs right in.
    """

    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED * 2.5
        self.color = ENEMY_COLOR
        self.is_moving = False

        self.state = "patrol"
        self.patrol_direction = random.choice(["up", "down", "left", "right"])
        self.last_move_direction = None  # used to avoid immediate reversals
        self.move_timer = 0
        self.move_delay = 20
        self.stuck_counter = 0

        self.last_player_grid_x = None
        self.last_player_grid_y = None
        self.chase_cooldown = 0

        # Patrol memory: count visits per tile to prefer exploring less-visited tiles
        self.visited_tiles = defaultdict(int)
        self.visited_tiles[(self.grid_x, self.grid_y)] += 1

        try:
            self.image = pygame.image.load("assets/images/enemy.png")
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.use_image = True
        except:
            self.image = None
            self.use_image = False

    def calculate_distance(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    # ----------------------
    # Tile-based Bresenham LoS
    # ----------------------
    def _wall_tile_set(self, walls):
        """Return a set of tiles occupied by walls (gx, gy)."""
        return {(w.x // TILE_SIZE, w.y // TILE_SIZE) for w in walls}

    def _bresenham_tiles(self, start, end):
        """Return list of grid tiles (gx,gy) along the line from start to end inclusive.
        start/end are (gx,gy) integers. Implementation of integer Bresenham line algorithm."""
        x0, y0 = start
        x1, y1 = end
        tiles = []

        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # error value

        while True:
            tiles.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

        return tiles

    def has_line_of_sight(self, player_pos, walls):
        """Check LOS using tile-by-tile Bresenham: return True only when no wall tile lies between."""
        # Convert pixel positions to grid coordinates
        player_gx = int(player_pos[0] // TILE_SIZE)
        player_gy = int(player_pos[1] // TILE_SIZE)
        enemy_gx = self.grid_x
        enemy_gy = self.grid_y

        wall_tiles = self._wall_tile_set(walls)
        line_tiles = self._bresenham_tiles((enemy_gx, enemy_gy), (player_gx, player_gy))

        # Exclude the first tile (enemy's own tile) and the last tile (player's tile)
        # If you want walls in player's tile to block, remove excluding last tile.
        for tile in line_tiles[1:-1]:
            if tile in wall_tiles:
                return False
        return True

    # ----------------------
    # Update loop
    # ----------------------
    def update(self, player_pos, walls):
        player_x, player_y = player_pos
        dist = self.calculate_distance(self.x, self.y, player_x, player_y)
        has_los = self.has_line_of_sight(player_pos, walls)

        # State transitions (now require LoS for detection)
        if self.state == "patrol":
            if dist < ENEMY_CHASE_DISTANCE and has_los:
                self.state = "chase"
                self.last_player_grid_x = int(player_x / TILE_SIZE)
                self.last_player_grid_y = int(player_y / TILE_SIZE)
                self.chase_cooldown = 180
                self.stuck_counter = 0

        elif self.state == "chase":
            if dist < ENEMY_CHASE_DISTANCE and has_los:
                self.last_player_grid_x = int(player_x / TILE_SIZE)
                self.last_player_grid_y = int(player_y / TILE_SIZE)
                # refresh cooldown while player visible
                self.chase_cooldown = 180
                self.stuck_counter = 0
            else:
                # if no LoS, reduce cooldown faster (gives up quicker)
                if not has_los:
                    self.chase_cooldown -= 2

                # if far, reduce cooldown faster
                if dist > ENEMY_LOSE_DISTANCE:
                    self.chase_cooldown -= 2

            # transition to return when cooldown exhausted or stuck too long
            if self.chase_cooldown <= 0 or self.stuck_counter > 6:
                self.state = "return"
                self.stuck_counter = 0
            elif self.chase_cooldown > 0:
                self.chase_cooldown -= 1

        elif self.state == "return":
            if self.grid_x == self.start_x and self.grid_y == self.start_y:
                self.state = "patrol"
                self.stuck_counter = 0

        # Movement handling (grid-based with smooth interpolation)
        if self.is_moving:
            self._move_towards_target()
            if self._reached_target():
                # commit arrival
                self.is_moving = False
                self.x = self.target_x
                self.y = self.target_y
                # remember visited
                self.visited_tiles[(self.grid_x, self.grid_y)] += 1
        else:
            self.move_timer += 1
            if self.move_timer >= self.move_delay:
                self.move_timer = 0
                moved = self._try_move(walls)
                if not moved:
                    self.stuck_counter += 1

    # ----------------------
    # Movement decisions
    # ----------------------
    def _try_move(self, walls):
        dx, dy = 0, 0
        moved = False

        if self.state == "patrol":
            # Smarter patrol: prefer low-visit tiles and avoid immediate reversal
            # Build candidate directions with their resulting tile visit counts
            candidates = []
            for d in ("up", "down", "left", "right"):
                ddx, ddy = self._get_direction_delta(d)
                nx, ny = self.grid_x + ddx, self.grid_y + ddy
                # skip reversing into last_move_direction's opposite (prevent ping-pong)
                if self.last_move_direction:
                    opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
                    if d == opposite.get(self.last_move_direction):
                        continue
                # if tile is free, add with its visit count (default large if blocked so low priority)
                test_rect = pygame.Rect(
                    nx * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
                    ny * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
                    self.size, self.size
                )
                blocked = any(test_rect.colliderect(w) for w in walls)
                if not blocked:
                    candidates.append((self.visited_tiles.get((nx, ny), 0), d))

            # If no candidates (surrounded/blocked), allow reversing as last resort
            if not candidates:
                # pick any direction that is not blocked
                dirs = ["up", "down", "left", "right"]
                random.shuffle(dirs)
                for d in dirs:
                    ddx, ddy = self._get_direction_delta(d)
                    if self._attempt_move(ddx, ddy, walls):
                        self.patrol_direction = d
                        self.last_move_direction = d
                        return True
                return False

            # choose least visited candidate; occasionally randomize to avoid deterministic loops
            candidates.sort(key=lambda t: (t[0], random.random()))
            chosen_dir = candidates[0][1]
            self.patrol_direction = chosen_dir

            ddx, ddy = self._get_direction_delta(self.patrol_direction)
            moved = self._attempt_move(ddx, ddy, walls)
            if moved:
                self.last_move_direction = self.patrol_direction
                self.stuck_counter = 0
            else:
                # fallback: try random available directions (respects last_move_direction avoid)
                dirs = ["up", "down", "left", "right"]
                random.shuffle(dirs)
                for d in dirs:
                    ddx, ddy = self._get_direction_delta(d)
                    if d == ({"up":"down","down":"up","left":"right","right":"left"}.get(self.last_move_direction)):
                        continue
                    if self._attempt_move(ddx, ddy, walls):
                        self.patrol_direction = d
                        self.last_move_direction = d
                        moved = True
                        break

        elif self.state == "chase":
            if self.last_player_grid_x is not None:
                dx_to_player = self.last_player_grid_x - self.grid_x
                dy_to_player = self.last_player_grid_y - self.grid_y

                # Try primary greedy direction first
                if abs(dx_to_player) >= abs(dy_to_player):
                    dx = 1 if dx_to_player > 0 else -1 if dx_to_player < 0 else 0
                    dy = 0
                else:
                    dx = 0
                    dy = 1 if dy_to_player > 0 else -1 if dy_to_player < 0 else 0

                moved = self._attempt_move(dx, dy, walls)

                # Try perpendicular if blocked (prefer keeping progress)
                if not moved:
                    if dx != 0:
                        alt_dy = 1 if dy_to_player > 0 else -1 if dy_to_player < 0 else random.choice([-1, 1])
                        moved = self._attempt_move(0, alt_dy, walls)
                    elif dy != 0:
                        alt_dx = 1 if dx_to_player > 0 else -1 if dx_to_player < 0 else random.choice([-1, 1])
                        moved = self._attempt_move(alt_dx, 0, walls)

                # Try any free direction as last resort (to avoid getting stuck)
                if not moved:
                    for test_dx, test_dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        if self._attempt_move(test_dx, test_dy, walls):
                            moved = True
                            break

                if moved:
                    # remember last move (prevents quick reversal during chase)
                    if dx != 0 or dy != 0:
                        if dx == 1:
                            self.last_move_direction = "right"
                        elif dx == -1:
                            self.last_move_direction = "left"
                        elif dy == 1:
                            self.last_move_direction = "down"
                        elif dy == -1:
                            self.last_move_direction = "up"

        elif self.state == "return":
            dx_to_start = self.start_x - self.grid_x
            dy_to_start = self.start_y - self.grid_y

            if abs(dx_to_start) >= abs(dy_to_start):
                dx = 1 if dx_to_start > 0 else -1 if dx_to_start < 0 else 0
                dy = 0
            else:
                dx = 0
                dy = 1 if dy_to_start > 0 else -1 if dy_to_start < 0 else 0

            moved = self._attempt_move(dx, dy, walls)

            # Try alternate perpendicular if blocked
            if not moved:
                if dx != 0:
                    alt_dy = 1 if dy_to_start > 0 else -1 if dy_to_start < 0 else random.choice([-1, 1])
                    moved = self._attempt_move(0, alt_dy, walls)
                elif dy != 0:
                    alt_dx = 1 if dx_to_start > 0 else -1 if dx_to_start < 0 else random.choice([-1, 1])
                    moved = self._attempt_move(alt_dx, 0, walls)

            # last resort: try any direction to get un-stuck
            if not moved:
                for test_dx, test_dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    if self._attempt_move(test_dx, test_dy, walls):
                        moved = True
                        break

        return moved

    # ----------------------
    # Low-level helpers
    # ----------------------
    def _get_direction_delta(self, direction):
        if direction == "up":
            return 0, -1
        elif direction == "down":
            return 0, 1
        elif direction == "left":
            return -1, 0
        elif direction == "right":
            return 1, 0
        return 0, 0

    def _attempt_move(self, dx, dy, walls):
        if dx == 0 and dy == 0:
            return False

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        test_rect = pygame.Rect(
            new_x * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
            new_y * TILE_SIZE + TILE_SIZE // 2 - self.size // 2,
            self.size, self.size
        )

        # collision check against walls
        if not any(test_rect.colliderect(wall) for wall in walls):
            # commit move
            self.target_x = new_x * TILE_SIZE + TILE_SIZE // 2
            self.target_y = new_y * TILE_SIZE + TILE_SIZE // 2
            self.grid_x = new_x
            self.grid_y = new_y
            self.is_moving = True
            self.stuck_counter = 0
            # record visit (will increment again on arrival)
            self.visited_tiles[(new_x, new_y)] += 0  # ensure key exists
            return True
        return False

    def _move_towards_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if abs(dx) > self.speed:
            self.x += self.speed if dx > 0 else -self.speed
        else:
            self.x = self.target_x

        if abs(dy) > self.speed:
            self.y += self.speed if dy > 0 else -self.speed
        else:
            self.y = self.target_y

    def _reached_target(self):
        return self.x == self.target_x and self.y == self.target_y

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size, self.size
        )

    def draw(self, screen):
        if self.use_image and self.image:
            screen.blit(self.image, (self.x - self.size // 2, self.y - self.size // 2))
        else:
            if self.state == "chase":
                color = (255, 50, 50)
            elif self.state == "return":
                color = (255, 150, 150)
            else:
                color = self.color

            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)

            eye_offset = self.size // 6
            eye_size = self.size // 10
            pygame.draw.circle(screen, (255, 255, 0),
                               (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
            pygame.draw.circle(screen, (255, 255, 0),
                               (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)

    def reset(self):
        self.grid_x = self.start_x
        self.grid_y = self.start_y
        self.x = self.start_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_y * TILE_SIZE + TILE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        self.state = "patrol"
        self.move_timer = 0
        self.chase_cooldown = 0
        self.stuck_counter = 0
        self.visited_tiles.clear()
        self.visited_tiles[(self.grid_x, self.grid_y)] = 1
        self.last_move_direction = None
