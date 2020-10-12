### IMAGE PROCESSING

import os
import numpy as np
from PIL import Image
import tensorflow as tf
from typing import List, Optional, Text, Tuple



def get_list_of_files_in_dir(fldr_path, file_types = ['jpg', 'jpeg','png'], keep_fldr_path=True):
    """
    file_types: 'all' or list of allowed file endings
    keep_fldr_path: boolean, if false the input fldr_path prefix will be removed from the returned list entries
    """

    existing_flist = []

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath,fname)
            
            if keep_fldr_path == False:
                cur_fpath = cur_fpath.replace(fldr_path, '').strip('/').strip('\\')
            
            if file_types == 'all':
                existing_flist.append(cur_fpath)
            elif fname.split('.')[-1].lower() in file_types:
                existing_flist.append(cur_fpath)
    
    print("found {:d} existing images".format(len(existing_flist)))
    
    return existing_flist
    
### IMAGE PROCESSING

def parse_image_func(filepath, label):
    
    """filename: string tensor
    label: string tensor"""
    
    image_string = tf.io.read_file(filepath)
    image = tf.image.decode_jpeg(image_string)
    image = tf.image.convert_image_dtype(image, tf.float32)
    #images have been resized to 224 in data cleaning/prep
    image = tf.image.resize(image, [224, 224])

    return image, label


def augment_func(image, label): #add a dictionary for kwargs
    
    image = tf.image.random_flip_up_down(image)
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta=32.0 / 255.0)
    image = tf.image.random_saturation(image, lower=0.5, upper=1.5) 
    image = tf.image.random_contrast(image, 0.75, 1.25)
    
    image = tf.image.resize_with_crop_or_pad(image, 336, 336)
    image = tf.image.random_crop(image, size=[224, 224, 3])
    #Make sure the image is still in [0, 1]
    #image = tf.clip_by_value(image, 0.0, 1.0) can't clip as values are normalized around 0
    
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
    
#     if conv_color=='hsv':
#         dataset = dataset.map(conv_hsv, num_parallel_calls=32) #num_parallel_calls=32

#     if conv_color=='gray':
#         dataset = dataset.map(conv_gray, num_parallel_calls=32) #num_parallel_calls=32

#     if conv_color=='yiq':
#         dataset = dataset.map(conv_yiq, num_parallel_calls=32) #num_parallel_calls=32


    if for_training:
        dataset = dataset.repeat()

    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(1)
    
    return dataset


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