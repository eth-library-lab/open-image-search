 ### IMAGE PROCESSING

import os
import shutil
import numpy as np
import pandas as pd
from PIL import Image
import tensorflow as tf
from typing import List, Optional, Text, Tuple
from datetime import datetime as dt
import csv
import logging
import urllib
from io import BytesIO
import settings

import matplotlib.pyplot as plt
import matplotlib.style as style

from tensorflow.python.client import device_lib
import seaborn as sns
from sklearn.preprocessing import MultiLabelBinarizer

def init_logging(log_fpath=None):

    log_format = (
        '[%(asctime)s] %(levelname)-4s %(name)-8s %(message)s')

    if log_fpath==None:
        log_fpath = '../logs/downloads.log'
    
    prep_dir(log_fpath)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        filename=(log_fpath))
    
    return


def drop_nans_and_duplicates(df):
    rows_input = df.shape[0]

    # drop NaN's
    fltr = df.isna().any(axis=1)
    df = df.loc[~fltr,:]
    # drop duplicates
    df = df.drop_duplicates()

    rows_dropped = rows_input -  df.shape[0]

    print(f"dropped {rows_dropped} due NaN's or duplicates")
    
    return df




def prep_dir(fpath):
    """
    check if the folders in the fpath path exist.
    create them is not
    """
    
    dir_path = os.path.dirname(fpath) 

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return fpath


def log_status_at_interval(i, total_steps, interval=100, _log=True, _print=False):
    #print intermittent milestones to console & log
    if i % interval == 0:
        percent_complete = i/total_steps
        msg = 'currently processing {} of {} ({:0.1%} complete)'.format(i, total_steps, percent_complete)

        if _log:
            logging.info(msg)
        if _print:
            print(msg)


def list_files_in_dir(fldr_path):
    """
    return a list of filepaths for all filers in a give directory
    fldr_path: string, relative path to folder
    """
    existing_flist = []

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath, fname)
            existing_flist.append(cur_fpath)
    
    return existing_flist


def download_image(filepath, url):

    """ requests image from given url and saves it in original quality as jpeg in RGB format
    
    filename: local filepath to save the image to
    url: url to request image from"""
    
    if os.path.exists(filepath):
        logging.info('Image %s already exists. Skipping download.' % filepath)
        return

    try:
        response = urllib.request.urlopen(url)
    except:
        logging.warning('Warning: Could not download image %s from %s' % (filepath, url))
        return

    try:
        pil_image = Image.open(BytesIO(response.read()))
    except:
        logging.warning('Warning: Failed to parse image %s' % filepath)
        return

    try:
        pil_image_rgb = pil_image.convert('RGB')
    except:
        logging.warning('Warning: Failed to convert image %s to RGB' % filepath)
        return

    try:
        pil_image_rgb.save(filepath, format='JPEG')  # , quality=95
    except:
        logging.warning('Warning: Failed to save image %s' % filepath)
        return

      

def time_stamp():
    return dt.now().strftime('%Y%m%d%H%M')


def get_list_of_files_in_dir(fldr_path, file_types = ['jpg', 'jpeg','png'], keep_fldr_path=True):
    """
    file_types: 'all' or list of allowed file endings
    keep_fldr_path: boolean, if false the input fldr_path prefix will be removed from the returned list entries
    """

    existing_flist = []

    #list_dir = [os.path.isfile(os.path.join('.', f)) for f in os.listdir(fldr_path)]
    #print(all(list_dir))

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath,fname)
            #print(fname)
            
            if keep_fldr_path == False:
                cur_fpath = cur_fpath.replace(fldr_path, '').strip('/').strip('\\')
            
            if file_types == 'all':
                existing_flist.append(cur_fpath)
            elif (fname.split('.')[-1].lower() in file_types) and ('.ipynb_checkpoints' not in cur_fpath):
                existing_flist.append(cur_fpath)
    
    print("{:,} files found in directory".format(len(existing_flist)))
    
    return existing_flist
    
### IMAGE PROCESSING

def parse_image_func(filepath, label):
    
    """filename: string tensor
    label: string tensor"""
    
    image_string = tf.io.read_file(filepath)
    image = tf.image.decode_jpeg(image_string)
    image = tf.image.convert_image_dtype(image, tf.float32)
    #images normally have been resized to 224 in data cleaning/prep
    #images with size 320 are used for models like inception 
    image = tf.image.resize(image, [settings.img_min_dimension, settings.img_min_dimension])

    return image, label

def calc_rgb_means(img):
    
    r = np.mean(img[:,:,0])
    g = np.mean(img[:,:,1])
    b = np.mean(img[:,:,2])

    return r, g, b


def calc_rgb_std(img):
    
    r = np.std(img[:,:,0])
    g = np.std(img[:,:,1])
    b = np.std(img[:,:,2])

    return r, g, b


def calc_image_means(image_paths):
    
    """
    calculates the mean and standard deviation of pixels 
    image_paths: an iterable list of image filepaths    
    returns: tuple ((R_mean, G_mean, B_mean), (R_std, G_std, B_std))
    """
    
    R_mean = []
    G_mean = []
    B_mean = []
    
    R_std = []
    G_std = []
    B_std = []
    
    num_images = len(image_paths)
    print('calculating mean and stdev RGB values for {:,} images'.format(num_images))
    
    for i, image_path in enumerate(image_paths):
        try:
            img = np.array(Image.open(image_path))
        except:
            print('could not open image: ', image_path)
        
        
        r, g, b = calc_rgb_means(img)
        R_mean.append(r)
        G_mean.append(g)
        B_mean.append(b)
        
        r, g, b = calc_rgb_std(img)
        R_std.append(r)
        G_std.append(g)
        B_std.append(b)
        
        # print_dyn_progress_bar(num_images, i) # can't import?
        
    R_mean = np.mean(R_mean)
    G_mean = np.mean(G_mean)        
    B_mean = np.mean(B_mean)
    
    R_std = np.mean(R_std)
    G_std = np.mean(G_std)        
    B_std = np.mean(B_std)
    
    return ([R_mean, G_mean, B_mean], [R_std, G_std, B_std])


class ImageNormalizer():
    """
    class based implenetation of tensorflow's image normalization function. 
    allows rgb mean and stddev parameters to be defined on a init, and then the normalize_images method 
    can be passed into tf.datasets.map
    """

    def __init__(self,
                mean_rgb_values :Tuple[float, ...]=[0,0,0],
                stddev_rgb_values:Tuple[float, ...]=[1,1,1],
                num_channels: int=3,
                dtype: tf.dtypes.DType=tf.float32,
                data_format: Text='channels_last'):
        
        self.mean_rgb_values = mean_rgb_values
        self.stddev_rgb_values = stddev_rgb_values
        self.num_channels = num_channels
        self.dtype = dtype
        self.data_format = data_format
        
        
    def normalize_images(self,
                         features: tf.Tensor, 
                         label) -> tf.Tensor:
        
        """Normalizes the input image channels with the given mean and stddev.
        Args:
          features: `Tensor` representing decoded images in float format.
          mean_rgb: the mean of the channels to subtract.
          stddev_rgb: the stddev of the channels to divide.
          num_channels: the number of channels in the input image tensor.
          dtype: the dtype to convert the images to. Set to `None` to skip conversion.
          data_format: the format of the input image tensor
                       ['channels_first', 'channels_last'].
        Returns:
          A normalized image `Tensor`.
        """

        if self.data_format == 'channels_first':
            stats_shape = [self.num_channels, 1, 1]
        else:
            stats_shape = [1, 1, self.num_channels]

        if self.dtype is not None:
            features = tf.image.convert_image_dtype(features, dtype=self.dtype)

        mean_rgb = tf.constant(self.mean_rgb_values,
                                 shape=stats_shape,
                                 dtype=features.dtype)
        mean_rgb = tf.broadcast_to(mean_rgb, tf.shape(features))
        features = features - mean_rgb

        stddev_rgb = tf.constant(self.stddev_rgb_values,
                                 shape=stats_shape,
                                 dtype=features.dtype)
        stddev_rgb = tf.broadcast_to(stddev_rgb, tf.shape(features))
        features = features / stddev_rgb

        return features, label
    

    
