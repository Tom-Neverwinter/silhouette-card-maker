import math
import os
from PIL import Image, ImageDraw, ImageFont

from utilities import PaperSize

# Specify directory locations
asset_directory = 'assets'

# Generate calibration patterns for each paper size
for paper_size in PaperSize:
    base_filename = f'{paper_size.value}_blank.jpg'
    base_path = os.path.join(asset_directory, base_filename)

    # Load a base page template
    with Image.open(base_path) as im:
        # Load fonts for labels and coordinates
        font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)
        coord_font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 25)
        
        print_width = im.width
        print_height = im.height
        
        # Ensure image is in landscape orientation
        if print_height > print_width:
            im = im.rotate(90, expand=True)
            print_width = im.width
            print_height = im.height
        
        # Create front page with label
        front_image = im.copy()
        front_draw = ImageDraw.Draw(front_image)
        front_draw.text((print_width - 180, print_height - 180), 'front', fill=(0, 0, 0), anchor="ra", font=font)

        # Create back page with label
        back_image = im.copy()
        back_draw = ImageDraw.Draw(back_image)
        back_draw.text((print_width - 180, print_height - 180), 'back', fill=(0, 0, 0), anchor="ra", font=font)

        # Define test pattern specifications
        test_size = 25  # Size of each square marker in pixels
        test_half_size = math.floor(test_size / 2)  # Half size for centering calculations
        test_distance = 75  # Spacing between markers

        # Calculate how many markers fit on the page
        # Subtract 6 to leave margins on all sides
        matrix_size_x = math.floor(print_width / (test_size + test_distance)) - 6
        matrix_half_size_x = math.floor(matrix_size_x / 2)
        
        matrix_size_y = math.floor(print_height / (test_size + test_distance)) - 6
        matrix_half_size_y = math.floor(matrix_size_y / 2)

        # Calculate starting position to center the pattern grid on the page
        # Handles both odd and even matrix sizes differently for proper centering
        start_x = 0
        if matrix_size_x % 2 > 0:  # Odd number of markers
            start_x = math.floor(print_width / 2) - (matrix_half_size_x * test_distance) - ((matrix_half_size_x + .5) * test_size)
        else:  # Even number of markers
            if matrix_size_x <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_x}')
            start_x = math.floor(print_width / 2) - ((matrix_half_size_x - .5) * test_distance) - (matrix_half_size_x * test_size)

        start_y = 0
        if matrix_size_y % 2 > 0:  # Odd number of markers
            start_y = math.floor(print_height / 2) - (matrix_half_size_y * test_distance) - ((matrix_half_size_y + .5) * test_size)
        else:  # Even number of markers
            if matrix_size_y <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_y}')
            start_y = math.floor(print_height / 2) - ((matrix_half_size_y - .5) * test_distance) - (matrix_half_size_y * test_size)

        # Draw the calibration pattern on both front and back pages
        for x_index in range(matrix_size_x):
            for y_index in range(matrix_size_y):
                # Calculate position offset for this marker
                offset_x = x_index * (test_distance + test_size)
                offset_y = y_index * (test_distance + test_size)

                # Draw marker on front page
                front_element_x = start_x + offset_x
                front_element_y = start_y + offset_y
                front_shape = [(front_element_x, front_element_y), (front_element_x + test_size, front_element_y + test_size)]
                
                # Highlight center cross-hairs in blue, all other markers in black
                fill = "black"
                if x_index == matrix_half_size_x or y_index == matrix_half_size_y:
                    fill = "blue"

                front_draw.rectangle(front_shape, fill=fill)

                # Draw marker on back page with intentional offset
                # This offset helps identify printer X/Y alignment issues
                # The offset increases proportionally with distance from center
                back_element_x = front_element_x + x_index - matrix_half_size_x
                back_element_y = front_element_y + y_index - matrix_half_size_y
                back_shape = [(back_element_x, back_element_y), (back_element_x + test_size, back_element_y + test_size)]

                back_draw.rectangle(back_shape, fill=fill)
                
                # Label each back marker with its coordinate offset from center (0,0)
                # +30 pixels below center to avoid overlapping the square
                back_draw.text((back_element_x + test_half_size, back_element_y + test_half_size + 30), 
                              f'({x_index - matrix_half_size_x}, {y_index - matrix_half_size_y})', 
                              fill="red", anchor="mm", font=coord_font)

        # Create PDF with front page and back page rotated 180 degrees
        # The 180 degree rotation simulates flipping the paper over along its long edge
        # This allows alignment checking when printing duplex
        card_list = [front_image, back_image.rotate(180)]
        pdf_path = os.path.join("calibration", f"{paper_size.value}_calibration.pdf")
        card_list[0].save(pdf_path, save_all=True, append_images=card_list[1:], resolution=300, subsampling=0, quality=100)
