"""AI!"""

import operator
import random
from py3t import Field, Player

# AI workflow:
#  1. Look for possible win condition
#  2. Look for possible loss condition
#  3. Look for possible fork condition
#  4. Look for opposing fork condition
#      4.1. Place such that the opponent cannot create a fork or win, or place
#           two in a row where the third cell is empty.
#  5. Play the center.
#  6. Play opposing corner.
#  7. Play empty corner.
#  8. Play empty side.

class Priomap(Field):
    cell_placement_priomap = (
        (2, 1, 2),
        (1, 3, 1),
        (2, 1, 2),
    )

    def __init__(self, side, field):
        super(Priomap, self).__init__()
        self.side = side
        self.field = field
        self.reassess()

    @staticmethod
    def choose_by_priority(((x, y), prio)):
        return prio

    @staticmethod
    def best_prio_cells(prios):
        best = {}
        for coord, prio in prios:
            best.setdefault(prio, []).append(coord)
        max_prio = max(best)
        return best[max(best)]

    def reassess(self):
        self.clear()
        # Analyze all possible lines, counting own and foe cells.
        # If there is a foe cell in a line, it cannot be won.
        # If there are two foe cells in a line, it is a possible defeat.
        # If there is only a own cell, it can be won.
        # If there are only two cells, it is a possible victory.
        for line in self.field.lines():
            # First we need to calculate the counts on the whole line.
            lineprio = 0, 0
            for (x, y) in line:
                cell = self.field[y][x] 
                n_own, n_foe = 0, 0
                if cell == self.side:
                    n_own = 1
                elif cell:
                    n_foe = 1
                lineprio = map(operator.add, lineprio, (n_own, n_foe))
            # When we've calculated a line, update the map accordingly.
            for (x, y) in line:
                # It is only relevant to update cells which aren't taken.
                if self.field[y][x]:
                    continue
                n_own, n_foe = lineprio
                # Now the hairy part: calculating priority.
                # We accumulate it, as a cell may participate in many lines.
                prio = self[y][x] or 0
                # If the sum of the line counts is three, we know this line is
                # full and thus the counts don't matter in terms of priority.
                if n_own + n_foe == 3:
                    continue
                # If there are own cells and no foe cells, the priority is the
                # count of own cells.
                elif not n_foe:
                    prio += n_own
                # If there are foe cells and no own cells, the priority is the
                # count of foe cells.
                elif not n_own:
                    prio += n_foe
                self[y][x] = prio
        return self

    def get_best_cell(self):
        # Find the best cells, and play one of them This is achieved through
        # making a flat list out of all cells and their priority, then sorting
        # by the priority.
        flat_prios = []
        for (x, y) in self.field.cells():
            flat_prios.append(((x, y), self[y][x]))
        flat_prios.sort(key=self.choose_by_priority, reverse=True)
        # Now that the list is sorted, we need to find out if more than one cell
        # is up for playing.
        playable = []
        max_prio = None
        for coord, prio in flat_prios:
            if max_prio is None:
                max_prio = prio
            elif prio < max_prio:
                break
            playable.append(coord)
        print "Considering", playable
        (best_cell_x, best_cell_y) = self.equal_cell_choice(playable)
        print "Chose", (best_cell_x, best_cell_y), "with priority", max_prio
        return (best_cell_x, best_cell_y)

    def equal_cell_choice(self, choices):
        """Choose a cell based on the following static priority map::

            2 1 2
            1 3 1
            2 1 2
        """
        prios = []
        for (y, row) in enumerate(self.cell_placement_priomap):
            for (x, prio) in enumerate(row):
                if (x, y) in choices:
                    prios.append(((x, y), prio))
        prios.sort(key=self.choose_by_priority, reverse=True)
        best_cells = self.best_prio_cells(prios)
        print "Reconsidering", best_cells
        return random.choice(best_cells)

class Computer(Player):
    def __init__(self, field, side="O", **kwargs):
        super(Computer, self).__init__(field, side=side, **kwargs)
        self.priomap = Priomap(side, field)

    def play_once(self):
        self.priomap.reassess()
        (x, y) = self.priomap.get_best_cell()
        self.play((x, y))
