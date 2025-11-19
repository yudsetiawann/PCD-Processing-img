from PIL import Image
import numpy as np

def text_to_bin(message):
    """Mengubah string pesan menjadi binary."""
    return ''.join(format(ord(char), '08b') for char in message)

def bin_to_text(binary_data):
    """Mengubah binary menjadi string."""
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data.endswith("#####"): # Delimiter penanda akhir pesan
            return decoded_data[:-5]
    return decoded_data

def encode_lsb(image_path, message, output_path):
    """Menyisipkan pesan ke dalam gambar menggunakan LSB."""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    # Tambahkan delimiter agar kita tahu kapan pesan berakhir
    message += "#####"
    binary_msg = text_to_bin(message)
    data_len = len(binary_msg)
    
    pixels = np.array(img)
    total_pixels = width * height * 3
    
    if data_len > total_pixels:
        raise ValueError("Pesan terlalu panjang untuk ukuran gambar ini.")
    
    index = 0
    for row in range(height):
        for col in range(width):
            for channel in range(3): # R, G, B
                if index < data_len:
                    # Ubah bit terakhir (LSB)
                    current_val = pixels[row, col, channel]
                    binary_val = format(current_val, '08b')
                    
                    # Ganti bit terakhir dengan bit pesan
                    new_binary = binary_val[:-1] + binary_msg[index]
                    pixels[row, col, channel] = int(new_binary, 2)
                    index += 1
                else:
                    break
            if index >= data_len: break
        if index >= data_len: break
        
    encoded_img = Image.fromarray(pixels)
    encoded_img.save(output_path)
    return output_path

def decode_lsb(image_path):
    """Mengekstrak pesan dari gambar LSB."""
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)
    
    binary_data = ""
    for row in pixels:
        for pixel in row:
            for channel in pixel:
                binary_data += format(channel, '08b')[-1]
                
    # Coba decode setiap 8 bit (optimasi sederhana agar tidak loop semua pixel jika pesan pendek)
    # Namun untuk akurasi penuh, fungsi bin_to_text akan mencari delimiter
    return bin_to_text(binary_data)