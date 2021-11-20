from PIL import Image
import pandas as pd
import os.path
import shutil

classLabel = "1"

ponies = pd.read_csv("derpi_faces.csv")

pathImages = "./images/crop/"
pathLabels = "./images/crop/labels/"

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

ponies = ponies.sample(frac=1).reset_index(drop=True)

# Create labels folder
try:
    shutil.rmtree(pathLabels)
    os.mkdir(pathLabels)
except:
    print("Labels folder doesn't exist")
    os.mkdir(pathLabels)

ponies.apply(build_label_dict, axis=1)

# Create labels.txt for importation in makesense.ai software
with open(pathLabels + "labels.txt", "w+") as f:
    f.write("ts\n")
    f.write("other")

# Write the labels for each file.

for key, value in file_labels.items():
    write_labels(key, value)

print("Labels created")