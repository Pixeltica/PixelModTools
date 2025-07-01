import os
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

    recolor_dir = os.path.join(recolor_output_path, 'recolors')
    os.makedirs(recolor_dir, exist_ok=True)
    
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

   