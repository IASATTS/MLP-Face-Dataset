import os.path

pathLabels = "./datasets/dataset/train/labels"

class_labels_count = {}

for dirpath, dirs, files in os.walk(pathLabels):	
    for filename in files: 
        file_path = os.path.join(dirpath, filename)
        
        _, ext = os.path.splitext(file_path)
        if (filename == "labels.txt" or ext == ".zip" or ext == ".rar"):
            continue
        
        try:
            with open(file_path, "r") as f:
                for line in f.readlines():
                    label_class = line.split(" ")[0]
                    
                    if (label_class == "-1"):
                        test = ""
                    
                    class_count = class_labels_count.get(label_class)
                    if(class_count == None):
                        class_count = 0
                        
                    class_labels_count[label_class] = class_count + 1
        except Exception as inst:
            print("Error", inst)
        
        print(f'file {filename} processed; Total : {class_labels_count}') 

print(f'Final total : {class_labels_count}') 