import os
from PIL import Image

def resize_images_in_folder(root_folder, target_extension='.png', scale_factor=0.4):
    for root, _, files in os.walk(root_folder):
        for filename in files:
            if filename.lower().endswith(target_extension):
                file_path = os.path.join(root, filename)
                try:
                    image = Image.open(file_path)
                    new_width = int(image.width * scale_factor)
                    new_height = int(image.height * scale_factor)
                    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                    resized_image.save(file_path)
                    print(f"Resized {filename} to {new_width}x{new_height}")
                except Exception as e:
                    print(f"Failed to resize {filename}: {e}")

if __name__ == "__main__":
    root_folder = r"C:\Users\vince\Desktop\hdsr klaarzetten\oplevering_stbu_072023\figures_stbu_072023_resized\figures"  # Replace this with the path to your main folder
    resize_images_in_folder(root_folder)