from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def apply_watermark(image_path, output_path, text=None, logo_path=None, position="bottom_right", opacity=0.5):
    """
    Menambahkan watermark teks atau logo.
    Position: 'center' atau 'bottom_right'
    """
    base_image = Image.open(image_path).convert("RGBA")
    width, height = base_image.size
    
    # Layer transparan untuk watermark
    watermark_layer = Image.new("RGBA", base_image.size, (0,0,0,0))
    
    if logo_path:
        # --- Logic Logo Watermark ---
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo (maksimal 20% dari lebar gambar asli)
        logo_w, logo_h = logo.size
        scale = (width * 0.2) / logo_w
        new_size = (int(logo_w * scale), int(logo_h * scale))
        logo = logo.resize(new_size, Image.Resampling.LANCZOS)
        
        # Atur Opacity Logo
        # Kita ubah alpha channelnya
        r, g, b, alpha = logo.split()
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        logo.putalpha(alpha)
        
        w_final, h_final = logo.size
        
        if position == "center":
            x = (width - w_final) // 2
            y = (height - h_final) // 2
        else: # bottom_right
            x = width - w_final - 20
            y = height - h_final - 20
            
        watermark_layer.paste(logo, (x, y), logo)
        
    elif text:
        # --- Logic Text Watermark ---
        draw = ImageDraw.Draw(watermark_layer)
        
        # Load Font (Gunakan default jika ttf tidak ada, tapi diperbesar)
        try:
            # Coba load font standar (sesuaikan path jika di Linux/Mac)
            font_size = int(height * 0.05) # Ukuran font 5% dari tinggi gambar
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        # Hitung ukuran teks (metode baru Pillow)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        if position == "center":
            x = (width - text_w) // 2
            y = (height - text_h) // 2
        else: # bottom_right
            x = width - text_w - 20
            y = height - text_h - 20
            
        # Warna putih dengan alpha sesuai opacity (0-255)
        alpha_val = int(255 * opacity)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha_val))
    
    # Gabungkan layer
    result = Image.alpha_composite(base_image, watermark_layer)
    
    # Convert balik ke RGB untuk disimpan (kecuali user mau PNG transparan, tapi standar JPG ok)
    # Agar aman kita simpan sebagai PNG untuk menjaga kualitas
    result.save(output_path, "PNG")
    return output_path