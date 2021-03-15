import preprocess_images
import calculate_features
import train_similarity_search


# If preprocessing images
# put them in a folder in raw

preprocess_images.main()
calculate_features.main()
train_similarity_search.main()
# If input csv with ids & fpaths

# else if input folder of images

# make a dataframe to pass