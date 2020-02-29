# -*- coding: utf-8 -*-
"""GDI_FCN_TRAIN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eV4Iqy5DHI_xwoWjOwee9R5ki5a-QVt6

# SCRIPT NAME: GDI_FCN_TRAIN.ipynb
THIS SCRIPT DOES THE FOLLOWING FUNCTIONALITIES:

          1. PRE_PROCESS GDI DATASET
          2. TRAIN THE FCN-16 MODEL ON GDI DATA
          3. Visualize training performance
          4. TEST ON THE PERFORMANCE ON TEST DATA
          5. SAVE THE MODEL FOR LATER USE
"""

# import libraries
import tensorflow
import keras
import random
import cv2, os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
from PIL import Image

# comment this part if not using google colab
# from google.colab import drive
# drive.mount('/content/drive')

"""## Data Visualisation"""

# Path to the training and testing GDI data
dir_data = "/content/drive/My Drive/HCI_prep/GDI/"

dir_seg_test = dir_data + "/gd_imp_val/"
dir_img_test = dir_data + "/gd_val/"
dir_seg_train = dir_data + "/gd_imp_train/"
dir_img_train = dir_data + "/gd_train/"

ldseg = np.array(os.listdir(dir_seg_train))
ldseg_tr = np.array(os.listdir(dir_img_train))

# pick the first image from GDI Dataset and Visualise
fnm = ldseg[0]
fnm_tr = ldseg_tr[0]

print(fnm)
print(fnm_tr)

img = mpimg.imread(dir_seg_train + fnm)
imgplot = plt.imshow(img)
plt.title("importance image for Training: GDI Dataset")
plt.show()

img = mpimg.imread(dir_img_train + fnm_tr)
imgplot = plt.imshow(img)
plt.title("original image for Training: GDI Dataset")
plt.show()

"""# Data Preprocessing"""

n_classes = 1
meanval = (104.00699, 116.66877, 122.67892)

output_width, output_height = 224, 224
input_width, input_height = 224, 224

"""
Function Name: ImageArr()
Parameters: path, width, height
Functionalities: 1) Resizing to 224*224
                 2) Mean Value Reduction
                 3) RGB to BGR conversion

Returns: preprocessed image

"""


def ImageArr(path, width, height):
    # print(path)
    img = cv2.imread(path, 1)
    img = np.float32(cv2.resize(img, (width, height)))  # / 127.5 - 1

    # Meanvalue reduction
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img -= meanval

    return img


"""
Function Name: ImpArr()
Parameters: path,class, width, height
Functionalities: 1) BGR to GRAY conversion
                 2) Resizing to 224*224
                 2) values range from 0 to 255

Returns: preprocessed ground truth

"""


def ImpArr(path, classes, width, height):
    # ACCORDIG TO THE REF PAPER
    img = cv2.imread(path, 1)

    # convert to gray image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize to 224*224
    img = cv2.resize(img, (224, 224))

    # values range from 0 to 255
    label = np.array(img, dtype=np.uint8)

    # For classifiction problem, take the values of saliency map as positive sample,
    # if the value is more than 2/3 of 255
    label = label > 255.0 * 2 / 3

    label = np.expand_dims(label, axis=-1)
    # print("aftr expanding dim",label.shape)

    return label


images_train = os.listdir(dir_img_train)
images_train.sort()
# print("sorted",images_train)

imp_train = os.listdir(dir_seg_train)
imp_train.sort()
# print("sorted",imp_train )

images_test = os.listdir(dir_img_test)
images_test.sort()
# print("sorted",images_train )

imp_test = os.listdir(dir_seg_test)
imp_test.sort()
# print("sorted",imp_test )


# Append processed image arrays in separate lists
X_train = []
X_test = []

Y_train = []
Y_test = []

for im, seg in zip(images_train, imp_train):
    X_train.append(ImageArr(dir_img_train + im, input_width, input_height))
    Y_train.append(ImpArr(dir_seg_train + seg, n_classes, output_width, output_height))

for im, seg in zip(images_test, imp_test):
    X_test.append(ImageArr(dir_img_test + im, input_width, input_height))
    Y_test.append(ImpArr(dir_seg_test + seg, n_classes, output_width, output_height))

X_tr, Y_tr = np.array(X_train), np.array(Y_train)
print(X_tr.shape, Y_tr.shape)

X_tst, Y_tst = np.array(X_test), np.array(Y_test)
print(X_tst.shape, Y_tst.shape)

"""# TRAIN-VALIDATION-TEST SPLIT
Separate 10% data from Xtst and Ytst for testing. Use rest 90% data for validation while training.
"""

from sklearn.utils import shuffle

validation_rate = 0.9
index_validation = np.random.choice(X_tst.shape[0], int(X_tst.shape[0] * validation_rate), replace=False)
# print(index_validation)
index_test = list(set(range(X_tst.shape[0])) - set(index_validation))

X2, Y2 = shuffle(X_tst, Y_tst)
X_valid, Y_valid = X2[index_validation], Y2[index_validation]
X_test, Y_test = X2[index_test], Y2[index_test]

X_tr, Y_tr = shuffle(X_tr, Y_tr)
X_test, Y_test = shuffle(X_test, Y_test)
X_valid, Y_valid = shuffle(X_valid, Y_valid)

print("X_train and y_train shape are: ", X_tr.shape, Y_tr.shape)
print("X_valid and y_valid shape are: ", X_valid.shape, Y_valid.shape)
print("X_test and y_test shape are: ", X_test.shape, Y_test.shape)

"""# FCN-16 model building"""

# import libraries for training the model
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
import keras, sys, time, warnings
from tensorflow.keras.models import *
from tensorflow.keras.layers import *
import pandas as pd

'''
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
config =  tf.compat.v1.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.95
config.gpu_options.visible_device_list = "2"
'''
set_session(tf.compat.v1.Session())

print("python {}".format(sys.version))
print("keras version {}".format(keras.__version__));
del keras
print("tensorflow version {}".format(tf.__version__))

"""
Function Name: crop()
Parameters: feature map1, feature map 2,image input
Functionalities: crop feature map1 wrt.feature map 2
Returns: cropped o1 and o2
"""


def crop(o1, o2, i):
    o_shape2 = Model(i, o2).output_shape

    if IMAGE_ORDERING == 'channels_first':
        output_height2 = o_shape2[2]
        output_width2 = o_shape2[3]
    else:
        output_height2 = o_shape2[1]
        output_width2 = o_shape2[2]

    o_shape1 = Model(i, o1).output_shape
    if IMAGE_ORDERING == 'channels_first':
        output_height1 = o_shape1[2]
        output_width1 = o_shape1[3]
    else:
        output_height1 = o_shape1[1]
        output_width1 = o_shape1[2]

    cx = abs(output_width1 - output_width2)
    cy = abs(output_height2 - output_height1)

    if output_width1 > output_width2:
        o1 = Cropping2D(cropping=((0, 0), (0, cx)),
                        data_format=IMAGE_ORDERING)(o1)
    else:
        o2 = Cropping2D(cropping=((0, 0), (0, cx)),
                        data_format=IMAGE_ORDERING)(o2)

    if output_height1 > output_height2:
        o1 = Cropping2D(cropping=((0, cy), (0, 0)),
                        data_format=IMAGE_ORDERING)(o1)
    else:
        o2 = Cropping2D(cropping=((0, cy), (0, 0)),
                        data_format=IMAGE_ORDERING)(o2)

    return o1, o2


import tensorflow.keras
from tensorflow.keras.models import *
from tensorflow.keras.layers import *

IMAGE_ORDERING = 'channels_last'

# take vgg-16 pretrained model from "https://github.com/fchollet/deep-learning-models" here
pretrained_url = "https://github.com/fchollet/deep-learning-models/" \
                 "releases/download/v0.1/" \
                 "vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5"

pretrained = 'imagenet'  # 'imagenet' if weights need to be initialized!

"""
Function Name: get_vgg_encoder()
Functionalities: This function defines the VGG encoder part of the FCN network
                 and initialize this encoder part with VGG pretrained weights.
Parameter:input_height=224,  input_width=224, pretrained=pretrained
Returns: final layer of every blocks as f1,f2,f3,f4,f5

"""


