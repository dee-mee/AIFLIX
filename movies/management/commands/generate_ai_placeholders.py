import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate placeholder images for AI content categories'
    
    def handle(self, *args, **options):
        # Create the static/img directory if it doesn't exist
        img_dir = os.path.join(settings.STATICFILES_DIRS[0], 'img')
        os.makedirs(img_dir, exist_ok=True)
        
        # Define the images to generate
        images = [
            {
                'filename': 'ai-generated.jpg',
                'title': 'AI-Generated Movies',
                'subtitle': 'Created by artificial intelligence',
                'bg_color': (41, 121, 255),  # Blue
            },
            {
                'filename': 'ai-upscaled.jpg',
                'title': 'AI-Upscaled',
                'subtitle': 'Classics enhanced with AI',
                'bg_color': (156, 39, 176),  # Purple
            },
            {
                'filename': 'user-created.jpg',
                'title': 'User Creations',
                'subtitle': 'By our community',
                'bg_color': (0, 150, 136),  # Teal
            },
            {
                'filename': 'ai-series.jpg',
                'title': 'AI-Generated Series',
                'subtitle': 'Binge-worthy AI content',
                'bg_color': (230, 81, 0),  # Deep Orange
            },
            {
                'filename': 'ai-hero-bg.jpg',
                'title': 'AI Content',
                'subtitle': 'The future of entertainment',
                'bg_color': (13, 17, 23),  # Dark blue/black
            },
        ]
        
        # Generate each image
        for img_info in images:
            self.generate_image(img_info, img_dir)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated AI category images'))
    
    def generate_image(self, img_info, output_dir):
        # Create a new image with the specified background color
        width, height = 1280, 720
        image = Image.new('RGB', (width, height), color=img_info['bg_color'])
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to load a font
            font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Roboto-Bold.ttf')
            title_font = ImageFont.truetype(font_path, 72)
            subtitle_font = ImageFont.truetype(font_path, 36)
        except IOError:
            # Fall back to default font if the specified font is not available
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add title text
        title = img_info['title']
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        # Add subtitle text
        subtitle = img_info.get('subtitle', '')
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        
        # Calculate text positions (centered)
        title_x = (width - title_width) // 2
        title_y = (height - title_height) // 2 - 30
        
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + title_height + 20
        
        # Add text to image
        draw.text((title_x, title_y), title, fill='white', font=title_font, align='center')
        
        if subtitle:
            # Use a light gray color with transparency
            draw.text((subtitle_x, subtitle_y), subtitle, fill=(230, 230, 230), 
                     font=subtitle_font, align='center')
        
        # Add some decorative elements
        for i in range(5):
            x1 = (i * 200) % (width - 100)
            y1 = (i * 150) % (height - 100)
            x2 = x1 + 300
            y2 = y1 + 200
            # Use a very light gray for the ellipse outline
            draw.ellipse([x1, y1, x2, y2], outline=(240, 240, 240), width=5)
        
        # Save the image
        output_path = os.path.join(output_dir, img_info['filename'])
        image.save(output_path, 'JPEG', quality=85)
        
        self.stdout.write(f'Generated {output_path}')
