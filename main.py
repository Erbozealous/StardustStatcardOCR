# Import libraries
import pytesseract
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from tkinter import messagebox
import subprocess
import tempfile
import os
import platform



# Import compartments
import pointdefense
import laser
import missile
import sustainedbeam


class WeaponStatsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weapon Stats OCR")
        self.root.geometry("800x600")
        
        # Weapon type selection frame
        self.weapon_frame = ttk.LabelFrame(root, text="Weapon Type")
        self.weapon_frame.pack(padx=10, pady=5, fill="x")
        
        # Weapon type buttons
        self.weapon_type = tk.StringVar(value="pointdefense")
        ttk.Radiobutton(self.weapon_frame, text="Point Defense", value="pointdefense", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(self.weapon_frame, text="Laser", value="laser", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(self.weapon_frame, text="Missile", value="missile", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(self.weapon_frame, text="Sustained Beam", value="beam", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        
        # Input frame
        self.input_frame = ttk.LabelFrame(root, text="Input")
        self.input_frame.pack(padx=10, pady=5, fill="x")
        
        # Input buttons
        ttk.Button(self.input_frame, text="Select Image File", 
                   command=self.load_image_file).pack(side="left", padx=5)
        ttk.Button(self.input_frame, text="Paste from Clipboard", 
                   command=self.paste_from_clipboard).pack(side="left", padx=5)
        
        # Output frame
        self.output_frame = ttk.LabelFrame(root, text="Output")
        self.output_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Output text box
        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, 
                                                    width=50, height=20)
        self.output_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken")
        self.status_bar.pack(fill="x", padx=5, pady=5)
        
    def load_image_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            try:
                image = Image.open(file_path)
                result = process_image_to_template(image, self.weapon_type.get())
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set("Image processed successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
                self.status_var.set("Error processing image")
    
    def paste_from_clipboard(self):
        temp_path = None
        try:
            if platform.system() == "Darwin":
                # macOS path using ImageGrab
                image = ImageGrab.grabclipboard()
                if image is None:
                    raise ValueError("No image found in clipboard on macOS")
                
                result = process_image_to_template(image, self.weapon_type.get())
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set("Clipboard image processed successfully (macOS)")

            else:
                # Wayland path (Linux)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_path = temp_file.name
                
                print(f"Created temporary file: {temp_path}")
                
                try:
                    result = subprocess.run(['wl-paste', '-t', 'image/png'], 
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            check=True)
                    
                    with open(temp_path, 'wb') as f:
                        f.write(result.stdout)
                    
                    print(f"wl-paste output size: {len(result.stdout)} bytes")
                    if result.stderr:
                        print(f"wl-paste stderr: {result.stderr.decode()}")
                        
                except subprocess.CalledProcessError as e:
                    print(f"wl-paste error: {e}")
                    print(f"stderr: {e.stderr.decode() if e.stderr else 'No error output'}")
                    raise ValueError(f"No image found in clipboard: {e}")
                
                if os.path.getsize(temp_path) == 0:
                    raise ValueError("No image data in clipboard")
                
                image = Image.open(temp_path)
                result = process_image_to_template(image, self.weapon_type.get())
                
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set("Clipboard image processed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"No valid image in clipboard: {str(e)}")
            self.status_var.set("Error processing clipboard")

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass


def process_image_to_template(image, weapon_type='pointdefense'):
    # Read the image using PIL
    
    # Convert image to grayscale if needed
    image.convert("L")

    
    # Extract text from image using pytesseract
    text = pytesseract.image_to_string(image, config="--psm 6")
    print("Processing " + weapon_type)
    print("Extracted text from image:")
    print("---START OF TEXT---")
    print(text)
    print("---END OF TEXT---")
    
    if weapon_type == "pointdefense":
        output = pointdefense.processPointDefense(text)
    elif weapon_type == "laser":
        output = laser.processLaser(text)
    elif weapon_type == "missile":
        output = missile.processMissile(text)
    elif weapon_type == "beam":
        output = sustainedbeam.processSustainedBeam(text)
    else:
        raise ValueError(f"Unknown weapon type: {weapon_type}")
    
    
    
    return output

def get_template_for_type(weapon_type):
    templates = {
        'pointdefense': {
            'spacedamage': '',
            'range': '',
            'MV': '',
            'reload': '',
            'modrange': '',
            'missileaccuracy': '',
            'spacecraftaccuracy': '',
            'accuracyvalues': '',
            'missilehitchance': '',
            'spacecrafthitchance': '',
            'accuracy': '',
            'flakdamage': '',
            'flakrange': '',
            'flakshotrange': '',
            'prioritizedtype': '',
            'prioritizedprox': '',
        },
        'laser': {
            'burst': '',
            'burstsshots': '',
            'burstsdelay': '',
            'modrange': '',
            'startdamage': '',
            'enddamage': '',
            'damage': '',
            'shielddamage': '',
            'shieldbypass': '',
            'objectives': '',
            'charge': '',
            'reload': '',
            'range': '',
            'MV': '',
            'dispersion': '',
            'dispersionmax': '',
            'autoaim': '',
        },
        'beam': {
            'burst': '',
            'burstsshots': '',
            'burstsdelay': '',
            'maxrange': '',
            'total': '',
            'damage': '',
            'startdamage': '',
            'enddamage': '',
            'shielddamage': '',
            'shieldbypass': '',
            'hmaxrange': '',
            'htotal': '',
            'healing': '',
            'starthealing': '',
            'endhealing': '',
            'shieldhealing': '',
            'hshieldbypass': '',
            'objectives': '',
            'charge': '',
            'reload': '',
            'range': '',
            'MV': '',
            'dispersion': '',
            'dispersionmax': '',
            'autoaim': '',
        },
        'missile': {
            'burst': '',
            'burstsshots': '',
            'burstsdelay': '',
            'damage': '',
            'shielddamage': '',
            'shieldbypass': '',
            'ASW': '',
            'HP': '',
            'disruption': '',
            'objectives': '',
            'charge': '',
            'reload': '',
            'range': '',
            'MV': '',
            'autoaim': '',
        }
    }
    return templates.get(weapon_type, templates['pointdefense']).copy()

def main():
    root = tk.Tk()
    app = WeaponStatsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
