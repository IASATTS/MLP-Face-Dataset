from PIL import Image
import os.path
import glob

pathLabels = "./labels/no_ts/"
pathImages = "./images/crop_no_ts/"

small_labels = []

def detectSmallLabels(args, imageFilePath):
    img = Image.open(imageFilePath)
    img_width, img_height = img.size
    
    #label_class = args[0]
    perc_width = args[3]
    perc_height = args[4]
    
    final_width = img_width * float(perc_width)
    final_height = img_height * float(perc_height)
    
    final_rectangle = final_width * final_height
    
    msg = "Final rectangle size: " + str(int(final_rectangle)) + "; Image: " + file_path
    
    print(msg)
    
    if (final_rectangle < 100):
        small_labels.append(msg)

 #Find the image corresponding to the given label.
def getImageFromFilename(filename):
    image_name = filename.split(".")[0]
    
    # Try to find a matching image for the label, continue the loop if no match is found.
    matchingImages = glob.glob(pathImages + image_name + ".*")
    
    if (len(matchingImages) == 0):
        return None
    
    return matchingImages[0]

for dirpath, dirs, files in os.walk(pathLabels):	
    for filename in files: 
        file_path = os.path.join(dirpath, filename)
        
        _, ext = os.path.splitext(file_path)
        if (filename == "labels.txt" or ext == ".zip" or ext == ".rar"):
            continue
        
         #Find the image corresponding to the given label.
        imageFilePath = getImageFromFilename(filename)
        if (imageFilePath is None):
            continue    
        
        try:
            with open(file_path, "r") as f:
                for line in f.readlines():
                    args = line.split(" ")
                    
                    detectSmallLabels(args, imageFilePath)
                    
        except Exception as inst:
            print("Error", inst)
        
        print(f'file {filename} processed; Total : {len(small_labels)}') 

print(small_labels) 