import os

path = r"C:\Users\vince\Desktop\gef"

for root, dirnames, filenames in os.walk(path):
    for filename in filenames:
        file = os.path.join(root, filename)
        os.rename(file, file.replace(".GEF", ".gef"))