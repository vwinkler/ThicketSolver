import argparse


def neg(variableIndex):
    return -variableIndex


def printSoftClause(weight, literals):
    print("{} {} 0".format(weight, " ".join([str(literal) for literal in literals])))


def printHardClause(literals):
    printSoftClause(5, literals)


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


class TileCoordinates:
    def __init__(self, x, y):
        assert (x >= 0 or y >= 0)
        self.x = x
        self.y = y

    def __add__(self, other):
        return TileCoordinates(self.x + other.x, self.y + other.y)


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.currentVariableIndex = self.lastTileVariableIndex() + 1
        self.clauses = []

    def calcVariableIndexOfTile(self, tile):
        return self.width * tile.y + tile.x + 1

    def lastTileVariableIndex(self):
        return self.calcVariableIndexOfTile(TileCoordinates(self.width - 1, self.height - 1))

    def water(self, tile):
        return self.calcVariableIndexOfTile(tile)

    def thicket(self, tile):
        return -self.calcVariableIndexOfTile(tile)

    def tileExists(self, tile):
        return 0 <= tile.x < self.width and 0 <= tile.y < self.height

    def tileHasNeighbor(self, tile, direction):
        return self.tileExists(tile + direction)

    def makeVariable(self):
        var = self.currentVariableIndex
        self.currentVariableIndex += 1
        return var

    def addHardClause(self, literals):
        assert all([literal != 0 for literal in literals])
        self.addSoftClause(None, literals)

    def addSoftClause(self, weight, literals):
        assert all([literal != 0 for literal in literals])
        assert weight == None or weight >= 0
        self.clauses.append((weight, literals))

    def addNoBranchConstraintForTile(self, tile, direction):
        tiles = [tile + direction, tile + rotateCounterclockwise(direction), tile + rotateClockwise(direction)]
        if all([self.tileExists(tile) for tile in tiles]):
            self.addHardClause([neg(self.water(tile))] + [self.thicket(v) for v in tiles])

    def addNoBranchConstraintsForTile(self, tile):
        for direction in directions:
            if self.tileHasNeighbor(tile, direction):
                self.addNoBranchConstraintForTile(tile, direction)

    def addNoThreeOrMoreThicketsAroundRiverConstraintForTile(self, tile, direction):
        tiles = [tile + rotateCounterclockwise(direction),
                 tile + rotateCounterclockwise(rotateCounterclockwise(direction)),
                 tile + rotateClockwise(direction)]
        if all([self.tileExists(tile) for tile in tiles]):
            self.addHardClause([neg(self.water(tile))] + [self.water(v) for v in tiles])

    def addNoThreeOrMoreThicketsAroundRiverConstraintsForTile(self, tile):
        for direction in directions:
            self.addNoThreeOrMoreThicketsAroundRiverConstraintForTile(tile, direction)

    def addNoInnerSourcesOrDrainsConstraintForTile(self, tile):
        self.addNoThreeOrMoreThicketsAroundRiverConstraintsForTile(tile)

    def addThicketNextToRiverGoalForTile(self, tile, direction):
        var = self.makeVariable()
        self.addHardClause([neg(var), self.thicket(tile)])
        self.addHardClause([neg(var), self.water(tile + direction)])
        self.addSoftClause(4, [var])
        # ToDo: consider adding reverse implication

    def addThicketNextToRiverGoalsForTile(self, tile):
        for direction in directions:
            if self.tileHasNeighbor(tile, direction):
                self.addThicketNextToRiverGoalForTile(tile, direction)

    def addNoThicketNextToRiverGoalForTile(self, tile):
        var = self.makeVariable()
        self.addHardClause([neg(var), self.thicket(tile)])
        for direction in directions:
            if self.tileHasNeighbor(tile, direction):
                self.addHardClause([neg(var), self.thicket(tile + direction)])
        self.addSoftClause(2, [var])
        # ToDo: consider adding reverse implication

    def addVariableImpliesTileIsRiverEndConstraint(self, tile, variable):
        self.addHardClause([self.water(tile), neg(variable)])
        for i in range(len(directions)):
            for j in range(i + 1, len(directions)):
                tile1 = tile + directions[i]
                tile2 = tile + directions[j]
                if self.tileExists(tile1) and self.tileExists(tile2):
                    self.addHardClause([self.thicket(tile1), self.thicket(tile2), neg(variable)])

    def addTileIsRiverEndInDirectionImpliesVariableConstraint(self, tile, direction, variable):
        tiles = [tile + rotateCounterclockwise(direction),
                 tile + rotateCounterclockwise(rotateCounterclockwise(direction)),
                 tile + rotateClockwise(direction)]
        existingTiles = [tile for tile in tiles if self.tileExists(tile)]
        self.addHardClause([self.water(tile) for tile in existingTiles] + [self.thicket(tile), variable])

    def addTileIsRiverEndImpliesVariableConstraint(self, tile, variable):
        for direction in directions:
            if self.tileHasNeighbor(tile, direction):
                self.addTileIsRiverEndInDirectionImpliesVariableConstraint(tile, direction, variable)

    def addExactlyTwoTrueVariablesInSelectionConstraint(self, variables):
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                for k in range(j + 1, len(variables)):
                    self.addHardClause([neg(variables[i]), neg(variables[j]), neg(variables[k])])
        for i in range(len(variables)):
            self.addHardClause([variable for (l, variable) in enumerate(variables) if l != i])

    def addOneRiverConstraint(self):
        variables = []
        for y in range(self.height):
            for x in range(self.width):
                if x in {0, self.width - 1} or y in {0, self.height - 1}:
                    tile = TileCoordinates(x, y)
                    variable = self.makeVariable()
                    self.addVariableImpliesTileIsRiverEndConstraint(tile, variable)
                    self.addTileIsRiverEndImpliesVariableConstraint(tile, variable)
                    variables.append(variable)
        self.addExactlyTwoTrueVariablesInSelectionConstraint(variables)

    def sumSoftClauseWeights(self):
        return sum([weight for (weight, _) in self.clauses if weight])

    def printInstanceInfo(self, top):
        print("p wcnf {} {} {}".format(self.currentVariableIndex, len(self.clauses), top))

    def printClauses(self, top):
        for (weight, literals) in self.clauses:
            if not weight:
                weight = top
            printSoftClause(weight, literals)

    def generateClauses(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = TileCoordinates(x, y)
                self.addNoBranchConstraintsForTile(tile)
                self.addNoInnerSourcesOrDrainsConstraintForTile(tile)
                self.addThicketNextToRiverGoalsForTile(tile)
                self.addNoThicketNextToRiverGoalForTile(tile)
        self.addOneRiverConstraint()

    def printMaxSatFormula(self):
        self.generateClauses()
        top = self.sumSoftClauseWeights() + 10
        self.printInstanceInfo(top)
        self.printClauses(top)


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
    print(commentsTemplate.format(field.width, field.height, field.calcVariableIndexOfTile(TileCoordinates(0, 0)),
                                  field.lastTileVariableIndex()))


parser = argparse.ArgumentParser()
parser.add_argument('--width', dest='width', type=int, default=5)
parser.add_argument('--height', dest='height', type=int, default=12)
args = parser.parse_args()

field = Field(args.width, args.height)
printComments(field)
field.printMaxSatFormula()
