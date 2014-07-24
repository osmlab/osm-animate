import os
import glob
import csv
from bs4 import BeautifulSoup

osm_file = "/Users/andrewbollinger/Downloads/ghaziabadmap.osm"

## use snap.c to convert osm file to format suitable for datamaps
os.system("cat " + osm_file + " | ./snap > datamapfile")

## use beautiful soup to get timestamps from osm file (should ideally be done in C but I don't know how)

soup = BeautifulSoup(open(osm_file))
headers = [u'id',u'ts']

ways = soup.find_all('way')
rows = []
print "There are " + repr(len(ways))+ " ways"
for way in ways:
    rows.append([way['id'],way['timestamp']])

with open("ts_match.csv","wb") as f:
  writer = csv.writer(f)
  writer.writerow(headers)
  writer.writerows(row for row in rows)

## recreate my R script here: needs to assign a frame for each id, save each frame as a separate file

file_list = glob.glob() ## get the frames

## encode
for index, file in enumerate(file_list):
    os.system("cat " + file + " | ./encode -o \"" + str(index+1) +"\" -z 16")

## get the encoded directories
dirs = os.listdir()

## render
for d in dirs:
    os.system("./render -t 0 -A -- \"" + d + "\" 12 28.4 77.1 28.9 77.4 > " + d.zfill(4) +".png") ## need to dynamically produce the bounding box

## animate
os.system("convert -coalesce -dispose 1 -delay 20 -loop 0 *.png " + place_nameg + ".gif")
