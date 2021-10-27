#!/usr/bin/env python3

import random

from creatures import Creature
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

DEFAULT_GRID_COLOR = color.rgba(255, 255, 255, 128)
ENEMY_GRID_COLOR = color.rgba(255, 0, 0, 128)
FRIEND_GRID_COLOR = color.rgba(0, 255, 0, 128)
NEUTRAL_GRID_COLOR = color.rgba(255, 255, 0, 192)

DEFAULT_CAMERA_POS = (5.5, -36, -36)
DEFAULT_CAMERA_ROT = (-45, 0, 0)

game_map = None
ui = None
update_interval = 1.2  # How many seconds to wait before for refreshing the map
update_time = 0.0
player = Creature(factions=["Player"])


class MapBlock:
    def __init__(self, **kwargs):
        self.map = kwargs.get("map")
        self.indices = kwargs.get("indices")
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.type = kwargs.get("type")  # TODO: Rename this
        self.parent = kwargs.get("parent")
        self.grid_color = DEFAULT_GRID_COLOR
        self.entities = {
            "Terrain": Entity(parent=self.parent),
            "Grid": Entity(parent=self.parent),
            "Object": Entity(parent=self.parent),
        }
        self.grid_blink_action = None
        self.occupant = None
        if self.type is not None:
            self.update_terrain()

    def _click(self):
        self.map._click(self)

    def blink_grid(self, **kwargs):
        self.grid_blink_action = self.entities["Grid"].blink(
            value=kwargs.get("value", self.grid_color + color.rgba(0, 0, 0, 128)),
            duration=1.2,
            loop=kwargs.get("loop", True),
            interrupt="finish",
            curve=curve.linear_boomerang,
        )

    def remove_occupant(self):
        occupant = self.occupant
        self.entities["Object"].model = None
        self.grid_color = DEFAULT_GRID_COLOR
        self.occupant = None
        return occupant

    def update_terrain(self):
        if self.type == "wall":
            self.entities["Grid"].model = None
            self.entities["Terrain"].model = "cube"
            self.entities["Terrain"].texture = "brick"
            self.entities["Terrain"].position = (self.x, self.y, -0.5)

        elif self.type == "floor":
            self.entities["Grid"].model = "quad"
            self.entities["Grid"].texture = "white_cube"
            self.entities["Grid"].color = self.grid_color
            self.entities["Grid"].collider = "box"
            self.entities["Grid"].on_click = self._click
            self.entities["Grid"].position = (self.x, self.y, -0.01)
            if self.grid_blink_action:
                self.grid_blink_action.kill()
                self.grid_blink_action = None

            self.entities["Terrain"].model = "quad"
            self.entities["Terrain"].texture = "grass"
            self.entities["Terrain"].color = color.white
            self.entities["Terrain"].position = (self.x, self.y, 0)

        if self.occupant:
            obj_color = color.white
            if self.occupant is player:
                obj_color = color.blue
                self.grid_color = FRIEND_GRID_COLOR
            elif player.is_enemy(self.occupant):
                obj_color = color.red
                self.grid_color = ENEMY_GRID_COLOR
            elif player.is_friend(self.occupant):
                obj_color = color.green
                self.grid_color = FRIEND_GRID_COLOR
            else:
                obj_color = color.white
                self.grid_color = NEUTRAL_GRID_COLOR
            self.entities["Object"].parent = self.parent
            self.entities["Object"].model = "scale_gizmo"
            self.entities["Object"].texture = "white_cube"
            self.entities["Object"].color = obj_color
            self.entities["Object"].position = (self.x, self.y, -0.5)
            self.entities["Object"].rotation = (0, 180, 0)
        else:
            self.entities["Object"].model = None
            self.grid_color = DEFAULT_GRID_COLOR


