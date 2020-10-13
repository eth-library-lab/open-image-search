# 

To Do

[ ] create feature embeddings
[ ] compare similarity algorithms
        KNN
        Mini Batch K-Means
        Approximate Nearest Neighbors Oh Yeah (see Pratical Deep Learning, O'Reilly)

[ ] data workflow - new images, retraining comparison algorithm
    

# Possible Improvements

[ ] scalability & speed
    search algo: Annoy or NMSLIB
[ ] accuracy
    - better pretrained model
    - finetuning
    - different architecture
[ ] improve UI


# Resources


1. https://www.oreilly.com/library/view/practical-deep-learning/9781492034858/ch04.html

Practical Deep Learning for Cloud, Mobile, and Edge
by Anirudh Koul, Siddha Ganju, Meher Kasam
Released October 2019
Publisher(s): O'Reilly Media, Inc.
ISBN: 9781492034865



# Papers

## image retrieval

https://paperswithcode.com/task/image-retrieval



### Recognizing Art Style Automatically in painting with deep learning
Proceedings of the Ninth Asian Conference on Machine Learning 2017 • Adrian Lecoutre • Benjamin Negrevergne • Florian Yger

https://github.com/bnegreve/rasta](https://github.com/bnegreve/rasta

http://proceedings.mlr.press/v77/lecoutre17a/lecoutre17a.pdf


The artistic style (or artistic movement) of a painting is a rich descriptor that captures both visual and historical information about the painting. Correctly identifying the artistic style of a paintings is crucial for indexing large artistic databases. In this paper, we investigate the use of deep residual neural to solve the problem of detecting the artistic style of a painting and outperform existing approaches by almost 10% on the Wikipaintings dataset (for 25 dierent style). To achieve this result, the network is rst pre-trained on ImageNet, and deeply retrained for artistic style. We empirically evaluate that to achieve the best performance, one need to retrain about 20 layers. This suggests that the two tasks are as similar as expected, and explain the previous success of hand crafted features. We also demonstrate that the style detected on the Wikipaintings dataset are consistent with styles detected on an independent dataset and describe a number of experiments we conducted to validate this approach both qualitatively and quantitatively.
<hr>

### Large-scale Classification of Fine-Art Paintings: Learning The Right Metric on The Right Feature

http://proceedings.mlr.press/v77/lecoutre17a/lecoutre17a.pdf

Abstract. In the past few years, the number of fine-art collections that are digitized and publicly available has been growing rapidly. With the availability of
such large collections of digitized artworks comes the need to develop multimedia systems to archive and retrieve this pool of data. Measuring the visual similarity between artistic items is an essential step for such multimedia systems, which
can benefit more high-level multimedia tasks. In order to model this similarity
between paintings, we should extract the appropriate visual features for paintings
and find out the best approach to learn the similarity metric based on these features. We investigate a comprehensive list of visual features and metric learning
approaches to learn an optimized similarity measure between paintings. We develop a machine that is able to make aesthetic-related semantic-level judgments,
such as predicting a painting’s style, genre, and artist, as well as providing similarity measures optimized based on the knowledge available in the domain of art
historical interpretation. Our experiments show the value of using this similarity
measure for the aforementioned prediction tasks.

<hr>