def get_vgg_encoder(input_height=224, input_width=224, pretrained=pretrained):
    pad = 1

    # heights and weights must be divided by 32, for fcn
    assert input_height % 32 == 0
    assert input_width % 32 == 0

    img_input = Input(shape=(input_height, input_width, 3))

    # Unlike base paper, stride=1 has not been used here, because
    # Keras has default stride=1

    x = (ZeroPadding2D((pad, pad), data_format=IMAGE_ORDERING))(img_input)
    x = Conv2D(64, (3, 3), activation='relu', padding='valid', name='block1_conv1', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv2', data_format=IMAGE_ORDERING)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool', data_format=IMAGE_ORDERING)(x)
    f1 = x
    # Block 2
    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv1', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv2', data_format=IMAGE_ORDERING)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool', data_format=IMAGE_ORDERING)(x)
    f2 = x

    # Block 3
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv1', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv2', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv3', data_format=IMAGE_ORDERING)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool', data_format=IMAGE_ORDERING)(x)
    x = Dropout(0.5)(x)
    f3 = x

    # Block 4
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv1', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv2', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv3', data_format=IMAGE_ORDERING)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool', data_format=IMAGE_ORDERING)(x)
    f4 = x

    # Block 5
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv1', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv2', data_format=IMAGE_ORDERING)(x)
    x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv3', data_format=IMAGE_ORDERING)(x)
    x = MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool', data_format=IMAGE_ORDERING)(x)
    # x= Dropout(0.5)(x)

    f5 = x

    # Check if weights are initialised, model is learning!
    if pretrained == 'imagenet':
        VGG_Weights_path = tensorflow.keras.utils.get_file(
            pretrained_url.split("/")[-1], pretrained_url)

        Model(img_input, x).load_weights(VGG_Weights_path)

    return img_input, [f1, f2, f3, f4, f5]


"""
Function Name: fcn_16()
Functionalities: This function defines the Fully Convolutional part of the FCN network
                 and adds skip connections to build FCN-16 network
Parameter:n_classes, encoder=get_vgg_encoder, input_height=224,input_width=224
Returns: model

"""


def fcn_16(n_classes, encoder=get_vgg_encoder, input_height=224, input_width=224):
    # Take levels from the base model, i.e. vgg
    img_input, levels = encoder(input_height=input_height, input_width=input_width)
    [f1, f2, f3, f4, f5] = levels

    o = f5

    # fcn6
    o = (Conv2D(4096, (7, 7), activation='relu', padding='same', data_format=IMAGE_ORDERING))(o)
    o = Dropout(0.5)(o)

    # fc7
    o = (Conv2D(4096, (1, 1), activation='relu', padding='same', data_format=IMAGE_ORDERING))(o)
    o = Dropout(0.3)(o)

    conv7 = (Conv2D(1, (1, 1), activation='relu', padding='same', name="score_sal", data_format=IMAGE_ORDERING))(o)

    conv7_4 = Conv2DTranspose(1, kernel_size=(4, 4), strides=(2, 2), padding='same', name="upscore_sal2",
                              use_bias=False, data_format=IMAGE_ORDERING)(conv7)

    pool411 = (
        Conv2D(1, (1, 1), activation='relu', padding='same', name="score_pool4", data_format=IMAGE_ORDERING))(f4)

    # Add a crop layer 
    o, o2 = crop(pool411, conv7_4, img_input)

    # add skip connection
    o = Add()([o, o2])

    # 16 x upsample
    o = Conv2DTranspose(n_classes, kernel_size=(32, 32), strides=(16, 16), use_bias=False, data_format=IMAGE_ORDERING)(
        o)

    # crop layer
    ## Caffe calls crop layer that takes o and img_input as argument, it takes their difference and crops
    ## But keras takes it as touple, I checked the size diff and put this value manually.
    ## output dim was 240 , input dim was 224. 240-224=16. so 16/2=8

    score = Cropping2D(cropping=((8, 8), (8, 8)), data_format=IMAGE_ORDERING)(o)

    o = (Activation('sigmoid'))(score)
    model = Model(img_input, o)

    model.model_name = "fcn_16"

    return model


# Binary classification problem with 2 classes, salient or non-salient
model = fcn_16(n_classes=1, encoder=get_vgg_encoder, input_height=224, input_width=224)

# show model summary
model.summary()

"""# Training"""

from tensorflow.keras import optimizers
from tensorflow.keras.models import load_model

