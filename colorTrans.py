from PIL import Image ,ImageFont,ImageDraw
import numpy as np
import math

# path
path_tgt = 'img/style.png'
path_src = 'img/texture.png'
path_tsf = 'img/trasfer.png'

def arrayFromImg(_path = path_tgt):
    _img = Image.open(_path)
    _px = _img.load()
    _colorArray = np.ndarray(shape=(_img.width, _img.height, 3), dtype=np.float32, order='C')
    for y in range(_img.height):
        for x in range(_img.width):
            _colorArray[x, y] = _px[x, y]
    return _colorArray

def imgFromArray(_colorArray, _path = path_tsf):
    _img = Image.new("RGB", (_colorArray.shape[0],_colorArray.shape[1]), (0,0,0))
    _px = _img.load()
    for y in range(_img.height):
        for x in range(_img.width):
            _px[x, y] = (int(_colorArray[x,y][0]),int(_colorArray[x,y][1]),int(_colorArray[x,y][2]))

    _img.save(_path)





# # exaple array - correct way of multiply matrix and matrix vector
# xyz_lms = np.array([[0.3897, 0.689,-0.0787],[-0.2298,1.1834,0.0464],[0,0,1]])
# rbg_xyz = np.array([[0.5141,0.3239,0.1604],[0.2651,0.6702,0.0641],[0.0241,0.1228,0.8444]])
# c = np.array([1,1,1])
# rgb_lms = xyz_lms@rbg_xyz
# c = xyz_lms@c
#
# print(rgb_lms)
# print(c)
# # exaple array - correct way of multiply matrix and matrix vector

m_rgb_lms = np.array([[0.3811, 0.5783,0.0402],
                      [0.1967,0.7244,0.0782],
                      [0.0241,0.1228,0.8444]])

m_lms_rgb = np.array([[4.4679, -3.5873,0.1193],
                      [-1.2186,2.3809,-0.1624],
                      [0.0497,-0.2439,1.2045]])


m_lms_lab_0 = np.array([[1/np.sqrt(3),0,0],
                        [0,1/np.sqrt(6),0],
                        [0,0,1/np.sqrt(2)]])
m_lms_lab_1 = np.array([[1,1,1],
                        [1,1,-2],
                        [1,-1,0]])
m_lms_lab = m_lms_lab_0 @m_lms_lab_1

m_lab_lms_0 = np.array([[1,1,1],
                        [1,1,-1],
                        [1,-2,0]])
m_lab_lms_1 = np.array([[np.sqrt(3)/3,0,0],
                        [0,np.sqrt(6)/6,0],
                        [0,0,np.sqrt(2)/2]])
m_lab_lms = m_lab_lms_0 @ m_lab_lms_1

def convert_rgb_lab (_rgb):
    _lms = m_rgb_lms@_rgb
    # log 10

    for i in range(3):

        if np.isnan(np.log10(_lms[i])) or np.isinf(np.log10(_lms[i])):
            _lms[i] = 0
        else:
            _lms[i] = np.log10(_lms[i])

    # _lms[0] = np.log10(_lms[0])
    # _lms[1] = np.log10(_lms[1])
    # _lms[2] = np.log10(_lms[2])
    # if np.isinf(_lms[0]) :
    #     _lms[0] = 0
    # if np.isinf(_lms[1]) :
    #     _lms[1] = 0
    # if np.isinf(_lms[2]) :
    #     _lms[2] = 0

    _lab = m_lms_lab@_lms
    return (_lab)

def convert_lab_rgb(_lab):
    _lms = m_lab_lms@_lab
    # power 10
    _lms[0] = np.power( 10,_lms[0])
    _lms[1] = np.power( 10,_lms[1])
    _lms[2] = np.power( 10,_lms[2])
    # rgb
    _rgb = m_lms_rgb@_lms
    return(_rgb)

def convert_img_rgb_lab (_array):
    # convert rgb int -> lab float
    for y in range(_array.shape[1]):
        for x in range(_array.shape[0]):
            # int to float , rgb to lab
            _array[x, y] = convert_rgb_lab (_array[x, y]/255)
    return(_array)

def convert_img_lab_rgb (_array):
    # convert rgb int -> lab float
    for y in range(_array.shape[1]):
        for x in range(_array.shape[0]):
            # int to float , rgb to lab
            _array[x, y] = convert_lab_rgb (_array[x, y])
    return(_array)

def convert_img_rgb_float_int (_array):
    # convert rgb float -> int
    _iArray = np.ndarray(shape=_array.shape, dtype=np.int, order='C')
    for y in range(_array.shape[1]):
        for x in range(_array.shape[0]):

            _array[x, y][0] = np.clip(_array[x, y][0], 0, 1)
            _array[x, y][1] = np.clip(_array[x, y][1], 0, 1)
            _array[x, y][2] = np.clip(_array[x, y][2], 0, 1)
            _iArray[x,y] = 255 * _array[x, y]
    return(_iArray)

class Img_info():
    def __init__(self,_mean,_sd,_dArray):
        self.mean = _mean
        self.sd = _sd
        self.dArray = _dArray



def gat_mean_sd (_array):
    w = _array.shape[0]
    h = _array.shape[1]
    _mean = (0,0,0)

    for y in range(h):
        for x in range(w):
            # <x>
            _mean += _array[x, y]
    _mean = _mean/w/h

    _sd = (0,0,0)
    _dArray = np.ndarray(shape=_array.shape, dtype= np.clongdouble, order='C')
    for y in range(h):
        for x in range(w):
            # x*
            _dArray[x,y] = abs(_array[x, y] - _mean)
            # sigma
            _sd +=_dArray[x,y]
    _sd = _sd/w/h

    return(Img_info(_mean , _sd , _dArray))


