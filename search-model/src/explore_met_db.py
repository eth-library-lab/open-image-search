import logging
import os
import warnings
#import utils
from utils import *
import settings

from matplotlib import pyplot as plt
from matplotlib import style as style
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from datetime import datetime
import time
from tf_explain.callbacks.grad_cam import GradCAMCallback

# check if GPU os availabel for tensorflow 
print(get_available_devices())

fpath = settings.metadata_csvs
MODEL_NAME = ''.join(map(str, settings.model_name.split('_')[:-1]))
IMG_SIZE = settings.img_min_dimension
CHANNELS = 3


meta_df = process_metadata(fpath)
# plot_labels(meta_df)

# split dataset into training and validation set
X_train, X_val, y_train, y_val = train_test_split(
    meta_df['Image Location'], meta_df['Tags'], test_size=0.2, random_state=44)

y_train_bin, y_val_bin, N_LABELS, mlb = transform_labels(y_train, y_val)


def parse_function(filename, label):
    """Function that returns a tuple of normalized image array and labels array.
    Args:
        filename: string representing path to image
        label: 0/1 one-dimensional array of size N_LABELS
    """
    # Read an image from a file
    image_string = tf.io.read_file(filename)
    # Decode it into a dense vector
    image_decoded = tf.image.decode_image(image_string, channels=CHANNELS)
    # Resize it to fixed shape
    image_resized = tf.image.resize_with_pad(image_decoded, IMG_SIZE, IMG_SIZE)

    # Normalize it from [0, 255] to [0.0, 1.0]
    image_normalized = image_resized / 255.0

    return image_normalized, label


BATCH_SIZE = settings.batch_size  # Big enough to measure an F1-score
# Adapt preprocessing and prefetching dynamically
AUTOTUNE = tf.data.experimental.AUTOTUNE


def create_dataset(filenames, labels, augment, is_training=True):
    """Load and parse dataset.
    Args:
        filenames: list of image paths
        labels: numpy array of shape (BATCH_SIZE, N_LABELS)
        is_training: boolean to indicate training mode
    """
    # Create a first dataset of file paths and labels
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    # Parse and preprocess observations in parallel
    dataset = dataset.map(parse_function, num_parallel_calls=AUTOTUNE)
    # Batch the data for multiple steps
    dataset = dataset.batch(BATCH_SIZE)
    dataset = dataset.shuffle(buffer_size=256)
    
    '''
    if augment:
        data_augmentation = tf.keras.Sequential([
            layers.experimental.preprocessing.RandomFlip("horizontal"),
            layers.experimental.preprocessing.RandomTranslation(height_factor=(-.1, .1),width_factor=(-.1, .1)),
            ])
        dataset = dataset.map(lambda x, y: (data_augmentation(x, training=True), y), 
                    num_parallel_calls=AUTOTUNE)
    '''
    # Fetch batches in the background while the model is training.
    dataset = dataset.prefetch(buffer_size=AUTOTUNE)

    return dataset


train_ds = create_dataset(X_train, y_train_bin, augment=True)
val_ds = create_dataset(X_val, y_val_bin, augment=False)

for f, l in train_ds.take(1):
    print("Shape of features array:", f.numpy().shape)
    print("Shape of labels array:", l.numpy().shape)


@tf.autograph.experimental.do_not_convert 
def build_model(modelURL,dropout):    
    '''
    build model based on a pre-trained feature extractor from tfhub.
    Args:
        modelURL: url of selected feature extractor from https://tfhub.dev/s?module-type=image-feature-vector&tf-version=tf2
                    possible choices are: mobilenet: https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4 resnet50: https://tfhub.dev/google/imagenet/resnet_v2_50/feature_vector/5 inception: https://tfhub.dev/google/imagenet/inception_v3/feature_vector
        dropout: dropout rate of the last hidden layer
    '''
    feature_extractor_layer = hub.KerasLayer(modelURL, 
                                        input_shape=(IMG_SIZE,IMG_SIZE,CHANNELS))
    model = tf.keras.Sequential([
        feature_extractor_layer,
        layers.Dense(1024, activation='relu', name='hidden_layer'),
        layers.Dropout(dropout),
        layers.Dense(N_LABELS, activation='sigmoid', name='output')
        ])
    feature_extractor_layer.trainable = True

    print(model.summary())

    return model


