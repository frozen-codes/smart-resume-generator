"""
QR Code Generator Module for Resume Generator
Handles QR code generation for resume links and LinkedIn profiles
"""

import os
import random
import string
import datetime

# Try to import optional dependencies
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

def generate_qr_code(data, filename=None, size=10, border=4, logo_path=None):
    """
    Generate a QR code for the given data
    
    Args:
        data: URL or text to encode in the QR code
        filename: Optional filename for the QR code image
        size: Size of each QR code box in pixels
        border: Border size in boxes
        logo_path: Optional path to a logo to place in the center
        
    Returns:
        str: Path to the generated QR code image or error message
    """
    if not QR_AVAILABLE:
        return "Error: QR code generation requires qrcode and Pillow. Install with 'pip install qrcode[pil]'."
    
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        filename = f"qr_code_{timestamp}_{random_str}.png"
    
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=border,
        )
        
        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image from QR code
        img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
        
        # If logo path is provided, add logo to center of QR code
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert('RGBA')
                
                # Calculate position to place logo (center)
                box_width = qr.modules_count * size
                logo_size = int(box_width * 0.25)  # Logo size = 25% of QR code
                
                # Resize logo
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                
                # Calculate position
                pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
                
                # Create white box behind logo for better visibility
                white_box = Image.new('RGBA', (logo_size + 10, logo_size + 10), (255, 255, 255, 255))
                img.paste(white_box, (pos[0] - 5, pos[1] - 5), white_box)
                
                # Place logo on QR code
                img.paste(logo, pos, logo)
            except Exception as e:
                print(f"Error adding logo to QR code: {str(e)}")
        
        # Save image
        img.save(filename)
        return os.path.abspath(filename)
    
    except Exception as e:
        return f"Error generating QR code: {str(e)}"

def generate_qr_with_linkedin_template(linkedin_url, name=None, filename=None):
    """
    Generate a QR code with LinkedIn styling
    
    Args:
        linkedin_url: LinkedIn profile URL
        name: Optional name to display below QR code
        filename: Optional filename for the output image
        
    Returns:
        str: Path to the generated QR code image or error message
    """
    if not QR_AVAILABLE:
        return "Error: QR code generation requires qrcode and Pillow. Install with 'pip install qrcode[pil]'."
    
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_qr_{timestamp}.png"
    
    try:
        # Create the QR code
        qr_code_path = generate_qr_code(
            data=linkedin_url,
            size=10,
            border=4
        )
        
        if qr_code_path.startswith("Error"):
            return qr_code_path
        
        # Open the QR code image
        qr_img = Image.open(qr_code_path).convert('RGBA')
        
        # Create a new image with space for the LinkedIn logo and name
        width, height = qr_img.size
        new_height = height + 100  # Extra space for text and logo
        new_img = Image.new('RGBA', (width, new_height), (255, 255, 255, 255))
        
        # Paste the QR code onto the new image
        new_img.paste(qr_img, (0, 0))
        
        # Add the name if provided
        if name:
            try:
                draw = ImageDraw.Draw(new_img)
                
                # Try to use a nice font, fall back to default if not available
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position (centered)
                text_width = draw.textlength(f"Connect with {name} on LinkedIn", font=font)
                text_x = (width - text_width) // 2
                
                # Draw the text
                draw.text(
                    (text_x, height + 30),
                    f"Connect with {name} on LinkedIn",
                    fill=(0, 119, 181),  # LinkedIn blue
                    font=font
                )
            except Exception as e:
                print(f"Error adding text to QR code: {str(e)}")
        
        # Save the new image
        new_img.save(filename)
        
        # Delete the temporary QR code image
        try:
            os.remove(qr_code_path)
        except:
            pass
        
        return os.path.abspath(filename)
    
    except Exception as e:
        return f"Error generating LinkedIn QR code: {str(e)}" 