def make_tfdataset_from_df(df,
                           filepath_col_name, 
                           label_col_name,
                           batch_size=32,
                           for_training=False,
                           normalize=True,
                           augment=False,
                           augment_func=None,
                           rgb_values=([0,0,0],[1,1,1]),
                           conv_color='rgb'):
    
    """
    rgb_values: a tuple of lists containing first the 
    mean rgb values and then the std dev of rgb values for the training dataset
    """

    file_list = df[filepath_col_name].to_list()
    label_list = df[label_col_name].to_list()
    
    dataset = tf.data.Dataset.from_tensor_slices((file_list, label_list))

    if for_training:
        dataset = dataset.shuffle(buffer_size=2048)
    
    #load and decode image
    dataset = dataset.map(parse_image_func, num_parallel_calls=32)
    
    #perform data_augmentation
    if for_training and augment:
        dataset = dataset.map(augment_func, num_parallel_calls=32)

    if normalize:
        im_normer = ImageNormalizer(mean_rgb_values=rgb_values[0], 
                                    stddev_rgb_values=rgb_values[1])
        dataset = dataset.map(im_normer.normalize_images, num_parallel_calls=32)
    
    if conv_color=='rgb':
        pass

    if for_training:
        dataset = dataset.repeat()

    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(1)
    
    return dataset

def make_df_file_list(input_image_dir, keep_full_path=False, use_relative_path=True):

    if use_relative_path:
        rel_path = os.path.relpath(input_image_dir, start = os.curdir)
        rel_path += '/'         
        keep_full_path=False

    else:
        rel_path=''

    lst_fpaths = get_list_of_files_in_dir(input_image_dir, 
                                          file_types = ['jpg', 'jpeg','png','bmp'], 
                                          keep_fldr_path=keep_full_path )


    df = pd.DataFrame({'file_path':lst_fpaths})
    df['file_path'] = rel_path + df['file_path']

    return df

def print_dyn_progress_bar(total, i):
    """print a progress bar in a single line to monitor a for loop """
    
    barwidth = 50

    percent_complete = (i+1)/total
    completed = int(percent_complete * barwidth)
    remaining = barwidth - completed 
    
    bar_str = "\r[{}{}{}] {:0.2%}".format('-'*completed,
                                          '>',
                                          ' '*remaining,
                                          percent_complete )
    print(bar_str, end='')   
    
    return


def load_features(fpath):
    """
    load the csv of image features calculated by the tf model  
    """
    
    
    with open(fpath,'r') as dest_f:
        data_reader = csv.reader(dest_f,
                               delimiter = ',')
        #next(data_reader) #skips the header/first line
        data = [data for data in data_reader]

    data_array = np.asarray(data)
    labels = data_array[:,0].astype(str)
    features_list = data_array[:,1:].astype(np.float32).tolist()

    return labels, features_list 


def move_file(orig_fpath, new_fpath):

    try:
        utils.prep_dir(new_fpath)
        shutil.move(orig_fpath, new_fpath)
    except Error as e:
        print("could not move: ", orig_fpath, "\n", e)
        
    return


def get_file_modified_time(fpath):
    
    statbuf = os.stat(fpath)
    f_mod_time = statbuf.st_mtime
    
    return f_mod_time


def is_file_older_than(fpath, **timedelta_args):
     
    mod_time = get_file_modified_time(fpath)
    
    now = dt.datetime.now()
    time_limit = now - dt.timedelta(**timedelta_args)
    
    print("mod_time: ", dt.datetime.utcfromtimestamp(mod_time))
    print("time_limit: ",time_limit)
    time_limit = time_limit.timestamp()

    return mod_time < time_limit


