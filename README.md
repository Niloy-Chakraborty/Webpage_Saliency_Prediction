# Webpage_Saliency_Prediction

In this project, we have done a focused study on the saliency analysis for webpages using FiWi dataset and propose a Fully Convolutional Network (FCN) based architecture to predictthe saliency of webpages. Given an input Webpage image, the proposed model is capable of generating its saliency map.


P.S. This whole project has been tested on Google Colab.

# Guidelines to use this Repository

## A. REQUIREMENTS:
To avoid version conflicts, install tensorflow version 1.15.0, keras version 2.2.5

## B. USING PRE-TRAINED MODEL FOR SALIENCY ANALYSIS:
1. Download this repository
2. Download the Pre-trained model for FCN-16s from https://drive.google.com/open?id=1smxAlcvbkOpRBQb4ClfcAkgfaub6aMgo
3. Run .\Webpage_Saliency_Prediction\Prediction_and_Analysis\Model_Performance_on_Test_Images.ipynb
4. For computing AUC, CC and NSS scores, codes are provided in "Prediction_and_Analysis" folder. From "Evaluation Metric Scripts" run the auc_calculation.py for computing AUC score, and cross_correlation_and_nss_calculation.py for calculating CC/NSS score.

## C. FOR TRAINING MODEL WITH YOUR OWN DATA:
1. Download GDI dataset from https://github.com/cvzoya/visimportance/tree/master/data
2. Download FiWi dataset from https://www-users.cs.umn.edu/~qzhao/webpage_saliency.html
3. From "Model Training Scripts" folder, start training GDI model at first by running "GDI_FCN_TRAIN.ipynb" . 
Alternatively this pre-trained model can be downloaded from https://drive.google.com/open?id=1-MKN-nQj6NOX-J9P9UOqp5mjqfMynWcC
4. Run "heatmapGeneration.py" from Initial_Data_Preprocessing folder for generating Heatmaps from eye fixation data.  
5. After training, start training your FiWi data by running "website_saliency_prediction_final.py", from the same folder. Please check the proper path of the FiWi dataset,generated Heatmaps and pretrained GDI model to avoid path errors.
6. Use the saved model followning previous section B.

## D. MACHINE LEARNING ALGORITHMS FOR WEBSITE SALIENCY PREDICTION:






