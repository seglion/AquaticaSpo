import sys
import cv2
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

def get_dominant_colors(image_path, k=5):
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return []

        # Convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Reshape to list of pixels
        pixels = img.reshape(-1, 3)

        # KMeans to find dominant colors
        kmeans = KMeans(n_clusters=k, n_init=10)
        kmeans.fit(pixels)
        
        # Get colors and counts
        colors = kmeans.cluster_centers_
        counts = Counter(kmeans.labels_)
        
        # Sort by most frequent
        dominant_colors = []
        for i, count in counts.most_common(k):
            color = colors[i]
            hex_color = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
            dominant_colors.append((hex_color, count))
            
        return dominant_colors

    except Exception as e:
        print(f"Error extracting colors: {e}")
        return []

if __name__ == "__main__":
    image_path = "c:/Desarrollo/Aquatica/AquaticaSpo/frontend/src/assets/Logo Aq Fondo blanco_PEQ.jpg"
    print(f"Analyzing {image_path}...")
    colors = get_dominant_colors(image_path)
    
    print("\nDominant Colors Found:")
    for hex_code, count in colors:
        print(f"  {hex_code} (Count: {count})")