@tf.function
def macro_soft_f1(y, y_hat):
    """Compute the macro soft F1-score as a cost (average 1 - soft-F1 across all labels).
    Use probability values instead of binary predictions.
    
    Args:
        y (int32 Tensor): targets array of shape (BATCH_SIZE, N_LABELS)
        y_hat (float32 Tensor): probability matrix from forward propagation of shape (BATCH_SIZE, N_LABELS)
        
    Returns:
        cost (scalar Tensor): value of the cost function for the batch
    """
    y = tf.cast(y, tf.float32)
    y_hat = tf.cast(y_hat, tf.float32)
    tp = tf.reduce_sum(y_hat * y, axis=0)
    fp = tf.reduce_sum(y_hat * (1 - y), axis=0)
    fn = tf.reduce_sum((1 - y_hat) * y, axis=0)
    soft_f1 = 2*tp / (2*tp + fn + fp + 1e-16)
    cost = 1 - soft_f1 # reduce 1 - soft-f1 in order to increase soft-f1
    macro_cost = tf.reduce_mean(cost) # average on all labels
    return macro_cost

@tf.function
def macro_f1(y, y_hat, thresh=0.5):
    """Compute the macro F1-score on a batch of observations (average F1 across labels)
    
    Args:
        y (int32 Tensor): labels array of shape (BATCH_SIZE, N_LABELS)
        y_hat (float32 Tensor): probability matrix from forward propagation of shape (BATCH_SIZE, N_LABELS)
        thresh: probability value above which we predict positive
        
    Returns:
        macro_f1 (scalar Tensor): value of macro F1 for the batch
    """
    y_pred = tf.cast(tf.greater(y_hat, thresh), tf.float32)
    tp = tf.cast(tf.math.count_nonzero(y_pred * y, axis=0), tf.float32)
    fp = tf.cast(tf.math.count_nonzero(y_pred * (1 - y), axis=0), tf.float32)
    fn = tf.cast(tf.math.count_nonzero((1 - y_pred) * y, axis=0), tf.float32)
    f1 = 2*tp / (2*tp + fn + fp + 1e-16)
    macro_f1 = tf.reduce_mean(f1)
    return macro_f1


def get_available_devices():
    '''
    check if GPU is ready for tensorflow
    '''
    local_device_protos = device_lib.list_local_devices()
    # tf.debugging.set_log_device_placement(True)
    return [x.name for x in local_device_protos]

def show_img(X_train, y_train):
    '''
    display images in dataset with labels
    '''
    nobs = 4  # Maximum number of images to display
    ncols = 4  # Number of columns in display
    nrows = nobs//ncols  # Number of rows in display

    style.use("default")
    plt.figure(figsize=(12, 4*nrows))
    for i in range(nrows*ncols):
        ax = plt.subplot(nrows, ncols, i+1)
        plt.imshow(Image.open(X_train[i]))
        plt.title('\n{}\n{}\n'.format(X_train[i], y_train[i]), fontsize=10)
        plt.axis('off')
    plt.show()


def process_metadata(fpath):
    '''
    read metadata csv file and group rare labels
    '''
    meta_df = pd.read_csv(fpath)

    # Remove rows having missing Tags
    meta_df.dropna(subset=['Tags'], inplace=True)
    print("Total number of prints: ", meta_df.shape[0])

    # Edit image path
    meta_df['Image Location'] = meta_df['Image Location'].str.replace('images', settings.raw_image_dir)

    # find all labels with freq less than threshold
    label_freq_all = meta_df['Tags'].apply(lambda s: str(s).split(
        '|')).explode().value_counts().sort_values(ascending=False)
    #print("Total number of unqiue labeles: ", len(label_freq_all))
    threshold = 30
    rare = list(label_freq_all[label_freq_all < threshold].index)

    # categrorize all rare labels into 'others'
    meta_df['Tags'] = meta_df['Tags'].apply(
        lambda s: [l if l not in rare else 'others' for l in str(s).split('|')])

    return meta_df
    #print("We will be ignoring ",len(rare)," rare labels that appears less than ",threshold, " times:", rare)
    # print(label_freq_all[-300:])
    # only plot the top 100 labels
    #label_freq = label_freq_all[:100]


