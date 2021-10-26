#!/usr/bin/env python3


FACTIONS = {
    "Player": {
        "Enemy": -1000,
    },
    "Enemy": {
        "Player": -1000,
    },
    "Neutral": {},
}

class Creature():
    def __init__(self, **kwargs):
        self.factions = kwargs.get("factions", ["Neutral"])

    def is_enemy(self, creature):
        for my_faction in self.factions:
            for their_faction in creature.factions:
                try:
                    if FACTIONS[my_faction][their_faction] <= -100:
                        return True
                except KeyError:
                    pass
        return False

    def is_friend(self, creature):
        if self.is_enemy(creature):
            return False
        for my_faction in self.factions:
            for their_faction in creature.factions:
                if their_faction == my_faction:
                    return True
                try:
                    if FACTIONS[my_faction][their_faction] >- 100:
                        return True
                except KeyError:
                    pass
        return False
