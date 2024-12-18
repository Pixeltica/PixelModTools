import datetime
import os
import shutil
import pandas as pd
from PIL import Image
from pathlib import Path as p


def load_color_mappings(colormap_path):
    """Loads color mappings from a CSV file.

    Args:
        colormap_path: Path to the CSV file containing color mappings.

    Returns:
        A list of tuples, where each tuple contains a column index (prefix) and
        a dictionary mapping base colors to new colors.
    """
    df = pd.read_csv(colormap_path, header=None)
    color_mappings = []
    base_palette = df[0].tolist()

    for col_index in range(1, len(df.columns)):
        mapping = {base_palette[i]: df[col_index][i] for i in range(len(base_palette))}
        color_mappings.append((col_index, mapping))

    return color_mappings


def swap_colors(colormap_path, recolor_base_file, recolor_output_path):
    """Swaps colors in an image based on color mappings CSV.

    Args:
        colormap_path: Path to the CSV file containing color mappings.
        recolor_base_file: Path to the base image file.
        recolor_output_path: Path to the output directory for recolored images.
    """
    color_mappings = load_color_mappings(colormap_path)

    # Create recolor output directory and archive directory (if they don't exist)
    recolor_dir = os.path.join(recolor_output_path, 'recolors')
    archive_dir = os.path.join(recolor_output_path, 'archive_recolors')
    os.makedirs(recolor_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Clear existing files in recolors directory
    for filename in os.listdir(recolor_dir):
        file_path = os.path.join(recolor_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) # Just in case weird folders are still there
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    generated_images = []
    for prefix, color_map in color_mappings:
        image = Image.open(recolor_base_file).convert("RGBA")
        pixels = image.load()

        for i in range(image.width):
            for j in range(image.height):
                r, g, b, a = pixels[i, j]
                hex_color = f'#{r:02x}{g:02x}{b:02x}'

                if hex_color in color_map:
                    new_color = color_map[hex_color]
                    new_r = int(new_color[1:3], 16)
                    new_g = int(new_color[3:5], 16)
                    new_b = int(new_color[5:7], 16)
                    pixels[i, j] = (new_r, new_g, new_b, a)

        original_filename = os.path.basename(recolor_base_file)
        new_image_path = p(os.path.join(recolor_dir, f"{prefix}_{original_filename}"))
        image.save(new_image_path)
        print(f"Modified image saved as {new_image_path}")
        generated_images.append(new_image_path)

    create_allinone(recolor_base_file, generated_images, recolor_dir, archive_dir)  # Modified call


def create_allinone(base_image_path, image_paths, output_directory, archive_dir):
    """Creates an all-in-one combined image and saves it in two locations.

    Args:
        base_image_path: Path to the base image file.
        image_paths: A list of paths to the recolored image files.
        output_directory: Path to the output directory for the combined image.
        archive_dir: path to the archive directory
    """
    image_paths.insert(0, base_image_path)
    images = [Image.open(path) for path in image_paths]
    img_width, img_height = images[0].size

    num_images = len(images)
    num_columns = 2
    num_rows = (num_images + 1) // num_columns

    allinone_width = img_width * num_columns
    allinone_height = img_height * num_rows

    allinone_image = Image.new('RGBA', (allinone_width, allinone_height))

    for index, img in enumerate(images):
        x = (index % num_columns) * img_width
        y = (index // num_columns) * img_height
        allinone_image.paste(img, (x, y))

    allinone_image_path = p(os.path.join(output_directory, 'all_in_one.png'))
    allinone_image.save(allinone_image_path)
    print(f"Combined recolor saved as {allinone_image_path}")

    # Save a timestamped copy to the archive
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = p(os.path.join(archive_dir, f'all_in_one_{timestamp}.png'))
    allinone_image.save(archive_path)
    print(f"Archived combined recolor saved as {archive_path}")

# TEST #
# recolor_base_file = "/examples/base_image.png"
# colormap_path = "/examples/color_map.csv"
# recolor_output_path = "/examples/"
# swap_colors(colormap_path, recolor_base_file, recolor_output_path)

