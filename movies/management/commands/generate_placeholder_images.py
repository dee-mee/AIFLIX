import os
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate placeholder images for AI content categories'

    def handle(self, *args, **options):
        # Create the images directory if it doesn't exist
        os.makedirs(os.path.join(settings.STATIC_ROOT, 'img'), exist_ok=True)
        
        # Define the categories and their display names
        categories = [
            ('ai_generated', 'AI-Generated Movies'),
            ('ai_upscaled', 'AI-Upscaled Classics'),
            ('user_created', 'User Creations'),
            ('ai_series', 'AI-Generated Series'),
            ('trending', 'Trending AI Content'),
        ]
        
        # Generate an image for each category
        for category_id, category_name in categories:
            self.generate_image(category_id, category_name)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated placeholder images'))
    
    def generate_image(self, category_id, category_name):
        """Generate a placeholder image with the category name."""
        # Image dimensions
        width, height = 800, 450
        
        # Create a new image with a dark background
        image = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("arial.ttf", 48)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), category_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw the text
        draw.text((x, y), category_name, fill="#e50914", font=font)
        
        # Save the image
        filename = f"{category_id.replace(' ', '-').lower()}-thumb.jpg"
        filepath = os.path.join(settings.STATIC_ROOT, 'img', filename)
        image.save(filepath, 'JPEG', quality=85)
        
        self.stdout.write(f"Generated: {filepath}")
