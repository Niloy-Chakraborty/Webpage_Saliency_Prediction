# -*- coding: utf-8 -*-
"""SVM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VsMLdlxK8I6Z5cKiJMSeAMi2ispGW08g
"""
"""
This python script implements the SVM with degree 2 polynomial kernal
model using sklearn module and gives saliency predictions on webpage 
screenshots. The webpage screenshot cannot be given as such. This script 
takes input as a csv file containing intensity, chanel orientation, 
blue-yellow and red green conspicuity information at each pixel. The csv 
file can be generated by running conspicuity_ittikoch.py and 
dataFileGeneration.py consequently for a image.
"""
# Uncomment if using Google colab

# from google.colab import drive
# drive.mount('/content/drive')

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import metrics
import cv2
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import shuffle
import pandas as pd
import csv
import os

# list of headers for pandas dataframe
columns = ['Image_Names', 'Intensity_feature', 'Gabor_feature', 'C_feature', 'Saliency_value', 'label']
# Loading the data from the training data file
dataset = pd.read_csv('/content/drive/My Drive/HCI_prep/IttiKoch/data_32_selected.csv', names=columns, header=None)
# shuffling the data
dataset = shuffle(dataset)
# resting the index
dataset = dataset.reset_index()
print("before drop", dataset.head())

# creating the feature vector x and output vector y
y = dataset['label']
x = dataset.drop(["Image_Names", "label", "Saliency_value", "index"], axis=1)

# normalization
scaler = MinMaxScaler()
x = scaler.fit_transform(x)
x = pd.DataFrame(x)
# y = y/255.0

# train/test spilt
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=109)

# creating the SVM model with polynomial kernel of degree 2
SVMclf = svm.SVC(kernel='poly', degree=2)

# training the model on the split training dataset
SVMclf.fit(X_train, y_train)

# testing the model on the split test dataset
y_pred = SVMclf.predict(X_test)

"""
Function Name: get_prediction()
Functionalities: This function takes image and predicts saliency on the image 
                 using the SVM model and save the file in 
                 the custom location. It takes three inputs image, model and 
                 filename
Parameter:imageArr, rf, index
Returns: NULL

"""


def get_prediction(imageArr, rf, index):
    # folder location to save the predicted results
    predictionOnTestImages = "/content/drive/My Drive/HCI_prep/IttiKoch/SVM_Degree3_Prediction/"
    if not os.path.exists(predictionOnTestImages):
        os.mkdir(predictionOnTestImages)
    imageArr = np.asarray(imageArr, dtype="float")
    imageArr = scaler.fit_transform(imageArr)
    imageArr = pd.DataFrame(imageArr)

    predictionOnImage = rf.predict(imageArr)
    # print(predictionOnImage.shape)
    img = predictionOnImage.reshape(128, 128)
    img = img * 255.0
    cv2.imwrite(os.path.join(predictionOnTestImages, index + ".png"), img)


# Reading the test image data file and getting prediction for each
# test image by calling get_prediction() function.
file = open("/content/drive/My Drive/HCI_prep/IttiKoch/test_data_128.csv", 'r')
csvReader = csv.reader(file, delimiter=',')

# feature vector for test images
imageArr = []
# refers to image name, in this case denoted by integers
imageIndex = 0

for row in csvReader:
    # print(int(float(row[0])))
    if int(float(row[0])) == imageIndex:
        imageArr.append(row[1:4])
        if len(imageArr) == (128 * 128):
            print(imageIndex)
            get_prediction(imageArr, SVMclf, str(imageIndex))
            print("done")
            imageIndex = imageIndex + 1
            imageArr = []

file.close()

# metrics for evaluating the SVM model.
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
print("Precision:", metrics.precision_score(y_test, y_pred))
print("Recall:", metrics.recall_score(y_test, y_pred))