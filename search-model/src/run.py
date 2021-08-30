import preprocess_images
import calculate_features
import train_similarity_search
import settings
import clean_metadata
import export_metadata
import process_metadata


def main():

    # preprocess images before calculating features
    if settings.preprocess_images and (settings.raw_image_dir != settings.processed_image_dir):
        preprocess_images.main()

    # calculate features from images in in the data/processed directory ( settings.processed_image_dir)
    calculate_features.main()
    # make KNN model
    train_similarity_search.main()
    # clean the csv of metadata
    clean_metadata.main()
    # process the metadata
    # load from a folder of csv's
    # process_metadata.main()
    # export the metadata to json fixtures for loading into django
    export_metadata.main()

    return 1

if __name__ == "__main__":

    main()