import numpy as np
import pandas as pd

import cv2
from PIL import Image
# import matplotlib.pyplot as plt


import os
import sys
from pathlib import Path

sys.path.append('../src')

from dotenv import load_dotenv
load_dotenv("./.env.nbsettings")


def compute_sift(img, rootsift = True):
    '''
    use sift to detect keypoints and compute descriptors
    
    inputs: 
    img: img array
    
    outputs:
    list of [kp,des]
    kp: keypoints indices ( with cv2.keypoint type)
    des: descriptors with dimension num_of_keypoints*128 
    '''
    sift = cv2.SIFT_create()
    
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #descriptors with 128 dimensons
    kp, des = sift.detectAndCompute(img, None) 
    
    # if there are no keypoints or descriptors, return an empty tuple
    if len(kp) == 0:
        return ([], None)
    
    #first L1-normalizing and taking the square-root
    if rootsift:
        eps=1e-7
        des /= (des.sum(axis=1, keepdims=True) + eps)
        des = np.sqrt(des)

    return [kp,des]


def match_sift_ransac(img1, img2, des1,des2, plot_match=False, thre = 100):
    '''
    apply ransac after keypoint descriptor matching given 2 images using brute force searching
    
    inputs: 
    img1/img2: img array of 2 images to match
    des1/des2: tuple of keypoints indices and descritptors of 2 images 
    plot_match: boolean of showing image with point matching or not
    thre: threshlod of number of matched keypoints to be considered as similar images
    
    outputs:
    number of matched keypoints
    
    '''
    
    kp1,kp2 = des1[0],des2[0]
    desp1,desp2 = des1[1],des2[1]
    
    # check if descriptor is extracted 
    if len(kp1)*len(kp2) == 0:
        return False
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(desp1,desp2,k=2)
     
    # check if NN is found
    if len(matches[0]) < 2:
        return 0

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    # skip if number of matched keypoints < thre 
    if len(good) < thre:
        return len(good)
    else:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,2.0)
        #print('Determinant of Homography: ', np.linalg.det(M))
        matchesMask = mask.ravel().tolist()
        
        # exclude images if num of inlier matched points < thre
        if sum(matchesMask) < thre:
            return sum(matchesMask)
        
        # exclude images if homography doesn't make senses
        if np.linalg.det(M) < 0.5:
            return sum(matchesMask)

        h,w = img1.shape[:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)

        img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
        
        draw_params = dict(
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

        img3 = cv2.drawMatches(img1,des1[0],img2,des2[0],good,None,**draw_params)
        # plt.imshow(cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)),plt.show()
        
        # if plot_match:
        #     fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 6))
        #     axes[0].imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
        #     axes[1].imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
        #     fig.tight_layout()
        #     plt.show()

        #plt.imshow(cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)),plt.show()
        
        print('Num of matched keypoint pairs: ', sum(matchesMask))

    return sum(matchesMask)

def ransac_filter(des1,des2, thre = 30):
    '''
    apply ransac after keypoint descriptor matching given 2 images using brute force searching
    
    inputs: 
    des1/des2: tuple of keypoints indices and descritptors of 2 images 
    thre: threshlod of number of matched keypoints to be considered as similar images
    
    outputs:
    number of matched keypoints
    
    '''
    
    kp1,kp2 = des1[0],des2[0]
    desp1,desp2 = des1[1],des2[1]
    
    # check if descriptor is extracted 
    if len(kp1)*len(kp2) == 0:
        return 0
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(desp1,desp2,k=2)
     
    # check if NN is found
    if len(matches[0]) < 2:
        return 0

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    # skip if number of matched keypoints < thre 
    if len(good) < thre:
        return 0
    else:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,2.0)
        #print('Determinant of Homography: ', np.linalg.det(M))
        matchesMask = mask.ravel().tolist()
        
        # exclude images if num of inlier matched points < thre
        if sum(matchesMask) < thre:
            return 0
        
        # exclude images if homography doesn't make senses
        if np.linalg.det(M) < 0.5:
            return 0

    return sum(matchesMask)



def create_img_id(img_path):
    img_name = img_path.rsplit("/",1)[1]
    img_id = img_name.split(".",1)[0]
    return img_id

def create_dict_of_des_by_id(search_fpaths_input, rootsift=True):
    '''
    create a dictionary with image id as key, image descriptors as values
    '''
    des_dic = {}
    for path in search_fpaths_input: 
        img_id = create_img_id(path)

        img = cv2.imread(path)
        des = compute_sift(img, rootsift=rootsift)

        # only keep descriptors
        des_dic[img_id] = des[1]
    
    return des_dic

def create_dict_of_img_by_id(search_fpaths_input):
    '''
    create a dictionary with image id as key, image array as values
    '''
    img_dic = {}
    for path in search_fpaths_input: 
        img_id = create_img_id(path)

        img = cv2.imread(path)

        img_dic[img_id] = img
    
    return img_dic

def create_dict_of_des_by_id(search_fpaths_input):
    '''
    create a dictionary with image id as key, keypoints and descriptors as values
    '''
    des_dic = {}
    for path in search_fpaths_input: 
        img_id = create_img_id(path)
        img = cv2.imread(path)

        [points,descps] = compute_sift(img, rootsift = True)

        feat_list = []
        for point,descp in zip(points, descps):
            temp = [point.pt, point.size, point.angle, point.response, point.octave, point.class_id, descp]
            feat_list.append(temp)
        des_dic[img_id] = feat_list
    return des_dic


def format_sift_features_as_list(points,descps):
    
    feat_list = []

    for point,descp in zip(points, descps):
        temp = [list(point.pt),
                point.size,
                point.angle,
                point.response,
                point.octave,
                point.class_id,
                list(descp)]
        feat_list.append(temp)

    return feat_list


def format_sift_features_as_dict(points ,descps):
    "unpack the cv2 KeyPoint objects into a list of dicts with each point type and a list of descriptors"
    points_lst = []
    descriptor_lst = []

    for point, descp in zip(points, descps):
        points_lst.append({"pt" : list(point.pt),
                "size" : point.size,
                "angle" : point.angle,
                "response" : point.response,
                "octave" : point.octave,
                "class_id" : point.class_id})
        descriptor_lst.append(list(descp))

    return {"points":points_lst, "descriptors":descriptor_lst}