class GameMap(Entity):
    def __init__(self, **kwargs):
        self.size_x = kwargs.get("size_x", 16)
        self.size_y = kwargs.get("size_y", 16)
        start_pos = (0, 0, 0)
        start_rot = (0, 0, 45)
        self.player_block = None
        # Parent of all other Entities. Also used to rotate the map.
        self.control = Entity(
            position=start_pos,
            rotation=start_rot,
        )
        self.map_blocks = [
            [
                MapBlock(
                    map=self,
                    indices=(x, y),
                    x=x - self.size_x / 2,
                    y=y - self.size_y / 2,
                    parent=self.control,
                )
                for y in range(self.size_y)
            ]
            for x in range(self.size_x)
        ]
        self.generate_map()
        self.update_map()

    def _click(self, block):
        MODE = "move"
        if MODE == "move":
            if block in self.player_adjacent_blocks(occupied=False):
                self.move_player(block)
                self.update_map()
            elif block in self.player_adjacent_blocks():
                if player.is_enemy(block.occupant):
                    print("Slain an enemy!")
                    block.remove_occupant()
                else:
                    print("Can't move: Occupied.")
            else:
                print("Can't move: Too far.")

    def move_player(self, block, ignore=False):
        try:
            self.player_block.remove_occupant()
        except AttributeError:
            if not ignore:
                raise
        block.occupant = player
        self.player_block = block

    def generate_map(self):
        player_position = (int(self.size_x / 2), int(self.size_y / 2))
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                if x == 0 or y == 0 or x == self.size_x - 1 or y == self.size_y - 1:
                    self.map_blocks[x][y].type = "wall"
                else:
                    self.map_blocks[x][y].type = "floor"
                    if (x, y) == player_position:
                        self.move_player(self.map_blocks[x][y], ignore=True)
                    elif random.randint(0, 100) > 70:
                        creature = Creature(
                            factions=[random.choice(["Enemy", "Neutral"])]
                        )
                        self.map_blocks[x][y].occupant = creature

    def update_map(self):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                self.map_blocks[x][y].update_terrain()
        for block in self.player_adjacent_blocks():
            block.blink_grid()

    def player_adjacent_blocks(self, occupied=True):
        blocks = []
        px, py = self.player_block.indices
        for x in range(px - 1, px + 2):
            for y in range(py - 1, py + 2):
                if occupied is False and self.map_blocks[x][y].occupant is not None:
                    continue
                blocks.append(self.map_blocks[x][y])
        return blocks


def update():
    global game_map
    global update_interval
    global update_time
    pos_rate = 4
    rot_rate = pos_rate * 6
    keys = {
        "a": KEY_ACTIONS["pan_left"],
        "d": KEY_ACTIONS["pan_right"],
        "s": KEY_ACTIONS["pan_down"],
        "w": KEY_ACTIONS["pan_up"],
        "e": KEY_ACTIONS["zoom_out"],
        Keys.scroll_down: KEY_ACTIONS["zoom_out"],
        "q": KEY_ACTIONS["zoom_in"],
        Keys.scroll_up: KEY_ACTIONS["zoom_in"],
        "z": KEY_ACTIONS["rotate_left"],
        "c": KEY_ACTIONS["rotate_right"],
    }
    # update_time += time.dt
    # if update_time >= update_interval:
    #    game_map.update_map()
    #    update_time = 0
    for key in keys:
        if held_keys[key]:
            try:
                pos = [x * time.dt * pos_rate for x in keys[key]["camera_position"]]
                camera.position += pos
            except KeyError:
                pass
            try:
                rot = [x * time.dt * rot_rate for x in keys[key]["map_rotation"]]
                game_map.control.rotation += rot
            except KeyError:
                pass


class UI:
    def __init__(self):
        scale = (0.5, 0.9)
        text_scale = (1/(scale[0]), 1/scale[1])
        self.background = Entity(
            parent=camera.ui,
            model="quad",
            position=(0.5, 0.0),
            scale=(0.5, 0.9),
            color=color.rgba(192, 192, 192, 128)
        )
        self.text = Text(
            origin=(2.25,-16),
            parent=self.background,
            text="Foobar",
            scale=text_scale,
        )


def main():
    global game_map
    app = Ursina(position=(0, 0))
    camera.position = DEFAULT_CAMERA_POS
    camera.rotation = DEFAULT_CAMERA_ROT
    game_map = GameMap()
    ui = UI()
    game_map.update_map()
    app.run()


if __name__ == "__main__":
    main()
