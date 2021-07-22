#### notebook for finding corrupted images in scrapped dataset and write their object numbers in a csv file ####
# to download using the correct image url for images on the list, run met_download.py with --list = err_img_list.csv #

from os import listdir
from PIL import Image
import csv
import sys
import io
cnt = 0

with open("err_img_list.csv", 'w') as csv_file:
    im_writer = csv.writer(csv_file)

# loop through image dataset
for filename in listdir('./images'):
    if filename.endswith(('.jpg','.JPG','bmp')):
        try: #test if the image is valid
            img = Image.open('./images/'+filename)
            img.verify()

        except (IOError, SyntaxError) as e: #find corrupted images
            cnt=cnt+1 # count the number of corrupted images
            print('Bad file:', 'images/' + filename)
            # find object numbers of the corrupted images
            piece_csv = csv.reader(open('piece_info.csv', 'r'), delimiter=',')
            for row in piece_csv:
                if str('images/' + filename) == row[-1]:
                    # write object numbers into a csv file  
                    with open("err_img_list.csv", 'a') as csv_file:
                        im_writer = csv.writer(csv_file)
                        im_writer.writerow([row[0]])
                
#print(cnt)
