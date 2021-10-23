from ursina import *


game_map = None


class GameMap(Entity):
    def __init__(self, **kwargs):
        self.size_x = kwargs.get("size_x", 16)
        self.size_y = kwargs.get("size_y", 16)
        super().__init__(
            model="quad",
            position=(0, 19, -15),  # Hard coding this seems lame
            rotation=(0, 0, 45),
            scale=(10, 10),
            texture="white_cube",
            texture_scale=(self.size_x, self.size_y),
            color=color.dark_gray,
        )


def update():
    pos_rate = 4
    rot_rate = pos_rate * 6
    keys = {
        "a": {"camera_position": (time.dt * pos_rate, 0, 0)},
        "d": {"camera_position": (time.dt * -pos_rate, 0, 0)},
        "s": {"camera_position": (0, time.dt * -pos_rate, 0)},
        "w": {"camera_position": (0, time.dt * pos_rate, 0)},
        # Zoom out
        "e": {"camera_position": (0, time.dt * -pos_rate, time.dt * -pos_rate)},
        # Zoom in
        "q": {"camera_position": (0, time.dt * pos_rate, time.dt * pos_rate)},
        "z": {"map_rotation": (0, 0, time.dt * rot_rate)},
        "c": {"map_rotation": (0, 0, time.dt * -rot_rate)},
    }
    for key in keys:
        if held_keys[key]:
            try:
                camera.position += keys[key]["camera_position"]
            except KeyError:
                pass
            try:
                game_map.rotation += keys[key]["map_rotation"]
            except KeyError:
                pass


def main():
    global game_map
    camera.rotation_x = -80
    app = Ursina()
    game_map = GameMap()
    app.run()


if __name__ == "__main__":
    main()
