from ursina import *

KEY_ACTIONS = {
    "pan_left": {"camera_position": (1, 0, 0)},
    "pan_right": {"camera_position": (-1, 0, 0)},
    "pan_down": {"camera_position": (0, -1, 0)},
    "pan_up": {"camera_position": (0, 1, 0)},
    "zoom_out": {"camera_position": (0, -1, -1)},
    "zoom_in": {"camera_position": (0, 1, 1)},
    "rotate_left": {"map_rotation": (0, 0, 1)},
    "rotate_right": {"map_rotation": (0, 0, -1)},
}

game_map = None


class GameMap(Entity):
    def __init__(self, **kwargs):
        self.size_x = kwargs.get("size_x", 16)
        self.size_y = kwargs.get("size_y", 16)
        # start_pos = (-10, 28, 6) # Magic numbers are bad
        start_pos = (0, 0, 0)
        start_rot = (0, 0, 45)
        self.control = Entity(
            position=start_pos,
            rotation=start_rot,
        )
        self.floor = [[] * self.size_y] * self.size_x
        self.grid = [[] * self.size_y] * self.size_x
        self.walls = []
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                self.grid[x].append(
                    Entity(
                        parent=self.control,
                        model="quad",
                        texture="white_cube",
                        color=color.rgba(255, 255, 255, 128),
                        position=(x, y, -0.01),
                    )
                )
                self.floor[x].append(
                    Entity(
                        parent=self.control,
                        model="quad",
                        texture="grass",
                        position=(x, y, 0),
                    )
                )
                if x == 0 or y == 0 or x == self.size_x - 1 or y == self.size_y - 1:
                    self.walls.append(
                        Entity(
                            parent=self.control,
                            model="cube",
                            position=(x, y, 0),
                            texture="brick",
                            # color=color.rgba(255, 255, 255, 128)
                        )
                    )
                    self.walls.append(
                        Entity(
                            parent=self.control,
                            model="cube",
                            position=(x, y, -1),
                            texture="brick",
                            # color=color.rgba(255, 255, 255, 128)
                        )
                    )


def update():
    pos_rate = 4
    rot_rate = pos_rate * 6
    keys = {
        "a": KEY_ACTIONS["pan_left"],
        "d": KEY_ACTIONS["pan_right"],
        "s": KEY_ACTIONS["pan_down"],
        "w": KEY_ACTIONS["pan_up"],
        "e": KEY_ACTIONS["zoom_out"],
        "q": KEY_ACTIONS["zoom_in"],
        "z": KEY_ACTIONS["rotate_left"],
        "c": KEY_ACTIONS["rotate_right"],
    }
    for key in keys:
        if held_keys[key]:
            try:
                pos = [x * time.dt * pos_rate for x in keys[key]["camera_position"]]
                camera.position += pos
                print(camera.position)
            except KeyError:
                pass
            try:
                rot = [x * time.dt * rot_rate for x in keys[key]["map_rotation"]]
                game_map.control.rotation += rot
            except KeyError:
                pass


def main():
    global game_map
    app = Ursina()
    camera.rotation_x = -45
    camera.position += (10, -28, -6)
    game_map = GameMap()
    app.run()


if __name__ == "__main__":
    main()
