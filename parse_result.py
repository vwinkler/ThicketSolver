import sys
import argparse
from enum import Enum


class Result(Enum):
    optimumFound = 0
    unsat = 1
    unknown = 2


def parseResultToken(token):
    if token == "OPTIMUM FOUND":
        return Result.optimumFound
    elif token == "UNSAT":
        return Result.unsat
    elif token == "UNKNOWN":
        return Result.unknown
    else:
        raise RuntimeError("could not parse result: 's {}'".format(token))


def parseInput():
    intermediateOptimums = []
    variableAssignments = {}
    for line in sys.stdin:
        tokens = line.split()
        if tokens[0] == "s":
            result = parseResultToken(" ".join(tokens[1:]))
        elif tokens[0] == "c":
            pass
        elif tokens[0] == "o":
            intermediateOptimums.append(int(tokens[1]))
        elif tokens[0] == "v":
            for literalString in tokens[1:]:
                literal = int(literalString)
                variable = abs(literal)
                value = (literal > 0)
                variableAssignments[variable] = value

    return result, variableAssignments, intermediateOptimums


class TileType(Enum):
    thicket = 0
    river = 1


class Field:
    def __init__(self, width, height, variableAssignments):
        self.width = width
        self.height = height
        self.variableAssignments = variableAssignments
        self.tiles = self.makeTiles()

    def calcVariableIndex(self, x, y):
        return y * self.width + x + 1

    def getTileForVariable(self, variableIndex):
        if self.variableAssignments[variableIndex]:
            output = TileType.river
        else:
            output = TileType.thicket
        return output

    def getTileAtPositionFromVariables(self, x, y):
        variableIndex = self.calcVariableIndex(x, y)
        if variableIndex in self.variableAssignments:
            output = self.getTileForVariable(variableIndex)
        else:
            raise RuntimeError("unknown assignment for tile ({},{})".format(x, y))
        return output

    def makeTiles(self):
        tiles = []
        for y in range(self.height):
            for x in range(self.width):
                output = self.getTileAtPositionFromVariables(x, y)
                tiles.append(output)
        return tiles

    def calcTileIndex(self, x, y):
        return y * self.width + x

    def printGrid(self):
        translation = {TileType.river: "W", TileType.thicket: "T"}
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[self.calcTileIndex(x, y)]
                print(" {}".format(translation[tile]), end='')
            print()
            print()

    def tryPrintUrl(self):
        if self.width == 5:
            translation = {TileType.river: "1", TileType.thicket: "2"}
            url = "https://loopherolayout.xyz/?c={}".format("".join([translation[tile] for tile in self.tiles]))
            print("see also: {}".format(url))
            return True
        else:
            return False


parser = argparse.ArgumentParser()
parser.add_argument('--width', dest='width', default=5)
parser.add_argument('--height', dest='height', default=12)
args = parser.parse_args()

result, variableAssignments, _ = parseInput()

if result == Result.optimumFound:
    print("An optimum solution was found.")
    print()

    try:
        field = Field(args.width, args.height, variableAssignments)
    except RuntimeError as e:
        print("Error: {}".format(e))

    field.printGrid()
    field.tryPrintUrl()

elif result == Result.unsat:
    print("Error: The formula is unsatisfiable, therefore no valid solution exists")
elif result == Result.unknown:
    print("Error: An unknown error occurred while solving the SAT formula")
