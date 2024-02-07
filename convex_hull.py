# Alice Giola
# CS 4412
# Project 2: Convex Hull

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


# Based on my boyfriend's suggestion I made this custom class that is aware of its neighbors,
# clones the list of points and holds useful references to their clockwise and counterclockwise
# neighbors as well as a ref to the original point.

class pointClone:
    def __init__(self, x, y, qpointf_pointer):
        self.x = x
        self.y = y

        # Gives the points an ability to have a clockwise and counterclockwise neighbor.
        self.clockwise_neighbor = None
        self.counterclockwise_neighbor = None
        self.qpointf_pointer = qpointf_pointer


# This is the class you have to complete.
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        # Sorts the list of points by their X values and then places them into a
        # new list to be used in the algorithm
        points_sorted = sorted(points, key=lambda x: x.x())

        t1 = time.time()
        points_list = []

        # Uses the new pointsClone class to makes processing the list of points
        # easier to use
        for x in points_sorted:
            points_list.append(pointClone(x.x(), x.y(), x))
        # Takes the final calculated project and places it into a final list to
        # be calculated
        hull_final = recursive_convex_hull(points_list)
        t2 = time.time()

        # Takes the hull from above and draws them out using the QlineF feature
        # so they appear on the GUI (checks for if the final hull has at least two
        # points)
        finished_list = []
        if len(hull_final) > 1:
            for x in hull_final:
                finished_list.append(QLineF(x.qpointf_pointer, x.clockwise_neighbor.qpointf_pointer))
        hull = finished_list

        # When passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(hull, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t1 - t2))


def recursive_convex_hull(points):
    # Checks if the attribute points has only one point remaining.
    # If it does then it returns the single point
    if len(points) == 1:
        return points

    # Finds the middle point of the list and assigns it to a usable
    # variable to be used in the below calculations. Takes the resulting
    # float and converts it to an integer since floats can't be used to define the center.
    middle_point = int((len(points) - 1) / 2)

    # Assigns sets of points or "sub-hulls" to a s1 and s2 variable. then calls the
    # recursion of these points to divide and conquer the equation for easier
    # processing. Uses the middle point and splits the two sub-hulls down the center.
    s1 = recursive_convex_hull(points[0: (middle_point + 1)])
    s2 = recursive_convex_hull(points[(middle_point + 1): (len(points))])

    # Calls the combine_hulls function during return which takes parts s1 and s2
    # and merges them to create larger sub-hulls
    return combine_hulls(s1, s2)


def find_rotation(p1, p2, p3):
    # This function is used to determine the "facing" rotation from points
    # p1, p2, and p3. Searches for the cross product of the points to determine
    # if its facing left or right or if their neither.
    part1 = (p3.x - p1.x) * (p2.y - p1.y)
    part2 = (p2.x - p1.x) * (p3.y - p1.y)
    return part1 - part2


def combine_hulls(s1, s2):
    # Assigns the furthest right point of the left hull to p_top and the furthest
    # left point of the right hull to q_top to find the top tangent points
    p_top = max(s1, key=lambda pointClone: pointClone.x)
    q_top = min(s2, key=lambda pointClone: pointClone.x)

    # Assigns the bottom tangent points to the same as the top tangent points
    # since they will start in the same location
    p_bot = p_top
    q_bot = q_top

    # While loop that searches for the top tangent
    while True:
        # Copies p_top and q_top for checking if they match their starting positions
        # later in calculations
        p_start = p_top
        q_start = q_top

        # Searches for direction using a combination of the find_rotation function
        # and the pointClone class. This allows for the creation of the top half
        # tangent for the creation of a new hull from the combination of these two
        if q_top.clockwise_neighbor:
            while 0 > find_rotation(p_top, q_top, q_top.clockwise_neighbor):
                q_top = q_top.clockwise_neighbor
        if p_top.counterclockwise_neighbor:
            while 0 < find_rotation(q_top, p_top, p_top.counterclockwise_neighbor):
                p_top = p_top.counterclockwise_neighbor

        # if the top p and q points match the starting points after all calculation
        # have been made, break and begin search of the bottom tangent
        if p_top == p_start and q_top == q_start:
            break

    # While loop that searches for the bottom tangent
    while True:
        # Copies p_bot and q_bot for checking if they match their starting positions
        # later in calculations
        p_start = p_bot
        q_start = q_bot

        # Searches for direction using a combination of the find_rotation function
        # and the pointClone class. This allows for the creation of the bottom half
        # tangent for the creation of a new hull from the combination of these two
        # (very similar in essence to finding the top half of the hull)
        if q_bot.counterclockwise_neighbor:
            while 0 < find_rotation(p_bot, q_bot, q_bot.counterclockwise_neighbor):
                q_bot = q_bot.counterclockwise_neighbor
        if p_bot.clockwise_neighbor:
            while 0 > find_rotation(q_bot, p_bot, p_bot.clockwise_neighbor):
                p_bot = p_bot.clockwise_neighbor

        # if the bottom p and q points match the starting points after all calculation
        # have been made, break and continue with the rest of the function
        if p_bot == p_start and q_bot == q_start:
            break

    # Once the two hulls have been connected from the above while loops, recreates the
    # points neighbors so the points between the tangents are now recognized as
    # neighboring points
    p_top.clockwise_neighbor = q_top
    q_top.counterclockwise_neighbor = p_top
    p_bot.counterclockwise_neighbor = q_bot
    q_bot.clockwise_neighbor = p_bot

    # When the function is done processing the tangent lines and the hulls have been
    # fully combined, creates a new list based upon their neighboring clockwise
    # point to be sent back to the recursive function
    start = q_bot
    combined_hull = []
    while True:
        combined_hull.append(q_bot)
        q_bot = q_bot.clockwise_neighbor
        if q_bot == start:
            break

    # Returns the final combined hulls as a single hull to be used in the recursive
    # function to be combined with the next hull or be returned to the main function
    return combined_hull
