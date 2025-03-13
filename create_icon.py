"""
Script to create a simple Pokemon icon for our application.
This will generate a pokemon_icon.ico file that can be used as the application icon.
"""

import os
import sys
import base64
from io import BytesIO
from PIL import Image, ImageDraw

def create_pokeball_icon(size=256, output_file="pokemon_icon.ico"):
    """Create a simple Pokeball icon and save it as an ICO file."""
    # Create a new image with a white background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw the outer circle (red top, white bottom)
    draw.ellipse((0, 0, size-1, size-1), outline=(0, 0, 0, 255), width=int(size/20))
    draw.pieslice((0, 0, size-1, size-1), 0, 180, fill=(255, 0, 0, 255))
    draw.pieslice((0, 0, size-1, size-1), 180, 360, fill=(255, 255, 255, 255))
    
    # Draw the middle line
    line_width = int(size/20)
    draw.rectangle((0, size/2 - line_width/2, size, size/2 + line_width/2), fill=(0, 0, 0, 255))
    
    # Draw the center circle
    center_size = size/5
    draw.ellipse((size/2 - center_size, size/2 - center_size, 
                 size/2 + center_size, size/2 + center_size), 
                 fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=int(size/40))
    
    # Draw the inner circle
    inner_size = center_size * 0.6
    draw.ellipse((size/2 - inner_size, size/2 - inner_size, 
                 size/2 + inner_size, size/2 + inner_size), 
                 fill=(0, 0, 0, 255))
    
    # Save as ICO file
    img.save(output_file, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print(f"Icon created successfully: {output_file}")
    return output_file

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        create_pokeball_icon()
    except ImportError:
        print("Error: Pillow library is required to create the icon.")
        print("Please install it with: pip install pillow")
        sys.exit(1) 