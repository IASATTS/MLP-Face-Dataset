from PIL import Image

from os import listdir
from os.path import isfile, join
import pandas as pd
import os.path
import shutil
import random
import PIL
import copy

# Specify the required size of the dataset, equals to number of files in image folder if = None
datasetSize = None 
classLabel = "0"

ponies = pd.read_csv("derpi_faces.csv")

pathImages = "./images/crop/"
pathLabels = "./images/crop/labels/"
pathDataset = "./datasets/dataset/" # Warning : pathDataset will also set the path to the training+validation folder in the YAML file. That path will be used when training the final yolov5 model.

file_labels = {}

def get_yolo_label(filename, xmin, ymin, xmax, ymax):
    print(filename)
    img = Image.open(filename)

    width, height = img.size
    w = xmax - xmin
    h = ymax - ymin

    center_x, center_y = (xmax - w//2), (ymax - h//2)
    
    w_fraction = w / width
    h_fraction = h / height
    center_x_fraction = center_x / width
    center_y_fraction = center_y / height

    return center_x_fraction, center_y_fraction, w_fraction, h_fraction

def write_labels(fid, rows):
    #filename = row['id'] #.split('/')[-1]
    #fid = filename.split(".")[0]
    try:
        newFilePath = pathLabels + fid + ".txt"
        
        # Create or overwrite the file
        with open(newFilePath, "w+") as f:
            
            # Write the label for each row
            for idx, row in enumerate(rows):
                print("Image id %s, face %s" % (row['id'], row['index']))
                
                filename = row['id']
                center_x, center_y, w, h = get_yolo_label(pathImages + filename, int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']))
                
                label = " ".join([classLabel, str(center_x), str(center_y), str(w), str(h)])
                f.write(label)
                
                if idx < len(rows) - 1:
                    f.write("\n")

    except Exception as inst:
      print("Error", inst)
      
def build_label_dict(row):
    
    #if row['id'] == '2296799.png':
    #    f = ''

    filename = row['id'] #.split('/')[-1]
    fid = filename.split(".")[0]

    fileExists = os.path.isfile(pathImages + filename)
    if not fileExists:
        return

    if(file_labels.get(fid) == None):
        file_labels[fid] = []

    width = row['xmax'] - row['xmin'] 
    height = row['ymax'] - row['ymin'] 

    currentRows = file_labels[fid]
    skipCurrentRow = False
    
    for prevRow in currentRows:
        prevWidth = prevRow['xmax'] - prevRow['xmin'] 
        prevHeight = prevRow['ymax'] - prevRow['ymin'] 
        
        # If both rows references the same object in the same image, only keep one of them.
        if prevRow['index'] == row['index'] :
            # Replace the previous row with the current one if the current one is smaller.
                # Otherwise, skip the current row.
            if width < prevWidth or height < prevHeight:
                currentRows.remove(prevRow)
                print("Replaced row id %s, face %s" % (row['id'], row['index']))
            else:
                skipCurrentRow = True
                print("Skipped row id %s, face %s" % (row['id'], row['index']))
       
    if not skipCurrentRow:
        newRow = {'id': row['id'], 'index': row['index'], 'xmin': row['xmin'], 'xmax': row['xmax'], 'ymin': row['ymin'], 'ymax': row['ymax']}
        currentRows.append(newRow)
        print("Added row id %s, face %s" % (row['id'], row['index']))

def create_dataset_folders():
    create_folder(pathDataset + "train/images")
    create_folder(pathDataset + "train/labels")
    create_folder(pathDataset + "validation/images")
    create_folder(pathDataset + "validation/labels")
    create_folder(pathDataset + "test/images")
    create_folder(pathDataset + "test/labels")
    
def create_folder(path):
    os.makedirs(path, exist_ok=False)

ponies = ponies.sample(frac=1).reset_index(drop=True)

# Create labels folder
try:
    shutil.rmtree(pathLabels)
    os.mkdir(pathLabels)
except:
    print("Labels folder doesn't exist")
    os.mkdir(pathLabels)

ponies.apply(build_label_dict, axis=1)

# Write the labels for each file.

for key, value in file_labels.items():
    write_labels(key, value)

# -------------------------
# Sepparate in 3 datasets
# -------------------------

# Create dataset folder
try:
    shutil.rmtree(pathDataset)
    create_dataset_folders()
except:
    print("Dataset folder doesn't exist")
    create_dataset_folders()

_, _, files = next(os.walk(pathImages))

# datasetSize = all images if not specified.
if(datasetSize is None):
    datasetSize = len(files)

validation_size = int(0.1 * datasetSize)
test_size = int(0 * datasetSize)
train_size = int(datasetSize - validation_size - test_size)

random.shuffle(files)
files = files[:datasetSize]

x = 0

# Separate the dataset into folder using the chosen split
print("Separate into folders")
for filename in files: 
    if(x < train_size):
        pathDest = pathDataset + "train/"
    elif(x < (train_size + validation_size)):
        pathDest = pathDataset + "validation/"
    else:
        pathDest = pathDataset + "test/"
    
    shutil.copyfile(pathImages + filename, pathDest + "images/" + filename)
    
    #original = PIL.Image.open(pathImages + filename)
    #original.save(pathDest + "images/" + filename, format="png", quality=100)
    
    labelFilename = filename.split(".")[0] + ".txt"
    shutil.copyfile(pathLabels + labelFilename, pathDest + "labels/" + labelFilename)
    
    print("Processed image " + str(x))
    x = x + 1
    
# Create data.yaml
with open(pathDataset + "data.yaml", "w+") as f:
    path =  os.path.abspath(pathDataset).replace("\\","/")
    f.write("train: " + path + "/train/images\n")
    f.write("val: " + path + "/validation/images\n")
    f.write("\n")
    f.write("nc: 2\n")
    f.write("names: ['ts', 'other']")
    
print("Dataset creation done")