# credits to trevorfiez and Owen Jow for the origin version of The Met Image Downloader in this repo:
# https://github.com/trevorfiez/The-Metropolitan-Museum-of-Art-Image-Downloader

##### Notebook to download Met painting images by artist name, type, or a list of object numbers #####
#run this line to download all open access prints in Met collection:
# python3 met_download.py --csv=MetObjects.csv --out=images/ --type="Print"

#example artwork page: https://www.metmuseum.org/art/collection/search/841336


import urllib3
import sys
import getopt
import csv
import os
import httplib2
from selenium import webdriver
import shutil


def check_artists(artist, artists):
    if (len(artists) == 0):
        return True
    else:
        return artist in artists


def check_types(piece_type, types):
    if (len(types) == 0):
        return True
    else:
        return piece_type in types


def check_object_num(object_num, num_list):
    return object_num in num_list


def match_lines(met_csv, artists, types, list_file):
    '''
    search the Met metadata csv file for artworks that match the given query
    '''
    lines = []

    print(artists)
    # download images if the list is given
    if (list_file != ""):
        f = open(list_file, 'r')
        obj_num_list = []
        for line in f:
            obj_num_list.append(line.strip())

        for row in met_csv:
            if (check_object_num(row[0], obj_num_list)):
                lines.append(row)
        #print(lines)
    else:
        for row in met_csv:
            #check if artist/type match
            if (check_artists(row[18], artists) and check_types(row[8], types)):
                lines.append(row)

    return lines

  
def download_lines(lines, out_dir, met_csv):
    '''
    find the image link from each artwork page to download the image
    '''

    image_names = []

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # init the csv file to store metadata of downloaded images 
    if not os.path.exists(os.path.join(out_dir, "piece_info.csv")):
        with open(os.path.join(out_dir, "piece_info.csv"), 'w') as csv_file:
            im_writer = csv.writer(csv_file, delimiter=',')

            for row in met_csv:
                im_writer.writerow(row + ['Image Location'])
                break
    else:

        # Note: you will need geckodriver and firefox web browser
        # See https://pypi.org/project/selenium.
        driver = webdriver.Firefox()
        for line in lines:
            res = ""

            with open(os.path.join(out_dir, "piece_info.csv"), 'rt') as csv_file:
                # skip images that has been downloaded
                im_reader = csv.reader(csv_file, delimiter=',')
                for row in im_reader:
                    #print("line: ", line[4])
                    #print("row: ", row[4])
                    if line[4].strip() == row[4].strip():
                        image_names.append(row[-1])
                        print("Image already downloaded: ", image_names[-1])
                        break
                else:
                    try:
                        # go to the individual page for artwork 
                        obj_url = 'http://www.metmuseum.org/art/collection/search/' + line[4].strip()
                        driver.get(obj_url) #objectID column
                        html = driver.page_source
                    except urllib3.exceptions.EmptyPoolError:
                        image_names.append(None)
                        print("URL Error")
                        continue
                    # find the image url from the artwork page
                    offset = html.find(
                        "artwork__interaction artwork__interaction--download")

                    if (offset == -1):
                        image_names.append(None)
                        continue
                    offset = html[offset:].find('http') + offset
                    if html[offset:].find('.bmp') != -1:
                        end = html[offset:].find('.bmp') + offset + 4
                    elif html[offset:].find('.JPG') != -1:
                        end = html[offset:].find('.JPG') + offset + 4   
                    elif html[offset:].find('.jpg') != -1:
                        end = html[offset:].find('.jpg') + offset + 4
                    
                    else:
                        print("Image Not Found")
                        
                    #print("offset: ", offset)
                    #print("end: ", end)

                    if (end - offset > 300):
                        image_names.append(None)
                        print("Image Downloading URL Error: ", obj_url)
                        print(html[offset:end])
                        continue

                    image_link = html[offset:end]
                    image_link = image_link.replace("original", "web-large")
                    #print(image_link)

                    image_name = image_link.split('/')[-1]

                    image_path = os.path.join(out_dir, image_name)

                    image_file = ""
                    try:
                        http = urllib3.PoolManager()
                        image_file = http.request("GET", image_link)
                    
                    # alternative image link if the 1st url doesn't work
                        if image_file.status == 404:
                            offset = html.find("artwork__image gtm__artwork__image")
                            if (offset == -1):
                                print('Image Not Found')
                                continue
                            offset = html[offset:].find('http') + offset
                            end = html[offset:].find('main-image') + offset + 10
                            image_link = html[offset:end]
                            image_file = http.request("GET", image_link)

                    except (urllib3.exceptions.EmptyPoolError, httplib2.HttpLib2Error):
                        image_names.append(None)
                        print("URL error")
                        continue


                    with http.request('GET', image_link, preload_content=False) as resp, open(image_path, 'wb') as out_file:
                        shutil.copyfileobj(resp, out_file)
                    image_file.release_conn()

                    image_names.append(image_path)

                    if (image_names[-1] == None):
                        continue
                    
                    # write artwork metadata into csv
                    with open(os.path.join(out_dir, "piece_info.csv"), 'a') as csv_file:
                        im_writer = csv.writer(csv_file, delimiter=',')
                        im_writer.writerow(line + [image_names[-1]])

                    print(image_link)

    return image_names


def main(argv):
    opts, args = getopt.getopt(
        argv, "i:o:a:t:l:", ["csv=", "out=", "artist=", "type=", "list="])

    met_csv_file = ""
    out_dir = ""
    list_file = ""
    artists = []

    types = []

    for opt, arg in opts:
        if opt in ("--csv", "-i"):
            met_csv_file = arg
        elif opt in ("--out", "-o"):
            out_dir = arg
        elif opt in ("--artist", "-a"):
            artists = arg.split(':')
        elif opt in ("--type", "-t"):
            types = arg.split(":")
        elif opt in ("--list", "-l"):
            list_file = arg

    # need metadata csv file created by The Met which can be downloaded here: https://github.com/metmuseum/openaccess
    met_csv = csv.reader(open(met_csv_file, 'r'), delimiter=',')

    csv_lines = match_lines(met_csv, artists, types, list_file)

    lines = 0
    for line in csv_lines:
        lines += 1

    print(lines)

    download_lines(csv_lines, out_dir, met_csv)


if __name__ == "__main__":
    main(sys.argv[1:])
