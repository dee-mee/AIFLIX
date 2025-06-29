from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    # Create output directory if it doesn't exist
    output_dir = '/home/deemee/Documents/AIFLIX/static/images'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a new image with a gray background
    img = Image.new('RGB', (200, 200), color=(73, 80, 87))  # Dark gray
    d = ImageDraw.Draw(img)
    
    # Try to use a system font
    try:
        font = ImageFont.truetype("Arial.ttf", 80)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 80)
        except:
            font = ImageFont.load_default()
    
    # Draw a user icon
    d.ellipse((30, 30, 170, 170), outline='white', width=3)
    d.ellipse((60, 50, 140, 100), fill='white')
    d.ellipse((80, 100, 120, 160), fill='white')
    
    # Save the image
    output_path = os.path.join(output_dir, 'default-avatar.png')
    img.save(output_path)
    print(f'Default avatar created at {output_path}')

if __name__ == '__main__':
    create_default_avatar()
