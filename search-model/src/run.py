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
    
    # clean the csv of metadata
    clean_metadata.main()

    # calculate features from images in in the data/processed directory ( settings.processed_image_dir)
    if settings.calculate_features:
        calculate_features.main()
    # make KNN model
    if settings.create_retrieval_model:
        train_similarity_search.main()

    # process the metadata
    # load from a folder of csv's
    process_metadata.main()

    return 1

if __name__ == "__main__":

    main()