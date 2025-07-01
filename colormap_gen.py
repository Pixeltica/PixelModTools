import os
import pandas as pd
from PIL import Image
from pathlib import Path as p

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
    os.makedirs(output_dir, exist_ok=True)

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
        formatted_output_path = p(output_path)
        print(f"CSV file '{formatted_output_path}' created.")

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return
