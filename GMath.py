# todo:
#   Test: remap
#   Add: clamp version of lerp - return v won't go beyound a or b
#   Add: wrapper for sin, cosine, time.time, and atan
#
#
#
# Resources:      (Maybe has more functions to add)
#   https://gamedevbeginner.com/the-right-way-to-lerp-in-unity-with-examples/
#   https://www.ronja-tutorials.com/post/047-invlerp_remap/
#
#
# Ref: https://en.wikipedia.org/wiki/Interpolation
# Ref: https://en.wikipedia.org/wiki/Linear_interpolation
# Ref: https://en.wikipedia.org/wiki/Extrapolation
# Ref: https://en.wikipedia.org/wiki/Iterated_function
#
# Ref: https://en.wikipedia.org/wiki/Pythagorean_theorem
#
# Ref: https://www.omnicalculator.com/math/distance


import math


def magnitude(pos):
    # Ref: https://www.khanacademy.org/computing/computer-programming/programming-natural-simulations/programming-vectors/a/vector-magnitude-normalization
    #
    # Formula:
    #   mag = sqrt(x^2 + y^2...)
    x, y = 0, 1
    return math.sqrt((pos[x]*pos[x]) + (pos[y]*pos[y]))


def normalize(pos_x, pos_y: int) -> tuple:
    # Ref: https://www.khanacademy.org/computing/computer-programming/programming-natural-simulations/programming-vectors/a/vector-magnitude-normalization
    #
    # Formula:
    #   np = p/m

    x, y = 0, 1
    mag = magnitude((pos_x, pos_y))
    norm = (pos_x, pos_y)
    if mag > 0:
        norm = (pos_x/mag, pos_y/mag)

    return norm


# Returns a value between a and b based on a weight/percentage
# Examples:
#   lerp(1, 3, 1) = 3
#   lerp(1, 3, 0) = 1
#   lerp(1, 3, 0.5) = 2
def lerp(a, b, t: float) -> float:
    return (1.0 - t) * a + b * t


# Returns a weight/percentage based on a, b and the value entered
def invlerp(a, b, v: float) -> float:
    return (v - a) / (b - a)


# Returns a value between iMin and iMax based on value, but the output (value) will be limited/capped
# to the values given by oMin and oMax.
def remap(iMin, iMax, oMin, oMax, value: float) -> float:
    return lerp(oMin, oMax, invlerp(iMin, iMax, value))