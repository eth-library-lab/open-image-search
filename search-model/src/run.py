import preprocess_images
import calculate_features
import train_similarity_search
import settings
import clean_metadata
import export_metadata
import process_metadata
import create_recommender
import download_images

def main():

    # clean the csv of metadata
    clean_metadata.main()

    # download images
    download_images.main()

    # preprocess images before calculating features
    if settings.preprocess_images and (settings.raw_image_dir != settings.processed_image_dir):
        preprocess_images.main()

    # calculate features from images in in the data/processed directory ( settings.processed_image_dir)
    if settings.calculate_features:
        calculate_features.main()

    # process the metadata
    # load from a folder of csv's
    process_metadata.main()

    # make KNN model
    if settings.create_retrieval_model:
        create_recommender.main()
    
    return 1

if __name__ == "__main__":

    main()