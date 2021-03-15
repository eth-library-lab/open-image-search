import preprocess_images
import calculate_features
import train_similarity_search
import settings

# preprocess images before calculating features
if settings.preprocess_images and (settings.raw_image_dir != settings.processed_image_dir):
    preprocess_images.main()

# calculate features from images in in the data/processed directory ( settings.processed_image_dir)
calculate_features.main()
# make KNN model
train_similarity_search.main()
