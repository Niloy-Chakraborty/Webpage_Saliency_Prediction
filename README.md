# Webpage_Saliency_Prediction

![Saliency Analysis](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/blob/master/Readme%20Images/SaliencyAnalysis.png)

In this project, we have done a focused study on the saliency analysis for webpages using FiWi dataset and propose a Fully Convolutional Network (FCN) based architecture to predict the saliency of webpages, following [this](https://people.eecs.berkeley.edu/~jonlong/long_shelhamer_fcn.pdf) implementation. Given an input Webpage image, the proposed model is capable of generating its saliency map.


P.S. This whole project has been performed and tested on Google Colab. [Colab Access](https://drive.google.com/open?id=19EOE1yqbsomld394ZsosZisnvPcRYdTT)

# Guidelines to use this Repository

## DIRECTORY ARCHITECTURE:
Can be seen [here](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/blob/master/Directory%20Architecture.txt)

## A. REQUIREMENTS:
To avoid version conflicts, 

install tensorflow version 1.15.0 from [Tensorflow](https://www.tensorflow.org/install/pip)

install keras version 2.2.5 from [keras](https://keras.io/)

## B. USING PRE-TRAINED MODEL FOR WEBPAGE SALIENCY ANALYSIS:
1. Download this repository
2. Download the Pre-trained model for FCN-16s from [here](https://drive.google.com/open?id=1-MKN-nQj6NOX-J9P9UOqp5mjqfMynWcC)
3. Provide correct path for the downloaded model. Run [Model_Performance_on_Test_Images.ipynb](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Prediction_and_Analysis)
4. For computing AUC, CC and NSS scores, codes are provided in [Prediction_and_Analysis](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Prediction_and_Analysis) folder. From [Evaluation Metric Scripts](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Prediction_and_Analysis/Evaluation%20Metric%20Scripts) run the auc_calculation.py for computing AUC score, and cross_correlation_and_nss_calculation.py for calculating CC/NSS score.

## C. FOR TRAINING MODEL WITH YOUR OWN DATA:
1. Download GDI dataset from [here](https://github.com/cvzoya/visimportance/tree/master/data)
2. Download FiWi dataset from [here](https://www-users.cs.umn.edu/~qzhao/webpage_saliency.html)
3. From [Model Training Scripts](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Model_Training_Scripts) folder, start training GDI model at first by running "GDI_FCN_TRAIN.ipynb" with GDI dataset. 
Alternatively this pre-trained model can be downloaded from [here](https://drive.google.com/open?id=1smxAlcvbkOpRBQb4ClfcAkgfaub6aMgo)
4. Run [heatmapGeneration.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Initial_Data_Preprocessing) from Initial_Data_Preprocessing folder for generating Heatmaps from FiWi eye fixation data, in a sparate folder "finalHeatMap" 
5. Run "[TestImageGenerator.ipynb"](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/blob/master/Initial_Data_Preprocessing/TestImageGenerator.ipynb) to divide the data set into train and test by randomly separating 8 images from stilumi and generated heatMap. Move thiese folders to the [Evaluation Data](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Prediction_and_Analysis/Evaluation_Data) directory.
6. After training, start training FiWi data by running "website_saliency_prediction_final.py", from the [same folder](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Model_Training_Scripts). 
P.S. Please check the proper paths of the FiWi dataset stimuli,generated Heatmaps and pretrained GDI model to avoid path errors.
7. Save the model (change the path for saving model) and use the saved model  by followning section B.

## D. MACHINE LEARNING ALGORITHMS FOR WEBSITE SALIENCY PREDICTION:
Run the scripts in folowing order to get the saliency predictions using random forest and SVM.

1. Run "[TestImageGenerator.ipynb"](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/blob/master/Initial_Data_Preprocessing/TestImageGenerator.ipynb) to divide the data set into train and test by randomly separating 8 images from stilumi and generated heatMap. Create two folders for the same. These 8 images can be used for predicting model's performance for unknown data.
2. Run the [saliency.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) script for the training data set. This will create folders for intensity, channel orientation and subchannel conspicuity maps. This script will also give saliency predictions as per itti et al. in a seperate folder.
3. Run the [datafilegeneration.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) to generate a data file in csv format. This file carries the information of various conspicuity maps at each pixel of images in the training set.
4. Run the [datasegregation.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) file to generate one more csv file which is used by random forest regressor and SVM for generating saliency maps.
5. Run [saliency.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) and [datafilegeneration.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) for the test data.
6. Finally, run the [svm.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) and [randomforest.py](https://github.com/Niloy-Chakraborty/Webpage_Saliency_Prediction/tree/master/Machine_Learninig_Approach) scripts to get the saliency predictions on the test dataset. 




