from generation.tilemap import TileType

class RoomTemplates:
    @staticmethod
    def convert(layout):
        mapping = {' ': TileType.EMPTY, 'W': TileType.WALL, 'F': TileType.FLOOR, 'D': TileType.DOOR, 'H': TileType.HAZARD, 'X': TileType.EXIT, 'R': TileType.REWARD}
        return [[mapping.get(ch, TileType.EMPTY) for ch in row] for row in layout]

    @staticmethod
    def arena_room():
        return RoomTemplates.convert([
            "WWWWDWWWWW",
            "WFFFFFFFFW",
            "WFFFFFFFFW",
            "WFFFFFFFFW",
            "DFFFFFFFFD",
            "WFFFFFFFFW",
            "WFFFFFFFFW",
            "WFFFFFFFFW",
            "WWWWDWWWWW",
        ])

    @staticmethod
    def corridor_room():
        return RoomTemplates.convert([
            "WWWWWWWWWWWW",
            "DFFFFFFFFFFD",
            "WWWWWWWWWWWW",
        ])

    @staticmethod
    def crossroads_room():
        return RoomTemplates.convert([
            "WWWWDWWWW",
            "WFFFFFFFW",
            "WFFFFFFFW",
            "DFFFFFFFD",
            "WFFFFFFFW",
            "WFFFFFFFW",
            "WWWWDWWWW",
        ])

    @staticmethod
    def hazard_room():
        return RoomTemplates.convert([
            "WWWWDWWWWW",
            "WFFFFFFFFW",
            "WFFHHHHFFW",
            "WFFHFFHFFW",
            "DFFHFFHFFD",
            "WFFHHHHFFW",
            "WFFFFFFFFW",
            "WWWWDWWWWW",
        ])
