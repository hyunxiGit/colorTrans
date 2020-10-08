import math
def LinearToGammaSRGB(  x ) :

    if x <= 0.0031308 :
        return 12.92 * x;
    else :
        return 1.055 * math.pow( x, 1.0 / 2.4 ) - 0.055;


def GammaSRGBToLinear( x ) :
    if x <= 0.04045 :
        return x / 12.92;

    else:
        return math.pow( (x + 0.055) / 1.055, 2.4 )