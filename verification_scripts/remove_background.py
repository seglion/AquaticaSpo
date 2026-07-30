from PIL import Image
import numpy as np

def remove_white_background(input_path, output_path, tolerance=30):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            # Check if pixel is white-ish (R, G, B > 255 - tolerance)
            # The dominant color was #fcfdfd (252, 253, 253)
            if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
                new_data.append((255, 255, 255, 0)) # Transparent
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        img.save(output_path, "PNG")
        print(f"Successfully saved transparent logo to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_logo = "c:/Desarrollo/Aquatica/AquaticaSpo/frontend/src/assets/Logo Aq Fondo blanco_PEQ.jpg"
    output_logo = "c:/Desarrollo/Aquatica/AquaticaSpo/frontend/src/assets/Logo_Aq_Transparent.png"
    
    print(f"Processing {input_logo}...")
    remove_white_background(input_logo, output_logo)
