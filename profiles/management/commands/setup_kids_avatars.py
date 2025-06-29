import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Set up default kids avatars in the media directory'

    def handle(self, *args, **options):
        # Define source and destination directories
        static_avatars_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'avatars', 'kids')
        media_avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars', 'kids')
        
        # Create directories if they don't exist
        os.makedirs(static_avatars_dir, exist_ok=True)
        os.makedirs(media_avatars_dir, exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'avatars'), exist_ok=True)  # Ensure avatars directory exists
        
        # List of default avatars
        avatars = [
            'avatar1.png', 'avatar2.png', 'avatar3.png', 
            'avatar4.png', 'avatar5.png'
        ]
        
        # Generate avatars if they don't exist in static
        if not all(os.path.exists(os.path.join(static_avatars_dir, avatar)) for avatar in avatars):
            self.stdout.write('Generating default kids avatars...')
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            for i, emoji in enumerate(['🦊', '🐱', '🐼', '🐘', '🦁'], 1):
                # Create a new image with a colored background
                bg_colors = [
                    (255, 152, 0),   # Orange
                    (156, 39, 176),   # Purple
                    (0, 150, 136),    # Teal
                    (244, 67, 54),     # Red
                    (255, 193, 7)      # Yellow
                ]
                
                img = Image.new('RGB', (200, 200), color=bg_colors[i-1])
                d = ImageDraw.Draw(img)
                
                # Try to use a system font that supports emojis
                try:
                    font = ImageFont.truetype("NotoColorEmoji.ttf", 100)
                except:
                    try:
                        font = ImageFont.truetype("Segoe UI Emoji.ttf", 100)
                    except:
                        font = ImageFont.load_default()
                
                # Draw the emoji
                # Create a temporary drawing context to measure text
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                # Get text bounding box
                bbox = temp_draw.textbbox((0, 0), emoji, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((200 - text_width) // 2, (200 - text_height) // 2)
                
                d.text(position, emoji, font=font, embedded_color=True)
                
                # Save the image
                output_path = os.path.join(static_avatars_dir, f'avatar{i}.png')
                img.save(output_path)
                self.stdout.write(self.style.SUCCESS(f'Generated {output_path}'))
        
        # Copy default avatars from static to media directory if they don't exist
        for avatar in avatars:
            src = os.path.join(static_avatars_dir, avatar)
            dst = os.path.join(media_avatars_dir, avatar)
            
            # If the avatar doesn't exist in media, copy from static
            if not os.path.exists(dst):
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    self.stdout.write(self.style.SUCCESS(f'Copied {avatar} to media directory'))
                else:
                    self.stdout.write(self.style.WARNING(f'Source file not found: {src}'))
        
        # Copy default avatar if it doesn't exist
        default_avatar_src = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-avatar.png')
        default_avatar_dst = os.path.join(settings.MEDIA_ROOT, 'avatars', 'default-avatar.png')
        if not os.path.exists(default_avatar_dst):
            if os.path.exists(default_avatar_src):
                os.makedirs(os.path.dirname(default_avatar_dst), exist_ok=True)
                shutil.copy2(default_avatar_src, default_avatar_dst)
                self.stdout.write(self.style.SUCCESS('Copied default avatar to media directory'))
        
        self.stdout.write(self.style.SUCCESS('Kids avatars setup complete!'))
