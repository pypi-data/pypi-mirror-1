from itertools import cycle
from py3t import Player, Field
from py3t.ai import Computer

class Human(Player):
    def play_once(self):
        self.play(input("X, Y: "))

def play(players):
    players = cycle(players)
    for t_num in xrange(3 * 3):  # TODO Unhardcode.
        player = players.next()
        print
        print "Turn #%d begins." % (t_num + 1,)
        player.play_once()
        print player.field
        if player.victorious():
            return player

def main():
    field = Field()
    print "Human or Computer."
    p1 = input("P1 X: ")(field, side="X", name="P1")
    p2 = input("P2 O: ")(field, side="O", name="P2")
    winner = play((p1, p2))
    if winner:
        print winner, "wins!"
    else:
        print "Draw."

if __name__ == "__main__": main()
