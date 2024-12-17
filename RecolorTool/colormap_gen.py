from datetime import datetime
import os
import shutil
import pandas as pd
from PIL import Image
from pathlib import Path


def get_hex_color(r, g, b):
    """Converts RGB color values to a hexadecimal color code.

    Args:
        r: Red color value (0-255).
        g: Green color value (0-255).
        b: Blue color value (0-255).

    Returns:
        A string representing the hexadecimal color code.
    """
    return f'#{r:02x}{g:02x}{b:02x}'


def create_color_map(image_path, output_path):
    """Creates a color map from an image and saves it as a CSV file.
        Handles both generated and user-provided CSV files by creating backups.
    """
    output_dir = os.path.dirname(output_path)
    archive_dir = os.path.join(output_dir, 'archive_color_map')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Backup existing color_map.csv if it exists (regardless of origin)
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = Path(os.path.join(archive_dir, f'color_map_{timestamp}.csv'))
        shutil.copy2(output_path, archive_path)
        print(f"Existing color map backed up to {archive_path}")

    try:
        image = Image.open(image_path).convert("RGBA")
        pixels = image.load()
        data = []

        for row in range(0, image.height, 4):
            row_data = {}
            for col in range(image.width // 4):
                color = pixels[col * 4, row]
                hex_color = get_hex_color(color[0], color[1], color[2])
                row_data[col] = hex_color
            data.append(row_data)

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        formatted_output_path = Path(output_path)
        print(f"CSV file '{formatted_output_path}' created.")

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        # If we backed up an existing file, restore it because of the error
        if os.path.exists(archive_path):
            shutil.copy2(archive_path, output_path)
            print(f"Restored previous color map from {archive_path}")
        return  # Important: Exit the function to prevent further errors

    except Exception as e:  # Catch other potential errors during CSV creation
        print(f"An error occurred during CSV creation: {e}")
        # If we backed up an existing file, restore it because of the error
        if os.path.exists(archive_path):
            shutil.copy2(archive_path, output_path)
            print(f"Restored previous color map from {archive_path}")
        return  # Important: Exit the function


# TEST #
# image_path = "/examples/color_map_input.png"
# output_path = "/examples/color_map.csv"
# create_color_map(image_path, output_path)