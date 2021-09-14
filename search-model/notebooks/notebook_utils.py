import numpy as np
import pandas as pd
import os
from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from textwrap import wrap


def get_model_id_list(df, record_id_list):
    model_id_lst = []
    for record in record_id_list:
        model_id_idx = df.loc[df['record_id']==record].index.tolist() #135484
        if len(model_id_idx) == 0:
            print('RecordID not found: ',record)
        model_id_lst = model_id_lst + model_id_idx
    return model_id_lst

def plot_query_imgs(df, model_id_lst):
    # check that the file paths are correct
    for model_id in model_id_lst:  
        img_fpth = df["fpath"][model_id]
        #Image.open(img_fpth)
        img = plt.imread(img_fpth)
        plt.imshow(img)
        plt.show()

def clean_record_list(df, record_id_list):
    #for record in record_id_list:
        #result = df.loc[df['record_id']==record]
        #if record in [282489,282491]:
        #    print(result)
        #if len(result) == 0:
        #if record not in df['record_id']:
        #    record_id_list.remove(record)
    #print([int(x) in df['record_id'].values for x in record_id_list if x in [20655,17537,2453]])
    new_record_id_list = [x for x in record_id_list if x in df['record_id'].values]
    return new_record_id_list
        
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
    df_fpath['record_id'] = df_fpath['record_id'].str.split(
        pat=".", n=1, expand=True)[0]
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
    df_fpath["record_id"] = df_fpath["record_id"].astype(int)
    df = df_fpath.merge(df_meta, how="left", on="record_id")
    df.index.rename("model_id", inplace=True)
    return df_feat, df


def plot_similar_images(model_id, df, results, show_plots=True, save_figures=False):
    """
    model_id: list with the model ids of query images
    df: df with image metadata
    results: dataframe with searched image metadata 
    """

    # look up true image
    true_metadata = df.loc[model_id, :]
    true_img_path = df.iloc[model_id, 0]

    # plot results
    num_plots = min(len(results), 20)
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


def plot_realted_images(record_id, df, show_plots=True, save_figures=False):
    """
    record_id: list of record IDs of related artworks
    df: df with image metadata
    """
    model_id = get_model_id_list(df, record_id)
    
    # look up true image
    true_metadata = df.loc[model_id, :]
    true_img_path = df.iloc[model_id, 0]
    
    # plot results
    num_plots = min(len(true_img_path), 20)
    fig, axs = plt.subplots(nrows=num_plots, ncols=1,
                            figsize=(8, int(num_plots*4)))

   # show related images
    for i, (idx, row) in enumerate(true_metadata.iterrows()):

        axs[i].set_title(str(i+1) + ': ' + row['title'])
        im = plt.imread(row['fpath'])
        # axs[i+1].axis('off')
        axs[i].imshow(im)

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
         for i, (idx, row) in enumerate(true_metadata.iterrows())]


def plot_similar_images_in_pairs(record_id, results1, results2, show_plots=True, save_figures=False):
    """
    record_id: list of record IDs of related artworks
    df: df with image metadata
    """

    # plot results
    num_plots = min(len(results1), 20)
    fig, axs = plt.subplots(nrows=num_plots, ncols=2,
                            figsize=(8, int(num_plots*4)))

    # show similar images
    #for i, (idx, row) in enumerate(results_list1.iterrows()):
    for i, ((_,row1),(_,row2)) in enumerate(zip(results1.iterrows(),results2.iterrows())):

        axs[i,0].set_title("\n".join(wrap(str(i+1) + ': ' + row1['title'],35)))#, wrap=True
        axs[i,1].set_title("\n".join(wrap(str(i+1) + ': ' + row2['title'],45)))

        im1 = plt.imread(row1['fpath'])
        im2 = plt.imread(row2['fpath'])
        # axs[i+1].axis('off')
        axs[i,0].imshow(im1)
        axs[i,1].imshow(im2)

    for ax_r in axs:
        for ax_c in ax_r:
            ax_c.set_xticks([])
            ax_c.set_yticks([])

    for i in range(2):
        for sp_name in axs[0,i].spines:

            axs[0,i].spines[sp_name].set_visible(True)
            axs[0,i].spines[sp_name].set_linewidth(3)


    fig.tight_layout()
    if show_plots:
        plt.show()

    if save_figures:
        fldr = os.path.join("..", "data", "interim", "test_images")
        if not os.path.exists(fldr):
            os.makedirs(fldr)

        fig_fname = '{}: {}.png'.format(record_id, results1['title'])
        fig_fpath = os.path.join(fldr, fig_fname)
        fig.savefig(fig_fpath)
    '''
    _ = [print(str(i+1), ': ', row['recordURL'])
         for i, (idx, row) in enumerate(results1.iterrows())]
    '''    