# Check the layers and the weights
# Cros-validate the weights manually with the vgg weights opened with Netron API
# model.set_weights(model_pretrained)
for i, layer in enumerate(model.layers):
    print(i, layer.name)

    print(layer.get_weights())
    # print(i,layer.name)

# Freeze the first 19 layers
for layer in model.layers[:19]:
    print(layer.name)
    layer.trainable = False

# Check trainable status
for i, layer in enumerate(model.layers):
    print(i, layer.name, layer.trainable)

# Customise the optimiser

# sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
sgd = optimizers.SGD(lr=0.001, momentum=0.90, decay=5 ** (-4), nesterov=True)
adam = optimizers.Adam(learning_rate=0.0001, beta_1=0.9, beta_2=0.999, epsilon=1e-07)

# Compile the model

# Try with adam with custom sgd (SGD+nesterov) and choose the best
# default adam: lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0.
# For Loss: chcek with mse, binary crossentropy , kullback_leibler_divergence

model.compile(optimizer="sgd", loss='binary_crossentropy', metrics=['accuracy'])

# Final Summary: Check non trainable parameters
model.summary()

# fit the model

hist1 = model.fit(X_tr, Y_tr, validation_data=(X_tst, Y_tst), batch_size=24, epochs=150,
                  verbose=1)  # , callbacks=[es, mc])

# save the model

model.save("/content/drive/My Drive/HCI_prep/with_VGG_weights_gdi_fcn16_24_02_2020.h5")

# evaluate the model
saved_model = load_model("/content/drive/My Drive/HCI_prep/with_VGG_weights_gdi_fcn16_24_02_2020.h5")

_, train_acc = saved_model.evaluate(X_tr, Y_tr, verbose=0)
_, test_acc = saved_model.evaluate(X_test, Y_test, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_acc, test_acc))

"""# Visualizing the model performance"""

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
c = 0
col = ["r", "g", "b", "c"]
for key1 in ['loss', 'val_loss']:
    # print(hist1.history[key1])
    ax1.plot(hist1.history[key1], label=key1, c=col[c])
    ax1.legend(loc=2)
    c = c + 1
for key2 in ['acc', 'val_acc']:
    ax2.plot(hist1.history[key2], label=key2, c=col[c])
    ax2.legend(loc=1)
    c = c + 1

ax1.set_xlabel('epochs')
ax1.set_ylabel('Loss', color='r')
ax2.set_ylabel('Accuracy*100', color='b')
plt.savefig("/content/drive/My Drive//HCI_prep/Plot_with_VGG_weights_gdi_fcn16_24_02_2020_full.png")

"""# Test on Test images"""

# img = "/content/drive/My Drive/HCI_prep/Dataset_Website1/stimuli/coursera.png"
import cv2, os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow
import tensorflow.keras
from tensorflow.keras.models import load_model
from PIL import Image

saved_model = load_model("/content/drive/My Drive/HCI_prep/with_VGG_weights_gdi_fcn16_24_02_2020.h5")
# img_is = cv2.imread(img)

for img_is in X_test:
    # show the test image
    img_is = cv2.resize(img_is, (224, 224))
    plt.imshow(img_is)
    plt.title("test image")
    plt.show()

    # The test data was preprocessed before, so no processing is required!
    # If not preprocessed then use then use the following commented section.
    '''
  
  # Resize the image
  width, height= 224,224
  img = np.float32(cv2.resize(img_is, ( width, height))) 

  # Meanvalue reduction
  meanval=(104.00699, 116.66877, 122.67892)
  img -= meanval

  X= np.array(img)
  print(X.shape)
  #print(X)
  '''
    img = img_is.reshape(-1, 224, 224, 3)

    im_pred = saved_model.predict(img)
    print("prediction shape", im_pred.shape)
    # print(im_pred.max())
    # print(im_pred.min())
    # print(im_pred)

    rescaled_new = im_pred.reshape(224, 224, 1)
    print(rescaled_new.shape)
    # data=rescaled_new
    # print(rescaled_new)
    # rescaled = (255.0 / data.max() * (data - data.min()))
    # print(rescaled)
    # im_new = Image.fromarray(rescaled)
    # im_new.show()
    rescaled_new = cv2.resize(rescaled_new, (224, 224))
    plt.imshow(rescaled_new)
    plt.title("Importance Map")
    plt.show()
