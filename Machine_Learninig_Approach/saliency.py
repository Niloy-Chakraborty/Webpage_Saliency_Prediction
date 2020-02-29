# -*- coding: utf-8 -*-
"""Saliency.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mAqEljEkwLHU7fxdEEvr4dw4E6uEV3nj
"""
"""
This script generates the intensity, channel orientation red-green,
blue-yellow subchannel consicuity maps of the webpagescreenshots.
This script also gives ittikoch's saliency maps for a webpage image.
Here eye fixation maps are resized to the same size as that of the
conspicuity maps mentioned above.
"""

# Uncomment if using Google colab
# from google.colab import drive
#
# drive.mount('/content/drive')

import math
import logging
import cv2
import numpy
from scipy.ndimage.filters import maximum_filter
import os
import sys

"""
Function Name: features()
Functionalities: This function takes image as an input and extracts features for the 
image by down-scaling it levels times and transforming it by applying
function at each scaled version and finally computing the difference
between the scaled and transformed version.
Parameter:image, channel, levels, startsize
Returns: features
"""


def features(image, channel, levels=9, start_size=(256, 256)):
    image = channel(image)
    if image.shape != start_size:
        # print("size is different")
        image = cv2.resize(image, start_size)
    # print("Finished")
    scales = [image]
    for l in range(levels - 1):
        # logger.debug("scaling at level %d", l)
        scales.append(cv2.pyrDown(scales[-1]))

    features = []
    # print("levels: ", levels-5)
    for i in range(1, levels - 5):
        big = scales[i]
        for j in (3, 4):
            # logger.debug("computing features for levels %d and %d", i, i + j)
            small = scales[i + j]
            srcsize = (small.shape[1], small.shape[0])
            dstsize = (big.shape[1], big.shape[0])
            # logger.debug("Shape source: %s, Shape target :%s", srcsize, dstsize)
            scaled = cv2.resize(small, dstsize)
            features.append(((i + 1, j + 1), cv2.absdiff(big, scaled)))
            # print("inside feature function: ", len(features))
        # print("inside feature function: ",len(features))
    # print("i reached end of features")
    return features


"""
Function Name: N()
Functionalities: This function takes image as an input and returns normalized
                 feature map as per Itti et al. (1998).				
Parameter:image
Returns: normalized feature map
"""


def N(image):
    M = 8.  # an arbitrary global maximum to which the image is scaled.
    # (When saving saliency maps as images, pixel values may become
    # too large or too small for the chosen image format depending
    # on this constant)
    image = cv2.convertScaleAbs(image, alpha=M / image.max(), beta=0.)
    w, h = image.shape
    maxima = maximum_filter(image, size=(w / 10, h / 1))
    maxima = (image == maxima)
    mnum = maxima.sum()
    # logger.debug("Found %d local maxima.", mnum)
    maxima = numpy.multiply(maxima, image)
    mbar = float(maxima.sum()) / mnum
    # logger.debug("Average of local maxima: %f.  Global maximum: %f", mbar, M)
    return image * (M - mbar) ** 2


"""
Function Name: makeNormalizedColorChannels()
Functionalities: This function for a given image, normalizes all the 3 channels. It implements	
                 color opponencies as per Itti et al. (1998).		
Parameter:image, thresholdRatio
Returns: image
"""


def makeNormalizedColorChannels(image, thresholdRatio=10.):
    intens = intensity(image)
    threshold = intens.max() / thresholdRatio
    # logger.debug("Threshold: %d", threshold)
    r, g, b = cv2.split(image)
    cv2.threshold(src=r, dst=r, thresh=threshold, maxval=0.0, type=cv2.THRESH_TOZERO)
    cv2.threshold(src=g, dst=g, thresh=threshold, maxval=0.0, type=cv2.THRESH_TOZERO)
    cv2.threshold(src=b, dst=b, thresh=threshold, maxval=0.0, type=cv2.THRESH_TOZERO)
    R = r - (g + b) / 2
    G = g - (r + b) / 2
    B = b - (g + r) / 2
    Y = (r + g) / 2 - cv2.absdiff(r, g) / 2 - b

    # Negative values are set to zero.
    cv2.threshold(src=R, dst=R, thresh=0., maxval=0.0, type=cv2.THRESH_TOZERO)
    cv2.threshold(src=G, dst=G, thresh=0., maxval=0.0, type=cv2.THRESH_TOZERO)
    cv2.threshold(src=B, dst=B, thresh=0., maxval=0.0, type=cv2.THRESH_TOZERO)
    cv2.threshold(src=Y, dst=Y, thresh=0., maxval=0.0, type=cv2.THRESH_TOZERO)

    image = cv2.merge((R, G, B, Y))
    return image


"""
Function Name: markMaxima()
Functionalities: This function maps the maxima in the saliency.		
Parameter:saliency
Returns: marked version
"""


