#!/usr/bin/env python3

import random

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


class MapBlock:
    def __init__(self, **kwargs):
        self.map = kwargs.get("map")
        self.indices = kwargs.get("indices")
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.type = kwargs.get("type")  # TODO: Rename this
        self.parent = kwargs.get("parent")
        self.grid_color = color.rgba(255, 255, 255, 128)
        self.entities = {
            "Terrain": Entity(parent=self.parent),
            "Grid": Entity(parent=self.parent),
            "Object": Entity(parent=self.parent),
        }
        self.action = None
        self.occupant = None
        if self.type is not None:
            self.update_terrain()

    def _click(self):
        self.map._click(self)

    def _debug_info(self):
        print(f"{self.x},{self.y}")

    def add_obj(self, obj="enemy"):
        self.occupant = obj
        self.obj_color = color.white
        if obj == "player":
            self.obj_color = color.blue
            self.grid_color = color.rgba(0, 255, 0, 128)
        elif obj == "enemy":
            self.obj_color = color.red
            self.grid_color = color.rgba(255, 0, 0, 128)

    def blink_grid(self, **kwargs):
        self.action = self.entities["Grid"].blink(
            value=kwargs.get("value", self.grid_color + color.rgba(0, 0, 0, 128)),
            duration=1.2,
            loop=kwargs.get("loop", True),
            interrupt="finish",
            curve=curve.linear_boomerang,
        )

    def blink_grid(self, **kwargs):
        self.action = self.entities["Grid"].blink(
            value=kwargs.get("value", self.grid_color + color.rgba(0, 0, 0, 128)),
            duration=1.2,
            loop=kwargs.get("loop", True),
            curve=curve.linear_boomerang,
        )

    def clear(self, entity=None):
        entities = self.entities
        if entity:
            entities = [entity]
        for entity in entities:
            try:
                self.entities[entity].disable()
            except AttributeError:
                pass
            try:
                self.entities[entity].pause()
            except AttributeError:
                pass
            try:
                destroy(self.entities[entity])
            except AttributeError:
                pass
            del self.entities[entity]
            if entity == "Object":
                self.occupant = None

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
            if self.action:
                self.action.finish()
                self.action = None

            self.entities["Terrain"].model = "quad"
            self.entities["Terrain"].texture = "grass"
            self.entities["Terrain"].color = color.white
            self.entities["Terrain"].position = (self.x, self.y, 0)

        if self.occupant:
            self.entities["Object"].parent = self.parent
            self.entities["Object"].model = "scale_gizmo"
            self.entities["Object"].texture = "white_cube"
            self.entities["Object"].color = self.obj_color
            self.entities["Object"].position = (self.x, self.y, -0.5)
            self.entities["Object"].rotation = (0, 180, 0)
        else:
            self.entities["Object"].model = None


class GameMap(Entity):
    def __init__(self, **kwargs):
        self.size_x = kwargs.get("size_x", 16)
        self.size_y = kwargs.get("size_y", 16)
        start_pos = (0, 0, 0)
        start_rot = (0, 0, 45)
        self.player_block = None
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
                print("CAN MOVE!")
                self.move_player(block)
                self.update_map()
            elif block in self.player_adjacent_blocks():
                print("Can't move: Occupied.")
            else:
                print("Can't move: Too far.")

    def move_player(self, block):
        self.player_block.occupant = None
        print(f"{self.player_block.x},{self.player_block.y} -> {block.x},{block.y}")
        block.add_obj(obj="player")
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
                        self.map_blocks[x][y].add_obj(obj="player")
                        self.player_block = self.map_blocks[x][y]
                    elif random.randint(0, 100) > 70:
                        self.map_blocks[x][y].add_obj(obj="enemy")
                self.map_blocks[x][y].update_terrain()

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


def main():
    global game_map
    app = Ursina()
    camera.rotation_x = -45
    camera.position += (0, -28, -6)
    game_map = GameMap()
    app.run()


if __name__ == "__main__":
    main()
