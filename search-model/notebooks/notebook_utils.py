import numpy as np
import pandas as pd
import os
from PIL import Image


import tensorflow as tf
import tensorflow_datasets as tfds
#import tensorflow_recommenders as tfrs
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def get_record_ids_from_features_df(df_feat):
    """
    using the df from the calculated features csv
    add a column with record ids
    return df
    """

    df_fpath = df_feat.iloc[:, [0]]
    df_fpath = df_fpath.rename(columns={0: "fpath"})
    df_fpath['record_id'] = df_fpath["fpath"].str.rsplit(
        pat="/", n=1, expand=True)[1]
    print(df_fpath['record_id'][:5])
    df_fpath['record_id'] = df_fpath['record_id'].str.split(
        pat=".", n=1, expand=True)[0]
    print(df_fpath['record_id'][:5])
    df_fpath.index.rename("model_id", inplace=True)

    return df_fpath


def process_metadata(feature_path, metadata_path):
    df_meta = pd.read_csv(metadata_path)
    df_feat = pd.read_csv(feature_path, header=None)

    df_meta = df_meta.rename(
        columns={'recordID': 'record_id', 'matTec': 'material_technique'})
    df_meta.index.rename("db_id", inplace=True)
    df_meta = df_meta.reset_index()
    df_meta["record_id"] = df_meta["record_id"].astype("Int64")

    df_fpath = get_record_ids_from_features_df(df_feat)
    # print(df_fpath.head())
    df_fpath["record_id"] = df_fpath["record_id"].astype(int)
    df = df_fpath.merge(df_meta, how="left", on="record_id")
    df.index.rename("model_id", inplace=True)
    return df_feat, df


def plot_similar_images(model_id, df, results, show_plots=True, save_figures=False):
    """
    j: index (of labels list) to look up
    df: df with image metadata
    labels: true labels. list with the object ids for all the images
    features_list: list of numpy arrays with the extracted features
    """

    # look up true image
    true_metadata = df.loc[model_id, :]
    true_img_path = df.iloc[model_id, 0]

    # look up similar images
    #distances, indices = clf_func([features_list[j]])
    #object_ids = labels[indices.tolist()[0]]
    #tdf = df.loc[object_ids,:]

    # plot results
    num_plots = min(len(results), 10)
    fig, axs = plt.subplots(nrows=1+num_plots, ncols=1,
                            figsize=(8, int(num_plots*4)))

    # show true image
    axs[0].set_title('original image: ' + true_metadata['title'],
                     fontdict={'fontweight': 750})
    # axs[0].axis('off')
    im = plt.imread(true_img_path)
    axs[0].imshow(im)
    axs[0].spines['bottom'].set_visible(True)
    axs[0].spines['bottom'].set_linewidth(3)

    # show similar images
    for i, (idx, row) in enumerate(results.iterrows()):

        axs[i+1].set_title(str(i+1) + ': ' + row['title'])
        im = plt.imread(row['fpath'])
        # axs[i+1].axis('off')
        axs[i+1].imshow(im)

    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])

    for sp_name in axs[0].spines:

        axs[0].spines[sp_name].set_visible(True)
        axs[0].spines[sp_name].set_linewidth(3)

    fig.tight_layout()
    if show_plots:
        plt.show()

    if save_figures:
        fldr = os.path.join("..", "data", "interim", "test_images")
        if not os.path.exists(fldr):
            os.makedirs(fldr)

        fig_fname = '{}: {}.png'.format(model_id, true_metadata['title'])
        fig_fpath = os.path.join(fldr, fig_fname)
        fig.savefig(fig_fpath)

    _ = [print(str(i+1), ': ', row['recordURL'])
         for i, (idx, row) in enumerate(results.iterrows())]


def plot_similar_images_t(model_id, df, results1, results2, show_plots=True, save_figures=False):
    """
    j: index (of labels list) to look up
    df: df with image metadata
    labels: true labels. list with the object ids for all the images
    features_list: list of numpy arrays with the extracted features
    """

    # look up true image
    true_metadata = df.loc[model_id, :]
    true_img_path = df.iloc[model_id, 0]

    # look up similar images
    #distances, indices = clf_func([features_list[j]])
    #object_ids = labels[indices.tolist()[0]]
    #tdf = df.loc[object_ids,:]

    # plot results
    num_plots = min(len(results1[0]), 10)
    fig, axs = plt.subplots(nrows=1+num_plots, ncols=2,
                            figsize=(8, int(num_plots*4)))
    # show true image
    axs[0, 0].set_title('original image: ' + true_metadata['title'],
                        fontdict={'fontweight': 750})
    # axs[0].axis('off')
    im = plt.imread(true_img_path)
    axs[0, 0].imshow(im)
    axs[0, 0].spines['bottom'].set_visible(True)
    axs[0, 0].spines['bottom'].set_linewidth(3)

    # show similar images of model1
    for i, (idx, row) in enumerate(results1.iterrows()):

        axs[i+1, 0].set_title(str(i+1) + ': ' + row['title'])
        im = plt.imread(row['fpath'])
        # axs[i+1].axis('off')
        axs[i+1, 0].imshow(im)

    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])

    for sp_name in axs[0].spines:

        axs[0, 0].spines[sp_name].set_visible(True)
        axs[0, 0].spines[sp_name].set_linewidth(3)

    fig.tight_layout()
    if show_plots:
        plt.show()

    if save_figures:
        fldr = os.path.join("..", "data", "interim", "test_images")
        if not os.path.exists(fldr):
            os.makedirs(fldr)

        fig_fname = '{}: {}.png'.format(model_id, true_metadata['title'])
        fig_fpath = os.path.join(fldr, fig_fname)
        fig.savefig(fig_fpath)

    _ = [print(str(i+1), ': ', row['recordURL'])
         for i, (idx, row) in enumerate(results1.iterrows())]

    # show similar images of model1
    for i, (idx, row) in enumerate(results2.iterrows()):

        axs[i+1, 1].set_title(str(i+1) + ': ' + row['title'])
        im = plt.imread(row['fpath'])
        # axs[i+1].axis('off')
        axs[i+1, 1].imshow(im)

    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])

    for sp_name in axs[0].spines:

        axs[0, 1].spines[sp_name].set_visible(True)
        axs[0, 1].spines[sp_name].set_linewidth(3)

    fig.tight_layout()
    if show_plots:
        plt.show()

    if save_figures:
        fldr = os.path.join("..", "data", "interim", "test_images")
        if not os.path.exists(fldr):
            os.makedirs(fldr)

        fig_fname = '{}: {}.png'.format(model_id, true_metadata['title'])
        fig_fpath = os.path.join(fldr, fig_fname)
        fig.savefig(fig_fpath)

    _ = [print(str(i+1), ': ', row['recordURL'])
         for i, (idx, row) in enumerate(results2.iterrows())]