''' old method
s_img_array = arrayFromImg(path_s)
r_img_array = arrayFromImg(path_r)

# data convert
s_img_array = convert_img_rgb_lab(s_img_array)
r_img_array = convert_img_rgb_lab(r_img_array)

# get info
s_img_info = gat_mean_sd (s_img_array)
r_img_info = gat_mean_sd (r_img_array)

# data

# print(r_img_info.sd)
# print(r_img_info.mean)
# print(r_img_info.dArray)

# print(s_img_info.sd)
# print(s_img_info.mean)
# print(s_img_info.dArray)

## s_img_info.dArray +=s_img_info.mean
## tArray = convert_img_lab_rgb(s_img_info.dArray)
## imgFromArray(tArray)

# make new data

w = s_img_info.dArray.shape[0]
h = s_img_info.dArray.shape[1]
_tArray = np.ndarray(shape=s_img_info.dArray.shape, dtype=np.clongdouble, order='C')

_td = r_img_info.sd/s_img_info.sd * s_img_info.dArray
_tArray = r_img_info.mean + _td

# first convert lab to rgb, then standarlize the value and clamp
# img will be wired when 2 images are too different
_resultArray = convert_img_rgb_float_int(convert_img_lab_rgb(_tArray))
imgFromArray(_resultArray)
print (_resultArray)

# convert rgb

'''

import cv2

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

def image_stats (src):
    l, a, b = cv2.split(src)
    (lMean, lStd) = (l.mean(), l.std())
    (aMean, aStd) = (a.mean(), a.std())
    (bMean, bStd) = (b.mean(), b.std())
    return (lMean, lStd, aMean, aStd, bMean, bStd)

def _min_max_scale(arr, new_range=(0, 255)):
	"""
	Perform min-max scaling to a NumPy array

	Parameters:
	-------
	arr: NumPy array to be scaled to [new_min, new_max] range
	new_range: tuple of form (min, max) specifying range of
		transformed array

	Returns:
	-------
	NumPy array that has been scaled to be in
	[new_range[0], new_range[1]] range
	"""
	# get array's current min and max
	mn = arr.min()
	mx = arr.max()

	# check if scaling needs to be done to be in new_range
	if mn < new_range[0] or mx > new_range[1]:
		# perform min-max scaling
		scaled = (new_range[1] - new_range[0]) * (arr - mn) / (mx - mn) + new_range[0]
	else:
		# return array if already in range
		scaled = arr

	return scaled

def _scale_array(arr, clip=True):
	"""
	Trim NumPy array values to be in [0, 255] range with option of
	clipping or scaling.

	Parameters:
	-------
	arr: array to be trimmed to [0, 255] range
	clip: should array be scaled by np.clip? if False then input
		array will be min-max scaled to range
		[max([arr.min(), 0]), min([arr.max(), 255])]

	Returns:
	-------
	NumPy array that has been scaled to be in [0, 255] range
	"""
	if clip:
		scaled = np.clip(arr, 0, 255)
	else:
		scale_range = (max([arr.min(), 0]), min([arr.max(), 255]))
		scaled = _min_max_scale(arr, new_range=scale_range)

	return scaled


# green = np.float32([[[0.5,1.0,0]]])
# new_green = cv2.cvtColor(green,cv2.COLOR_BGR2LAB).astype("float32")

#read source

# uncali
tgt =  cv2.imread(path_tgt)
# cali
src = cv2.imread(path_src)

# srgb to rgb
for y in range(src.shape[1]):
    for x in range(src.shape[0]):
        # int to float , rgb to lab
        for i in range(src.shape[2]):
            src[x, y][i] = GammaSRGBToLinear(src[x, y][i]/255)*255
for y in range(tgt.shape[1]):
    for x in range(tgt.shape[0]):
        # int to float , rgb to lab
        for i in range(tgt.shape[2]):
            tgt[x, y][i] = GammaSRGBToLinear(tgt[x, y][i]/255)*255

#rgb to lab
src = cv2.cvtColor(src.astype("uint8"), cv2.COLOR_BGR2LAB).astype("float32")
tgt = cv2.cvtColor(tgt.astype("uint8"), cv2.COLOR_BGR2LAB).astype("float32")

# back to int for opencv
(lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = image_stats(src)
(lMeanTgt, lStdTgt, aMeanTgt, aStdTgt, bMeanTgt, bStdTgt) = image_stats(tgt)

print(lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc)
print(lMeanTgt, lStdTgt, aMeanTgt, aStdTgt, bMeanTgt, bStdTgt)

l,a,b = cv2.split(src)

l -= lMeanSrc
a -= aMeanSrc
b -= bMeanSrc

l = (lStdTgt / lStdSrc) *l
a = (aStdTgt / aStdSrc) * a
b = (bStdTgt / bStdSrc) * b

l += lMeanTgt
a += aMeanTgt
b += bMeanTgt

clip = False

l = _scale_array(l, clip=clip)
a = _scale_array(a, clip=clip)
b = _scale_array(b, clip=clip)

tsf = cv2.merge([l, a, b])
tsf = cv2.cvtColor(tsf.astype("uint8"), cv2.COLOR_LAB2BGR)


# rgb to srgb
for y in range(tsf.shape[1]):
    for x in range(tsf.shape[0]):
        # int to float , rgb to lab
        for i in range(tsf.shape[2]):
            tsf[x, y][i] = LinearToGammaSRGB(tsf[x, y][i]/255)*255

print(tsf)

cv2.imwrite(path_tsf, tsf)

'''
window_name = path_r
# convert rgb to lab
source = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype("float32")

rows,cols,chanel = source.shape

r,g,b = cv2.split(src)

r_mean = r.mean()
r_std = r.std()
print(r_mean)
print(r_std)
'''