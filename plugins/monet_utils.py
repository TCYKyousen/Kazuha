import ctypes
import os
import sys
from PySide6.QtGui import QImage, QColor

def get_wallpaper_path():
    try:
        if sys.platform != "win32":
            return None
        SPI_GETDESKWALLPAPER = 0x0073
        path = ctypes.create_unicode_buffer(260)
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 260, path, 0)
        p = path.value
        if os.path.exists(p):
            return p
    except Exception:
        pass
    return None

def extract_colors(image_path):
    if not image_path:
        return None
    try:
        img = QImage(image_path)
        if img.isNull():
            return None
        
        # Scale down for performance
        small = img.scaled(100, 100, aspectRatioMode=1) # KeepAspect
        width = small.width()
        height = small.height()
        
        r_sum = 0
        g_sum = 0
        b_sum = 0
        count = 0
        
        # Simple average
        for y in range(height):
            for x in range(width):
                c = small.pixelColor(x, y)
                r_sum += c.red()
                g_sum += c.green()
                b_sum += c.blue()
                count += 1
                
        if count == 0:
            return None
            
        avg_r = r_sum // count
        avg_g = g_sum // count
        avg_b = b_sum // count
        
        primary = QColor(avg_r, avg_g, avg_b)
        
        # Generate palette
        # Helper to clamp
        def clamp(v): return max(0, min(255, v))
        
        def lighten(c, amount):
            h = c.hue()
            s = c.saturation()
            l = c.lightness() + amount
            return QColor.fromHsl(h, s, clamp(l))
            
        def darken(c, amount):
            h = c.hue()
            s = c.saturation()
            l = c.lightness() - amount
            return QColor.fromHsl(h, s, clamp(l))

        # Adjust primary for visibility if too dark/light
        if primary.lightness() < 40:
            primary = lighten(primary, 40 - primary.lightness())
        elif primary.lightness() > 200:
            primary = darken(primary, primary.lightness() - 200)

        # Generate colors
        accent = primary.name()
        bg_surface = lighten(primary, 230 if primary.lightness() < 128 else 200).name() # Very light version
        if QColor(bg_surface).lightness() < 240: # Ensure it's light enough for light mode
             bg_surface = "#F9F9F9"
             
        # Create a simple scheme
        return {
            "primary": accent,
            "background": bg_surface,
            "surface": "#FFFFFF",
            "text": "#000000" # Simplified, UI handles dark mode adaptation usually
        }
    except Exception:
        return None
