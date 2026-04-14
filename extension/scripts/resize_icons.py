import os
from PIL import Image

source_logo = r"C:\Users\hp\.gemini\antigravity\brain\dd26809d-2840-4cad-94c4-3013bfc481fb\phishguard_logo_1776178168791.png"
extension_icons_dir = r"d:\Download Me\Ramsethi_Rangesh\phishguard-india\extension\icons"

os.makedirs(extension_icons_dir, exist_ok=True)

try:
    img = Image.open(source_logo).convert("RGBA")
    
    sizes = [16, 48, 128]
    for size in sizes:
        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
        out_path = os.path.join(extension_icons_dir, f"icon{size}.png")
        resized_img.save(out_path, format="PNG")
        print(f"Saved {out_path}")
        
    dashboard_logo = r"d:\Download Me\Ramsethi_Rangesh\dashboard\pg_logo.png"
    dashboard_img = img.resize((256, 256), Image.Resampling.LANCZOS)
    dashboard_img.save(dashboard_logo, format="PNG")
    print(f"Saved {dashboard_logo}")
    
except Exception as e:
    print(f"Error resizing logo: {e}")
