import pandas as pd
import os.path
import shutil
import random
import pathlib
import glob
 
create_dataset_folder = False

# Specify the required size of the dataset, equals to number of files in image folder if = None
datasetSize = None 

pathImages = "./images/crop_ts_and_others/"
pathLabelsRoot = "./labels/ts_and_others/"
pathDataset = "./datasets/dataset/" # Warning : pathDataset will also set the path to the training+validation folder in the YAML file. That path will be used when training the final yolov5 model.

def create_dataset_folders():
    create_folder(pathDataset + "train/images")
    create_folder(pathDataset + "train/labels")
    create_folder(pathDataset + "validation/images")
    create_folder(pathDataset + "validation/labels")
    create_folder(pathDataset + "test/images")
    create_folder(pathDataset + "test/labels")
    
def create_folder(path):
    os.makedirs(path, exist_ok=False)

 #Find the image corresponding to the given label.
def getImageFromFilename(filename):
    image_name = filename.split(".")[0]
    
    # Try to find a matching image for the label, continue the loop if no match is found.
    matchingImages = glob.glob(pathImages + image_name + ".*")
    
    if (len(matchingImages) == 0):
        return None
    
    return matchingImages[0]

# -------------------------
# Sepparate in 3 datasets
# -------------------------

# Create dataset folder
if (create_dataset_folder):
    try:
        shutil.rmtree(pathDataset)
        create_dataset_folders()
    except:
        print("Dataset folder doesn't exist")
        create_dataset_folders()

labels = []

# Go through all the labels in the given path, recursively
for dirpath, dirs, files in os.walk(pathLabelsRoot):	
    for filename in files: 
        file_path = os.path.join(dirpath, filename)
        
        _, ext = os.path.splitext(file_path)
        if (filename == "labels.txt" or ext == ".zip" or ext == ".rar"):
            continue
        
        labels.append((filename, dirpath + "/"))

# datasetSize = all images if not specified.
if(datasetSize is None):
    datasetSize = len(labels)

validation_size = int(0.1 * datasetSize)
test_size = int(0.05 * datasetSize)
train_size = int(datasetSize - validation_size - test_size)

random.shuffle(labels)
labels = labels[:datasetSize]

x = 0

# Separate the dataset into folder using the chosen split
print("Separate into folders")
for labelFileName, labelPath in labels: 
    #Find the image corresponding to the given label.
    imageFilePath = getImageFromFilename(labelFileName)
    if (imageFilePath is None):
        continue   

    imageFileName = os.path.basename(imageFilePath)
    
    if(x < train_size):
        pathDest = pathDataset + "train/"
    elif(x < (train_size + validation_size)):
        pathDest = pathDataset + "validation/"
    else:
        pathDest = pathDataset + "test/"
    
    # Copy the given label to the dataset labels folder
    shutil.copyfile(labelPath + labelFileName, pathDest + "labels/" + labelFileName)
    
    #original = PIL.Image.open(pathImages + filename)
    #original.save(pathDest + "images/" + filename, format="png", quality=100)
    
    # Copy the given image to the dataset images folder
    shutil.copyfile(pathImages + imageFileName, pathDest + "images/" + imageFileName)
    
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