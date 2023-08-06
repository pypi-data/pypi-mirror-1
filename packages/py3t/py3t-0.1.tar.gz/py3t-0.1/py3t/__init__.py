class Player(object):
    def __init__(self, field, side="X", name=None):
        self.field = field
        self.side = side
        self.name = name

    def __str__(self):
        if self.name:
            return self.name
        return super(Player, self).__str__()

    def play_once(self):
        raise NotImplementedError()

    def play(self, (x, y)):
        self.field[y][x] = self.side

    def victorious(self):
        for line in self.field.lines():
            for (x, y) in line:
                if self.field[y][x] != self.side:
                    break
            else:
                return True
        else:
            return False

class Field(list):
    def __init__(self):
        super(Field, self).__init__([
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ])

    def lines(self):
        return (
            # Horizontal lines
            ((0, 0), (1, 0), (2, 0)), # Y 0
            ((0, 1), (1, 1), (2, 1)), # Y 1
            ((0, 2), (1, 2), (2, 2)), # Y 2
            # Diagonal lines
            ((0, 0), (1, 1), (2, 2)),
            ((2, 0), (1, 1), (0, 2)),
            # Vertical lines
            ((0, 0), (0, 1), (0, 2)), # X 0
            ((1, 0), (1, 1), (1, 2)), # X 1
            ((2, 0), (2, 1), (2, 2)), # X 2
        )

    def cells(self):
        for y in (0, 1, 2):
            for x in (0, 1, 2):
                yield (x, y)

    def clear(self):
        self[:] = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

    def __str__(self):
        r = ""
        for row in self:
            for cell in row:
                r += str(cell or "N") + " "
            r += "\n"
        return r.strip()