def markMaxima(saliency):
    maxima = maximum_filter(saliency, size=(20, 20))
    maxima = numpy.array(saliency == maxima, dtype=numpy.float64) * 255
    r = cv2.max(saliency, maxima)
    g = saliency
    b = saliency
    marked = cv2.merge((b, g, r))
    return marked


"""
Function Name: writeCond()
Functionalities: This function saves the conspicuity map is the given location.	
Parameter:outFileName, image
Returns: Null
"""


def writeCond(outFileName, image):
    from matplotlib import pyplot as plt
    # plt.imsave(outFileName, image, cmap='gray')
    cv2.imwrite(outFileName, image)


# if outFileName and args.fileList:
# 	cv2.imwrite(outFileName % name, image)
# elif outFileName:
# 	cv2.imwrite(outFileName, image)

"""
Function Name: intensity()
Functionalities: This function converts a grey image to a color image and it is 
                 used as a parameter 'channel' to the function features().
Parameter:image
Returns: image
"""


def intensity(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


"""
Function Name: sumNormalizedFeatures()
Functionalities: This function takes features as input, normalizes them and combines
                 them into one.
Parameter:features, levels, startSize
Returns: combined feature map
"""


def sumNormalizedFeatures(features, levels=9, startSize=(256, 256)):
    # print(len(features))
    # commonWidth = int(startSize[0] / 2**(levels/2 - 1))
    commonWidth = int(startSize[0] / 2 ** (levels / 3))
    # commonHeight = int(startSize[1] / 2**(levels/2 - 1))
    commonHeight = int(startSize[1] / 2 ** (levels / 3))
    commonSize = (commonWidth, commonHeight)
    # logger.info("Size of conspicuity map: %s", commonSize)
    # print(commonSize)
    consp = N(cv2.resize(features[0][1], commonSize))
    for f in features[1:]:
        resized = N(cv2.resize(f[1], commonSize))
        consp = cv2.add(consp, resized)
    # print("i reached the end of SumNormalizedFeatures")
    return consp


"""
Function Name: makeGaborFilter()
Functionalities: This function generates a gabor filter with input parameters 
                 (taken as an array) and returns a function which is used as a
                 parameter channel for function features().
Parameter: dims, lambd, theta, psi, sigma, gamma
Returns: gabor filter
"""


def makeGaborFilter(dims, lambd, theta, psi, sigma, gamma):
    def xpf(i, j):
        return i * math.cos(theta) + j * math.sin(theta)

    def ypf(i, j):
        return -i * math.sin(theta) + j * math.cos(theta)

    def gabor(i, j):
        xp = xpf(i, j)
        yp = ypf(i, j)
        return math.exp(-(xp ** 2 + gamma ** 2 * yp ** 2) / 2 * sigma ** 2) * math.cos(2 * math.pi * xp / lambd + psi)

    halfwidth = dims[0] / 2
    halfheight = dims[1] / 2

    kernel = numpy.array([[gabor(halfwidth - i, halfheight - j) for j in range(dims[1])] for i in range(dims[1])])

    def theFilter(image):
        return cv2.filter2D(src=image, ddepth=-1, kernel=kernel, )

    return theFilter


"""
Function Name: intensityConspicuity()
Functionalities: This function generates the intensity conspicuity map.
Parameter: image
Returns: intensity cospicuity map
"""


def intensityConspicuity(image):
    fs = features(image=im, channel=intensity)
    # print("i m inside intensity conspicuity")
    return sumNormalizedFeatures(fs)


"""
Function Name: gaborConspicuity()
Functionalities: This function generates the channel orientation conspicuity map.
Parameter:image, steps
Returns: channel orientation cospicuity map
"""


def gaborConspicuity(image, steps):
    gaborConspicuity = numpy.zeros((32, 32), numpy.float)
    for step in range(steps):
        theta = step * (math.pi / steps)
        gaborFilter = makeGaborFilter(dims=(10, 10), lambd=2.5, theta=theta, psi=math.pi / 2, sigma=2.5, gamma=.5)
        gaborFeatures = features(image=intensity(im), channel=gaborFilter)
        summedFeatures = sumNormalizedFeatures(gaborFeatures)
        gaborConspicuity += N(summedFeatures)
    return gaborConspicuity


"""
Function Name: rgConspicuity()
Functionalities: This function generates the red-green subchannel conspicuity map.
Parameter:image
Returns: red-green subchannel conspicuity map
"""


def rgConspicuity(image):
    def rg(image):
        r, g, _, __ = cv2.split(image)
        return cv2.absdiff(r, g)

    fs = features(image=image, channel=rg)
    return sumNormalizedFeatures(fs)


"""
Function Name: byConspicuity()
Functionalities: This function generates the blue-yellow subchannel conspicuity map.
Parameter:image
Returns: blue-yellow subchannel conspicuity map
"""


def byConspicuity(image):
    def by(image):
        _, __, b, y = cv2.split(image)
        return cv2.absdiff(b, y)

    fs = features(image=image, channel=by)
    return sumNormalizedFeatures(fs)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    # input directory of the webpage images
    inputDir = "/content/drive/My Drive/HCI_prep/Dataset_Website1/stimuli/"
    # currentDir = os.curdir

    # current working directory
    currentDir = "/content/drive/My Drive/HCI_prep/IttiKoch/"
    # inputDir = os.path.join(currentDir, "dataset/stimuli/")

    # out directory for saving the original image. Image is stored with name equivalent to integer no.s.
    outDir_Original_Data = os.path.join(currentDir, "Original_Data")
    if not os.path.exists(outDir_Original_Data):
        os.mkdir(outDir_Original_Data)

    # out directory for saving intensity conspicuity maps of the webpage images.
    # Image is stored with name equivalent to integer no.s.
    outDir_intensity = os.path.join(currentDir, "intensity_32")
    if not os.path.exists(outDir_intensity):
        os.mkdir(outDir_intensity)

    # out directory for saving the channel orientation conspicuity maps of webpage images.
    # Image is stored with name equivalent to integer no.s.
    outDir_gabor = os.path.join(currentDir, "gabor_32")
    if not os.path.exists(outDir_gabor):
        os.mkdir(outDir_gabor)

    # out directory for saving the red-green subchannel conspicuity maps of webpage images.
    # Image is stored with name equivalent to integer no.s.
    outDir_rg = os.path.join(currentDir, "rg_32")
    if not os.path.exists(outDir_rg):
        os.mkdir(outDir_rg)

    # out directory for saving the blue-yellow subchannel conspicuity maps of webpage images.
    # Image is stored with name equivalent to integer no.s.
    outDir_by = os.path.join(currentDir, "by_32")
    if not os.path.exists(outDir_by):
        os.mkdir(outDir_by)

    # out directory for saving the combined subchannel conspicuity maps of webpage images.
    # Image is stored with name equivalent to integer no.s.
    outDir_c = os.path.join(currentDir, "c_32")
    if not os.path.exists(outDir_c):
        os.mkdir(outDir_c)

    # out directory for saving the saliency maps of webpage images as per Itti et. al. (1998).
    # Image is stored with name equivalent to integer no.s.
    outDir_saliency = os.path.join(currentDir, "saliency_32")
    if not os.path.exists(outDir_saliency):
        os.mkdir(outDir_saliency)

    # input directory of eye fixation maps of the webpages
    eyemapInputDir = os.path.join("/content/drive/My Drive/HCI_prep/Dataset_Website1/", "finalHeatMap")

    # out directory for saving the resized eye fixation maps.
    # Image is stored with name equivalent to integer no.s.
    eyemapResizedOutDir = os.path.join(currentDir, "eyeFixationResized33_32")

    if not os.path.exists(eyemapResizedOutDir):
        os.mkdir(eyemapResizedOutDir)

    # data = []
    commonSize = (32, 32)
    fileIndex = 0

    for filename in os.listdir(inputDir):

        if filename.endswith(".png"):
            try:
                path = os.path.join(inputDir, filename)
                # print("path: ", path)
                print(fileIndex)
                im = cv2.imread(path, cv2.COLOR_BGR2RGB)  # assume BGR, convert to RGB---more intuitive code.
                # print("done1")
                writeCond(os.path.join(outDir_Original_Data, str(fileIndex) + ".png"), im)
                # print("done2")
                im = numpy.array(im)
                if im is None:
                    # logger.fatal("Could not load file \"%s.\"", filename)
                    sys.exit()
                # print("done3")
                intensty = intensityConspicuity(im)
                # print("done4")
                gabor = gaborConspicuity(im, 4)
                # print("done1")
                im = makeNormalizedColorChannels(im)
                # print("done2")
                rg = rgConspicuity(im)
                # print("done3")
                by = byConspicuity(im)
                # print("done4")
                c = rg + by
                saliency = 1. / 3 * (N(intensty) + N(c) + N(gabor))
                c = .25 * c
                path = os.path.join(eyemapInputDir, filename)
                img = cv2.imread(path)
                img = cv2.resize(img, commonSize)
                # print("done5")
                writeCond(os.path.join(eyemapResizedOutDir, str(fileIndex) + ".png"), img)
                # print("done6")
                writeCond(os.path.join(outDir_intensity, str(fileIndex) + ".png"), intensty)
                writeCond(os.path.join(outDir_gabor, str(fileIndex) + ".png"), gabor)
                writeCond(os.path.join(outDir_rg, str(fileIndex) + ".png"), rg)
                writeCond(os.path.join(outDir_by, str(fileIndex) + ".png"), by)
                writeCond(os.path.join(outDir_c, str(fileIndex) + ".png"), c)
                writeCond(os.path.join(outDir_saliency, str(fileIndex) + ".png"), saliency)
                fileIndex = fileIndex + 1
            except:
                print("cannot open the file : " + path)
