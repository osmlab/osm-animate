import os
import glob
from bs4 import BeautifulSoup
import re
from dateutil import parser
from dateutil import relativedelta
import subprocess
import sys

## input settings
osm_file = str(sys.argv[1])
place_name = str(sys.argv[2]) ## for the directories and gif

## make a directory just for this to contain the mess; there's probably a better way to move the working directory then how I've handled below, that can be a future improvement
if not os.path.exists(place_name):
    os.makedirs(place_name)

## use snap.c to convert osm file to format suitable for datamaps
os.system("cat " + osm_file + " | ./snap > " + place_name +"/datamapfile")

## use beautiful soup to get timestamps from osm file and set frames (should ideally be done in C but I don't know how)

soup = BeautifulSoup(open(osm_file))

ways = soup.find_all('way')
rows = []
print "There are " + repr(len(ways))+ " ways"
for way in ways:
    rows.append([way['id'],way['timestamp'],0])

rs = sorted(rows, key=lambda x: x[1])
for row in rs:
    rd = relativedelta.relativedelta(parser.parse(row[1]),parser.parse(rs[0][1]))
    row[2] = rd.years * 12 + rd.months

total_frames = max(rs, key = lambda x: x[2])[2]
## there has to be a better way to do this next part but I wrote it on a plane with no access to stack-overflow
date_list = []
for i in range(total_frames+1):
    list_year = (parser.parse(rs[1][1]) + relativedelta.relativedelta(months=i)).year
    list_month = (parser.parse(rs[1][1]) + relativedelta.relativedelta(months=i)).month
    date_list.append(str(list_year) + "-" + str(list_month).zfill(2))

## set zoom and bounding box according to defaults or passed arguments
if len(sys.argv) < 4:
    bounds = soup.find('bounds')
    min_lat = bounds['minlat']
    min_lon = bounds['minlon']
    max_lat = bounds['maxlat']
    max_lon = bounds['maxlon']
    zoom_level = '12'
elif len(sys.argv) < 5:
    zoom_level = str(sys.argv[3])
else:
    zoom_level = str(sys.argv[3])
    min_lat = str(sys.argv[4])
    min_lon = str(sys.argv[5])
    max_lat = str(sys.argv[6])
    max_lon = str(sys.argv[7])

## use above info to save each frame as a separate file
with open(place_name + "/datamapfile") as f:
    lines = f.readlines()
    for i in range(0,total_frames):
        output = []
        ## create temp array of ids that match this frame
        flt = filter(lambda x: x[2] == i,rs)
        flt_ids = [flt[j][0] for j in range(0,len(flt))]
        ## iterate over lines and check ids against fitered list
        for line in lines:
            if (re.search("id=(\d+)",line).group(1) in flt_ids):
                output.append(line)
        g = open(place_name + "/frame_" + repr(i+1).zfill(4), 'w')
        g.write(''.join(output))
        g.close()

## get the frames
frame_list = glob.glob(place_name + "/frame*")

## encode
for index, file in enumerate(frame_list):
    os.system("cat " + file + " | ./encode -o \"" + place_name + "/" + str(index+1) +"\" -z " + zoom_level)

## render
for d in range(1,total_frames+1):
    os.system("./render -t 0 -A -- \"" + place_name + "/" + str(d) + "\" " + zoom_level + " " + min_lat + " " + min_lon + " " + max_lat + " " + max_lon + " > " + place_name + "/" + str(d).zfill(4) +".png")

## get png size
image_output = subprocess.check_output(["identify", place_name + "/0001.png"])
ps_width = re.search("PNG (\d+)x\d+",image_output).group(1)
ps_height = re.search("PNG \d+x(\d+)",image_output).group(1)

## make labels and join them to their image buddy
for i in range(1,total_frames+1):
    fr = str(i).zfill(4)
    os.system("convert -size " + ps_width + "x50 -gravity center -background black -stroke white -fill white label:'" + place_name + " " + date_list[i] + "' " + place_name + "/" + fr + "_label.png")
    os.system("convert -append " + place_name + "/" + fr +".png " + place_name + "/" + fr + "_label.png " + place_name + "/frame" + fr + ".png")

## create a starter black frame
os.system("convert -size " + ps_width + "x" + str(int(ps_height) + 50) + " canvas:black " + place_name + "/" + "frame0000.png")

## animate
os.system("convert -coalesce -dispose 1 -delay 20 -loop 0 " + place_name + "/frame*.png " + place_name + "/" + place_name + ".gif")

## redo the gif with pause at the end
os.system("convert " + place_name + "/" + place_name + ".gif \( +clone -set delay 500 \) +swap +delete " + place_name + "/" + place_name + ".gif")
