# Webpage_Saliency_Prediction

In this project, we have done a focused study on the saliency analysis for webpages using FiWi dataset and propose a Fully Convolutional Network (FCN) based architecture to predictthe saliency of webpages. Given an input Webpage image, the proposed model is capable of generating its saliency map.


P.S. This whole project has been tested on Google Colab.

# Guidelines to use this Repository

## REQUIREMENTS:
To avoid version conflicts, install tensorflow version 1.15.0, keras version 2.2.5

## USING PRE-TRAINED MODEL FOR SALIENCY ANALYSIS:
1. Download this repository
2. Download the Pre-trained model for FCN-16s from https://drive.google.com/open?id=1x1vT0dWqRruLUoPpcWI3yj04i8Dahfq0
3. Run .\Webpage_Saliency_Prediction\Prediction_and_Analysis\Model_Performance_on_Test_Images.ipynb

### P.S. For computing AUC, CC and NSS scores, codes are provided in "Prediction_and_Analysis" folder. From "Evaluation Metric Scripts" run the auc_calculation.py for computing AUC score, and cross_correlation_and_nss_calculation.py for calculating CC/NSS score    