def build_model_keras(model_name, dropout):
    '''
    build model based on a pre-trained Keras model.
    Args:
        model_name: name of the pre-trained Keras model
        dropout: dropout rate of the last hidden layer
    '''
    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    data_augmentation = tf.keras.Sequential([
        layers.experimental.preprocessing.RandomFlip("horizontal"),
        layers.experimental.preprocessing.RandomTranslation(
            height_factor=(-.1, .1), width_factor=(-.1, .1)),
    ])
    x = data_augmentation(inputs)
    preprocess_input = tf.keras.applications.resnet50.preprocess_input
    x = preprocess_input(x)

    if model_name == "vgg16":
        model_backbone = tf.keras.applications.VGG16(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        conv_layer = 'block5_conv3'
    elif model_name == "vgg19":
        model_backbone = tf.keras.applications.VGG19(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    elif model_name == "resnet50":
        model_backbone = tf.keras.applications.resnet50.ResNet50(include_top=False, input_tensor=x)
        #model_backbone = tf.keras.applications.resnet50.ResNet50(include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        conv_layer = 'conv5_block3_out'
    elif model_name == "resnet_V2":
        model_backbone = tf.keras.applications.resnet_v2.ResNet152V2(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        conv_layer = 'conv5_block3_out'
    elif model_name == "inception_resnet":
        model_backbone = tf.keras.applications.inception_resnet_v2.InceptionResNetV2(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    elif model_name == "inception_v3":
        model_backbone = tf.keras.applications.inception_v3.InceptionV3(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        conv_layer = 'activation_93'
    elif model_name == "xception":
        model_backbone = tf.keras.applications.xception.Xception(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    elif model_name == "mobilenet":
        model_backbone = tf.keras.applications.mobilenet.MobileNet(
            include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        conv_layer = 'conv_pw_13_relu'
    else:
        print("Feature extraction model Unrecognised")

    model_backbone.trainable = False
    feature_extractor_layer = model_backbone.layers[-1].output
    # need to change pooling layer type based on selected model
    gap = tf.keras.layers.GlobalAveragePooling2D()(feature_extractor_layer)

    hidden_layer = layers.Dense(1024, activation='relu')(gap)
    dropout_layer = layers.Dropout(dropout)(hidden_layer)
    prediction = layers.Dense(N_LABELS, activation='sigmoid')(dropout_layer)
    #model = tf.keras.Model(inputs=model_backbone.inputs, outputs=prediction)
    model = tf.keras.Model(inputs=inputs, outputs=prediction)

    print(model.summary())

    return model, conv_layer


def create_heatmap_val_set(X_val, y_val, mlb, label):
    '''
    Select a subset of the validation data to examine heatmaps
    Return:
        heatmap_validation_class: processed iamge arraies
        label_index: index of the query label
        val_img_paths: list of image locations
    '''
    # choose 5 images with the query label in tags
    val_img_paths = [el for el, labels in zip(X_val, y_val)
                     if label in labels][:5]

    validation_img_class = []
    for path in val_img_paths:
        img = tf.keras.preprocessing.image.load_img(
            path, target_size=(224, 224))
        array = tf.keras.preprocessing.image.img_to_array(img)
        validation_img_class.append(array)

    heatmap_validation_class = (validation_img_class, None)
    label_index = np.where(mlb.classes_ == label)[0][0]

    return heatmap_validation_class, label_index, val_img_paths


@tf.autograph.experimental.do_not_convert
def train_model(model, lr, epochs, save, heatmap_val_class, label_index, conv_layer, loss=macro_soft_f1):

    val_ds = create_dataset(X_val, y_val_bin, augment=False)

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='loss', patience=4, restore_best_weights=True
)   
    
    heatmap_fld = './heatmap/' + MODEL_NAME
    
    # tf-explain heatmap grad cam callback
    gradcam = GradCAMCallback(
        validation_data=heatmap_validation_class,
        layer_name=conv_layer,
        class_index=label_index,  # 183:Men
        output_dir=heatmap_fld,
    )
   
    tensorboard_callback = tf.keras.callbacks.TensorBoard("logs")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss=loss,
        metrics=[macro_f1])

    start = time.time()
    model.fit(train_ds,
              epochs=epochs, callbacks=[
                  early_stopping, gradcam, 
                  tensorboard_callback],
              validation_data=val_ds, verbose=1)
    
    # save trained model 
    if save:
        fname = MODEL_NAME + "_lr" + \
            str(lr) + '_epoch' + str(epochs) + "_batch" + str(BATCH_SIZE)
        model.save(os.path.join('saved_model/', fname))
        fpath = os.path.join('saved_model/', 'model_summary.txt')

        with open(fpath,'w') as f:
            f.write("Model Version Name: {} \n".format(fname))
            # Pass the file handle in as a lambda function to make it callable
            model.summary(print_fn=lambda x: f.write(x + '\n'))

    print('\nTraining took {}'.format(print_time(time.time()-start)))

    return model


model, conv_layer = build_model_keras(MODEL_NAME, dropout=0.5)  # mobilenet  inception_v3
#modelURL = 'https://tfhub.dev/google/imagenet/resnet_v2_50/feature_vector/5' 
#model = build_model(modelURL, dropout=0.5)
heatmap_validation_class, label_index, val_img_paths = create_heatmap_val_set(
    X_val, y_val, mlb, 'Men')
model = train_model(model, lr=5e-4, epochs=50, save=True,
                    heatmap_val_class=heatmap_validation_class, label_index=label_index, conv_layer=conv_layer)  # mobilenet inception_v3
#losses, val_losses, macro_f1s, val_macro_f1s = learning_curves(history)
for t in val_img_paths:
    show_prediction_imgLoc(t, meta_df, model, mlb, prob_thre=0.5)