def plot_labels(meta_df):
    '''
    plot histogram of top frequency labels
    '''

    label_freq_clean = meta_df['Tags'].explode().value_counts().sort_values(ascending=False)
    print("Final number of unqiue labeles after cleaning: ", len(label_freq_clean))
    # only plot the top 100 labels
    label_freq = label_freq_clean[:100]

    # Bar plot
    style.use("fivethirtyeight")
    plt.figure(figsize=(22, 20))
    sns.barplot(y=label_freq.index.values,
                x=label_freq, order=label_freq.index)
    plt.title("Frequency of Top 100 Label", fontsize=14)
    plt.xlabel("")
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.show()


def transform_labels(y_train, y_val):
    '''
    transform object labels into one-hot encoding format
    '''
    # Fit the multi-label binarizer on the training set
    mlb = MultiLabelBinarizer()
    mlb.fit(y_train)

    N_LABELS = len(mlb.classes_)

    '''# Loop over all labels and show them
    print("Labels:")
    N_LABELS = len(mlb.classes_)
    for (i, label) in enumerate(mlb.classes_):
        print("{}. {}".format(i, label))
    '''

    # transform the targets of the training and test sets
    y_train_bin = mlb.transform(y_train)
    y_val_bin = mlb.transform(y_val)

    return y_train_bin, y_val_bin, N_LABELS, mlb



def learning_curves(history):
    """Plot the learning curves of loss and macro f1 score 
    for the training and validation datasets.

    Args:
        history: history callback of fitting a tensorflow keras model 
    """

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    macro_f1 = history.history['macro_f1']
    val_macro_f1 = history.history['val_macro_f1']

    epochs = len(loss)

    style.use("bmh")
    plt.figure(figsize=(8, 8))

    plt.subplot(2, 1, 1)
    plt.plot(range(1, epochs+1), loss, label='Training Loss')
    plt.plot(range(1, epochs+1), val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')

    plt.subplot(2, 1, 2)
    plt.plot(range(1, epochs+1), macro_f1, label='Training Macro F1-score')
    plt.plot(range(1, epochs+1), val_macro_f1,
             label='Validation Macro F1-score')
    plt.legend(loc='lower right')
    plt.ylabel('Macro F1-score')
    plt.title('Training and Validation Macro F1-score')
    plt.xlabel('epoch')

    plt.show()

    return loss, val_loss, macro_f1, val_macro_f1


def print_time(t):
    """Function that converts time period in seconds into %h:%m:%s expression.
    Args:
        t (int): time period in seconds
    Returns:
        s (string): time period formatted
    """
    h = t//3600
    m = (t % 3600)//60
    s = (t % 3600) % 60
    return '%dh:%dm:%ds' % (h, m, s)


def show_prediction_imgLoc(img_loc, meta_df, model, mlb, prob_thre):

    # Get print info
    img_path = img_loc
    labels = meta_df.loc[meta_df['Image Location'] == img_loc]['Tags'].iloc[0]

    # Read and prepare image
    img = tf.keras.preprocessing.image.load_img(img_path)
    img = tf.keras.preprocessing.image.img_to_array(img)
    # Resize it to fixed shape
    image_resized = tf.image.resize_with_pad(
        img, settings.img_size, settings.img_size)
    img = image_resized/255
    img = np.expand_dims(img, axis=0)

    # Generate prediction
    prob = [prob for prob, prediction in sorted(
        zip(model.predict(img)[0], mlb.classes_), reverse=True) if prob > prob_thre]
    prediction = [prediction for prob, prediction in sorted(
        zip(model.predict(img)[0], mlb.classes_), reverse=True) if prob > prob_thre]
    pred_prob = [[prediction, prob] for prob, prediction in sorted(
        zip(model.predict(img)[0], mlb.classes_), reverse=True) if prob > prob_thre]
    print(pred_prob)


    # Dispaly image with prediction
    style.use('default')
    #plt.subplot(1, 2, 1)
    plt.figure(figsize=(8, 4))
    plt.imshow(Image.open(img_path))
    plt.title('\n\n{}\n\nGroundtruth\n{}\n\n'.format(
        img_path, labels), fontsize=9)

    #plt.subplot(1, 2, 2)
    if prob != []:
        plt.figure(figsize=(8, 4))
        sns.barplot(y=prob,
                    x=prediction)
        plt.title("Prediction", fontsize=14)
        plt.xlabel("")
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.show()
