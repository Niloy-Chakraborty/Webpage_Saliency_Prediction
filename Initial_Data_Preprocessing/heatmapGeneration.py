# -*- coding: utf-8 -*-
"""HeatMapGenerationUsingGitCode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fOTjFSzpmQhC0kGk6yF5zmnyva0ojjQC
"""
"""
This script generated the heatmaps of the eye fixation data from
the FiWi dataset.
"""

import cv2, os
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
# from google.colab.patches import cv2_imshow

# from google.colab import drive
# drive.mount('/content/drive')

"""
Function Name: GaussianMask()
Functionalities: This function applies the gaussian blur for a pixel of an image.
Parameter:sizex, sizey, sigma, center, fix
Returns: gaussian mask
"""


def GaussianMask(sizex, sizey, sigma=32, center=None, fix=1):
    x = np.arange(0, sizex, 1, float)
    y = np.arange(0, sizey, 1, float)
    x, y = np.meshgrid(x, y)

    if center is None:
        x0 = sizex // 2
        y0 = sizey // 2

    else:
        if np.isnan(center[0]) == False and np.isnan(center[1]) == False:
            x0 = center[0]
            y0 = center[1]

        else:
            return np.zeros((sizey, sizex))

    return fix * np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)


"""
Function Name: Fixpos2Densemap()
Functionalities: This function takes the eye fixation data, get gaussian mask 
                 for each pixel and combines it together to give a heat map
Parameter: fix_arr, width, height
Returns: heat map
"""


def Fixpos2Densemap(fix_arr, width, height):
    heatmap = np.zeros((H, W), np.float32)
    for n_subject in tqdm(range(fix_arr.shape[0])):
        # here sigma = 25 which is equivalent to standard foveal size.
        heatmap += GaussianMask(W, H, 25, (fix_arr[n_subject, 0], fix_arr[n_subject, 1]), fix_arr[n_subject, 2])

    # Normalization
    heatmap = heatmap / np.amax(heatmap)
    heatmap = heatmap * 255
    heatmap = heatmap.astype("uint8")
    # heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    return heatmap


if __name__ == '__main__':
    # Load image file
    # img1 = cv2.imread('/content/drive/My Drive/HCI_prep/Dataset_Website1/stimuli/zite.png')

    # input directory for the eyefixation data
    imdir = '/content/drive/My Drive/HCI_prep/Dataset_Website1/eyeMaps/all5'

    # out directory for saving the heatmaps
    outdir = '/content/drive/My Drive/HCI_prep/Dataset_Website1/finalHeatMap25/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for file in os.listdir(imdir):

        if file.endswith(".png"):
            path = os.path.join(imdir, file)
            print(path)

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            result = np.where(img == 255)
            # y = np.array(result[0])[::-1]
            y = np.array(result[0])
            x = np.array(result[1])
            z = np.ones(x.shape)
            fix_arr = np.column_stack([x, y, z])
            H, W = img.shape
            heatmap = Fixpos2Densemap(fix_arr, W, H)
            cv2.imwrite(os.path.join(outdir, file), heatmap)

            # print(file + " cannot be opened")

plt.imshow(heatmap)
gray = cv2.cvtColor(heatmap, cv2.COLOR_RGB2GRAY)
cv2.imwrite('/content/drive/My Drive/HCI_prep/Dataset_Website1/out2.png', gray)
plt.show()
