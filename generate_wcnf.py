import argparse


class TileDirection:
    def __init__(self, x, y):
        assert (abs(x) == 1 or abs(y) == 1)
        assert (x == 0 or y == 0)
        self.x = x
        self.y = y


def rotateCounterclockwise(direction):
    return TileDirection(direction.y, -direction.x)


def rotateClockwise(direction):
    return TileDirection(-direction.y, direction.x)


directions = [TileDirection(1, 0), TileDirection(0, -1), TileDirection(-1, 0), TileDirection(0, 1)]


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def calcVariableIndexOfTile(self, x, y):
        return self.width * y + x

    def tileHasNeighbor(self, x, y, direction):
        pass

    def printNoBranchConstraintForTile(self, x, y, direction):
        pass

    def printNoBranchConstraintsForTile(self, x, y):
        for direction in directions:
            if self.tileHasNeighbor(x, y, direction):
                self.printNoBranchConstraintForTile(x, y, direction)

    def printNoInnerSourcesOrDrainsConstraintForTile(self, x, y):
        pass

    def printThicketNextToRiverGoalForTile(self, x, y, direction):
        pass

    def printThicketNextToRiverGoalsForTile(self, x, y):
        for direction in directions:
            if self.tileHasNeighbor(x, y, direction):
                self.printThicketNextToRiverGoalForTile(x, y, direction)

    def printNoThicketNextToRiverGoalForTile(self, x, y):
        pass

    def printMaxSatFormula(self):
        for y in range(self.height):
            for x in range(self.width):
                self.printNoBranchConstraintsForTile(x, y)
                self.printNoInnerSourcesOrDrainsConstraintForTile(x, y)
                self.printThicketNextToRiverGoalsForTile(x, y)
                self.printNoThicketNextToRiverGoalForTile(x, y)


def printComments(field):
    commentsTemplate = """c Problem:
c * Based on this reddit post:
c   https://www.reddit.com/r/AskComputerScience/comments/m4mxgq/is_this_problem_intractable/
c * Given an m x n region, place "thickets" and "rivers" to generate the highest possible score.
c * A thicket which has no rivers above, below, left, or right of it, is worth 2 points.
c * A thicket with 1 adjacency is worth 4 points.
c * A thicket with 2 adjacency is worth 8 points.
c * A thicket with 3 adjacency is worth 12 points.
c * A thicket with full (4) adjacency is worth 16 points.
c * A river must begin on the border of a region and it cannot branch,
c   in other words, you can't ever backtrack on a river.
c
c This is a MaxSAT translation of an instance of the above problem.
c
c Problem instance: {}x{} (width x height)
c
c In this translation false='thicket' and true='river' for variables {}...{}"""
    print(commentsTemplate.format(field.width, field.height, field.calcVariableIndexOfTile(0, 0),
                                  field.calcVariableIndexOfTile(field.width, field.height)))


parser = argparse.ArgumentParser()
parser.add_argument('--width', dest='width', default=5)
parser.add_argument('--height', dest='height', default=12)
args = parser.parse_args()

field = Field(args.width, args.height)
printComments(field)
field.printMaxSatFormula()
