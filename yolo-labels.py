from PIL import Image

from os import listdir
from os.path import isfile, join
import pandas as pd
import os.path
import shutil
import random
import PIL

# Specify the required size of the dataset, equals to number of files in image folder if = None
datasetSize = None 
classLabel = "0"

ponies = pd.read_csv("derpi_faces.csv")

pathImages = "./images/crop/"
pathLabels = "./images/crop/labels/"
pathDataset = "./datasets/dataset/" # Warning : pathDataset will also set the path to the training+validation folder in the YAML file. That path will be used when training the final yolov5 model.

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

def write_labels(row):
    filename = row['id'].split('/')[-1]
    fid = filename.split(".")[0]

    print("Image id %s, face %s" % (row['id'], row['index']))
    try:
        newFilePath = pathLabels + fid + ".txt"
        fileExists = os.path.isfile(newFilePath)
        center_x, center_y, w, h = get_yolo_label(pathImages + filename, int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']))
        
        with open(newFilePath, "a+") as f:
            label = " ".join([classLabel, str(center_x), str(center_y), str(w), str(h)])
            
            if(fileExists == True):
                f.write("\n")
                
            f.write(label)

    except Exception as inst:
      print("Error", inst)

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

ponies.apply(write_labels, axis=1)

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
test_size = int(0.1 * datasetSize)
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