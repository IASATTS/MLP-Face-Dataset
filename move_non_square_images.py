from PIL import Image
import os.path
import glob
import shutil

pathImages = "./images/test/"
non_squares_folder = pathImages + "non_squares/"

non_squares = []

def moveNonSquare(imageFilePath):
    try:
        # filename not an image file
        img = Image.open(imageFilePath)
        img_width, img_height = img.size
        
        proportion = 0
        if (img_width <= img_height):
            proportion = img_width / img_height
        else:
            proportion = img_height / img_width
        
        is_rectangle = proportion >= 0.85
       
        img.close() 
       
        msg = "Final rectangle proportion: " + str(proportion) + "; Image: " + imageFilePath
        
        print(msg)
        
        if (is_rectangle == False):
            non_squares.append(msg)
            imageFileName = os.path.basename(imageFilePath)
            path_dest = non_squares_folder + imageFileName
            shutil.move(imageFilePath, path_dest)
    except IOError as e:
        print("Image error : " + imageFilePath + "; " + e)

try:
    shutil.rmtree(non_squares_folder)
    os.makedirs(non_squares_folder, exist_ok=False)
except:
    print("non_squares folder folder doesn't exist")
    os.makedirs(non_squares_folder, exist_ok=False)

_, _, files = next(os.walk(pathImages))

for filename in files:	
    file_path = os.path.join(pathImages, filename)
    
    _, ext = os.path.splitext(file_path)
    if (ext != ".jpg" and ext != ".jpeg" and ext != ".png" and ext != ".gif"):
        continue
    
    moveNonSquare(file_path)
    
    print(f'file {filename} processed; Total : {len(non_squares)}') 

print(non_squares) 