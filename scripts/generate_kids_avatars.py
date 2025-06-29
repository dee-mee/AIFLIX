from PIL import Image, ImageDraw, ImageFont
import os

# Create output directory
output_dir = '/home/deemee/Documents/AIFLIX/static/images/avatars/kids'
os.makedirs(output_dir, exist_ok=True)

# Avatar configurations
avatars = [
    {'name': 'avatar1.png', 'emoji': '🦊', 'bg_color': (255, 152, 0)},    # Orange
    {'name': 'avatar2.png', 'emoji': '🐱', 'bg_color': (156, 39, 176)},  # Purple
    {'name': 'avatar3.png', 'emoji': '🐼', 'bg_color': (0, 150, 136)},   # Teal
    {'name': 'avatar4.png', 'emoji': '🐘', 'bg_color': (244, 67, 54)},    # Red
    {'name': 'avatar5.png', 'emoji': '🦁', 'bg_color': (255, 193, 7)}     # Yellow
]

# Create avatars
for avatar in avatars:
    # Create a new image with a colored background
    img = Image.new('RGB', (200, 200), color=avatar['bg_color'])
    d = ImageDraw.Draw(img)
    
    # Try to use a system font that supports emojis
    try:
        font = ImageFont.truetype("NotoColorEmoji.ttf", 100)
    except:
        try:
            font = ImageFont.truetype("Segoe UI Emoji.ttf", 100)
        except:
            font = ImageFont.load_default()
    
    # Get text size and position
    text = avatar['emoji']
    # Create a temporary drawing context to measure text
    from PIL import ImageFont, ImageDraw, Image
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    # Get text bounding box
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((200 - text_width) // 2, (200 - text_height) // 2)
    
    # Draw the emoji
    d.text(position, text, font=font, embedded_color=True)
    
    # Save the image
    img.save(os.path.join(output_dir, avatar['name']))
    print(f'Created {avatar["name"]}')

print('All avatars created successfully!')
