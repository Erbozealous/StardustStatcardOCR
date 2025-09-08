# Import libraries
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, PhotoImage, messagebox
from PIL import Image, ImageGrab, ImageFilter
import subprocess
import tempfile
import os
import platform
import requests
from bs4 import BeautifulSoup
import re
import json



import ocr
import pointdefense
import laser
import missile
import sustainedbeam
import fighter
import fighterweapon

class WeaponStatsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weapon Stats OCR")
        self.root.geometry("800x650")
        
        # Read from settings.json if it exists
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        else: 
            # Initialize settings
            self.settings = {
                'psm_mode': 6,
                'auto_scale': True,
                'min_size': 600,
                'scale_factor': 2.0,
                'grayscale': False,
                'save_images': False,
                'existing_weapon': True,
                'theme': 'dark',
                'use_adaptive_threshold': False,
                'threshold': 127,
                'threhold_max': 255
            }
        
        # Weapon type selection frame
        self.weapon_frame = ttk.LabelFrame(root, text="Type")
        self.weapon_frame.pack(padx=10, pady=(5, 10), fill="x")
        
        # Create a frame for radio buttons with padding
        radio_frame = ttk.Frame(self.weapon_frame)
        radio_frame.pack(padx=5, pady=(5, 8), fill="x")
        
        # Weapon type buttons
        self.weapon_type = tk.StringVar(value="pointdefense")
        ttk.Radiobutton(radio_frame, text="Point Defense", value="pointdefense", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Laser", value="laser", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Missile", value="missile", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Sustained Beam", value="beam", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Fighter", value="fighter", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        ttk.Radiobutton(radio_frame, text="Fighter Weapon", value="fighterweapon", 
                        variable=self.weapon_type).pack(side="left", padx=5)
        
        # Input frame
        self.input_frame = ttk.LabelFrame(root, text="Input")
        self.input_frame.pack(padx=10, pady=(10, 10), fill="x")
        
        # Create a frame for buttons with padding
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(padx=5, pady=(5, 8), fill="x")
        
        # Input buttons
        ttk.Button(button_frame, text="Select Image File", 
                   command=self.load_image_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Paste from Clipboard", 
                   command=self.paste_from_clipboard).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Settings", 
                   command=self.open_settings).pack(side="right", padx=5)
        
        # Output frame
        self.output_frame = ttk.LabelFrame(root, text="Output")
        self.output_frame.pack(padx=10, pady=(10, 10), fill="both", expand=True)
        
        # Output text box
        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, 
                                                    width=50, height=20)
        self.output_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken")
        self.status_bar.pack(fill="x", padx=5, pady=(5, 8))
        self.status_var.set("The OCR can make mistakes. Make sure to double-check!")
        
    def load_image_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            try:
                image = Image.open(file_path)
                result = process_image_to_template(image, self.weapon_type.get(), self.settings)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set(self.weapon_type.get() +  " processed successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
                self.status_var.set("Error processing image")
    
    def open_settings(self):
        settings_window = SettingsWindow(self.root, self.settings)
        self.root.wait_window(settings_window.window)
        
        # After settings window is closed, check if settings were saved
        if hasattr(settings_window, 'settings_saved') and settings_window.settings_saved:
            self.settings = settings_window.final_settings
            print("Settings saved:", self.settings)
    
    def paste_from_clipboard(self):
        temp_path = None
        try:
            if platform.system() == "Darwin" or platform.system() == "Windows":
                # macOS path using ImageGrab
                image = ImageGrab.grabclipboard()
                if image is None:
                    raise ValueError("No image found in clipboard (" + platform.system() + ")")
                
                result = process_image_to_template(image, self.weapon_type.get(), self.settings)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set(self.weapon_type.get() +  " processed successfully")

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
                
                # Open and process the image
                image = Image.open(temp_path)
                result = process_image_to_template(image, self.weapon_type.get(), self.settings)
                
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result)
                self.status_var.set(self.weapon_type.get() + " image processed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("Error processing clipboard (" + platform.system() + ")")

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

class SettingsWindow:
    def __init__(self, parent, current_settings):
        self.window = tk.Toplevel(parent)
        self.window.title("OCR Settings")
        self.window.geometry("400x650")
        self.window.transient(parent)  # Make window modal
        self.window.grab_set()
        
        # Initialize settings flags
        self.settings_saved = False
        self.final_settings = None
        self.current_settings = current_settings
        
        # Create settings frames
        self.create_ocr_settings()
        self.create_image_settings()
        self.create_other_settings()
        self.create_buttons()
        
        # Load current settings into UI
        self.load_current_settings()
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_current_settings(self):
        # Set PSM mode
        current_psm = self.current_settings.get('psm_mode', 6)
        for value in self.psm_values:
            if value.startswith(str(current_psm)):
                self.psm_var.set(value)
                break
        
        # Set scale settings
        self.scale_var.set(self.current_settings.get('auto_scale', True))
        self.min_size.set(str(self.current_settings.get('min_size', 600)))
        self.scale_factor.set(str(self.current_settings.get('scale_factor', 2.0)))
        
        # Set grayscale
        self.grayscale_var.set(self.current_settings.get('grayscale', False))
        
        # Set adaptive threshold options
        self.adaptive_threshold_var.set(self.current_settings.get('use_adaptive_threshold', False))
        self.block_size_var.set(str(self.current_settings.get('threshold', 127)))
        self.c_value_var.set(str(self.current_settings.get('threshold_max', 255)))
        
        # Set save images
        self.save_images_var.set(self.current_settings.get('save_images', False))
        
        # Check for existing weapon
        self.existing_weapon_var.set(self.current_settings.get('existing_weapon', True))
        
        # Set theme
        self.theme_var.set(self.current_settings.get('theme', 'dark'))
    
    def create_ocr_settings(self):
        ocr_frame = ttk.LabelFrame(self.window, text="OCR Settings")
        ocr_frame.pack(padx=10, pady=(5, 10), fill="x")
        
        settings_frame = ttk.Frame(ocr_frame)
        settings_frame.pack(padx=5, pady=(5, 8), fill="x")
        
        # PSM Mode selection
        ttk.Label(settings_frame, text="Page Segmentation Mode:").pack(anchor="w", padx=5, pady=(2, 4))
        self.psm_values = [
            "0 - Orientation and script detection only",
            "1 - Automatic page segmentation with OSD",
            "3 - Fully automatic page segmentation, but no OSD",
            "4 - Assume a single column of text of variable sizes",
            "6 - Assume a uniform block of text",
            "7 - Treat the image as a single text line",
            "8 - Treat the image as a single word",
            "13 - Raw line. Treat the image as a single text line"
        ]
        self.psm_var = tk.StringVar()
        psm_combo = ttk.Combobox(ocr_frame, textvariable=self.psm_var, 
                                values=self.psm_values, state="readonly")
        psm_combo.pack(fill="x", padx=5, pady=(5, 8))
    
    def create_image_settings(self):
        image_frame = ttk.LabelFrame(self.window, text="Image Processing")
        image_frame.pack(padx=10, pady=(5, 10), fill="x")
        
        image_options_frame = ttk.Frame(image_frame)
        image_options_frame.pack(padx=5, pady=(5, 8), fill="x")
        
        # Auto-scale small images
        self.scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(image_options_frame, text="Auto-scale small images for better accuracy", 
                       variable=self.scale_var).pack(anchor="w", padx=5, pady=2)
        
        # Minimum image size before scaling
        min_size_frame = ttk.Frame(image_options_frame)
        min_size_frame.pack(fill="x", padx=5, pady=4)
        ttk.Label(min_size_frame, text="Minimum image size (pixels):").pack(side="left")
        self.min_size = tk.StringVar(value="600")
        ttk.Entry(min_size_frame, textvariable=self.min_size, width=5).pack(side="left", padx=5)
        
        # Scale factor for small images
        scale_frame = ttk.Frame(image_options_frame)
        scale_frame.pack(fill="x", padx=5, pady=4)
        ttk.Label(scale_frame, text="Scale factor:").pack(side="left")
        self.scale_factor = tk.StringVar(value="2.0")
        ttk.Entry(scale_frame, textvariable=self.scale_factor, width=5).pack(side="left", padx=5)
        
        # Grayscale conversion
        self.grayscale_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(image_options_frame, text="Convert to grayscale before processing", 
                       variable=self.grayscale_var).pack(anchor="w", padx=5, pady=2)
        
        # Adaptive thresholding
        self.adaptive_threshold_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(image_options_frame, text="Use adaptive thresholding", 
                       variable=self.adaptive_threshold_var).pack(anchor="w", padx=5, pady=2)
        
        # Adaptive threshold parameters
        threshold_frame = ttk.Frame(image_options_frame)
        threshold_frame.pack(fill="x", padx=5, pady=4)
        
        # Block size
        ttk.Label(threshold_frame, text="Threshold:").pack(side="left")
        self.block_size_var = tk.StringVar(value="127")
        ttk.Entry(threshold_frame, textvariable=self.block_size_var, width=5).pack(side="left", padx=5)
        
        # C value
        ttk.Label(threshold_frame, text="Threshold Max").pack(side="left", padx=(10,0))
        self.c_value_var = tk.StringVar(value="255")
        ttk.Entry(threshold_frame, textvariable=self.c_value_var, width=5).pack(side="left", padx=5)
        
        # Save processed images
        self.save_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(image_options_frame, text="Save processed images to a separate folder", 
                       variable=self.save_images_var).pack(anchor="w", padx=5, pady=2)
        
        
    def create_other_settings(self):
        other_frame = ttk.LabelFrame(self.window, text="Other")
        other_frame.pack(padx=10, pady=(5, 10), fill="x")
        
        other_options_frame = ttk.Frame(other_frame)
        other_options_frame.pack(padx=5, pady=(5, 8), fill="x")
        
        # Existing weapon handling
        self.existing_weapon_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_options_frame, text="Check if weapon already exists in the database",
                          variable=self.existing_weapon_var).pack(anchor="w", padx=5, pady=2)
        
        
        # Theme
        theme_frame = ttk.Frame(other_frame)
        theme_frame.pack(padx=5, pady=(5, 8), fill="x")
        ttk.Label(theme_frame, text="Theme: (will need to reopen)").pack(anchor="w", padx=5, pady=(2, 4))
        self.theme_var = tk.StringVar(value="dark")
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                      values=["dark", "light"], state="readonly")
        theme_combo.pack(fill="x", padx=5, pady=2)
        
    
    def create_buttons(self):
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=(5, 10), fill="x")
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side="right", padx=(5, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_settings).pack(side="right", padx=5)
    
    def save_settings(self):
        # Set a flag to indicate settings were saved
        self.settings_saved = True
        # Store current values
        try:
            self.final_settings = {
                'psm_mode': int(self.psm_var.get().split()[0]),
                'auto_scale': self.scale_var.get(),
                'min_size': int(self.min_size.get()),
                'scale_factor': float(self.scale_factor.get()),
                'grayscale': self.grayscale_var.get(),
                'save_images': self.save_images_var.get(),
                'existing_weapon': self.existing_weapon_var.get(),
                'theme': self.theme_var.get() if hasattr(self, 'theme_var') else 'dark',
                'use_adaptive_threshold': self.adaptive_threshold_var.get(),
                'threshold': int(self.block_size_var.get()),
                'threshold_max': int(self.c_value_var.get())
            }
            # Save settings to a JSON file
            with open('settings.json', 'w') as f:
                json.dump(self.final_settings, f, indent=4)
                
        
                
                
                
        except ValueError as e:
            messagebox.showerror("Error", "Invalid numeric value in settings")
            return
        self.window.destroy()
    
    def cancel_settings(self):
        # Set a flag to indicate settings were cancelled
        self.settings_saved = False
        self.window.destroy()

def process_image_to_template(image, weapon_type='pointdefense', settings=None):

    text = ocr.scan_image(image, weapon_type, settings)

    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = next((line for line in lines if line.strip()), "Unknown Weapon")
    
    # Check if weapon already exists in the database
    if( settings['existing_weapon'] ):
        exists, existing_entry = check_weapon_exists(weapon_name, weapon_type)
        if exists:
            if existing_entry:
                messagebox.showwarning(
                    "Weapon Already Exists",
                    f"The weapon '{weapon_name}' already exists in the database.\n\n"
                    f"Existing entry:\n{existing_entry}\n\n"
                    "You can continue processing to compare the values."
                )
            else:
                messagebox.showwarning(
                    "Weapon Already Exists",
                    f"The weapon '{weapon_name}' already exists in the database."
                )
            print(f"Weapon '{weapon_name}' already exists in the database.")
        else:
            print(f"Weapon '{weapon_name}' does not exist in the database.")
    
    if weapon_type == "pointdefense":
        output = pointdefense.processPointDefense(text)
    elif weapon_type == "laser":
        output = laser.processLaser(text)
    elif weapon_type == "missile":
        output = missile.processMissile(text)
    elif weapon_type == "beam":
        output = sustainedbeam.processSustainedBeam(text)
    elif weapon_type == "fighter":
        output = fighter.processFighter(text)
    elif weapon_type == "fighterweapon":
        output = fighterweapon.processFighterWeapon(text)
    else:
        raise ValueError(f"Unknown weapon type: {weapon_type}")
    

    return output




def check_weapon_exists(weapon_name, weapon_type='pointdefense'):
    """
    Check if a weapon already exists in the wiki database
    Returns (exists, details) where exists is a boolean and details is the existing entry if found
    """
    try:
        # URLs for different weapon types
        urls = {
            'pointdefense': 'https://projectstardustwiki.miraheze.org/wiki/Module:PointDefense/Data',
            'laser': 'https://projectstardustwiki.miraheze.org/wiki/Module:Laser/Data',
            'missile': 'https://projectstardustwiki.miraheze.org/wiki/Module:Missile/Data',
            'beam': 'https://projectstardustwiki.miraheze.org/wiki/Module:SustainBeam/Data'
        }
        
        # Get the appropriate URL
        url = urls.get(weapon_type)
        if not url:
            print(f"Unknown weapon type: {weapon_type}")
            return False, None
            
        # Set up headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        # Fetch the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different methods to find the Lua code
        lua_code = None
        
        # Method 1: Try finding highlighted code block
        content = soup.find('div', {'class': 'mw-highlight'})
        if content:
            lua_code = content.get_text()
        
        # Method 2: Try finding pre element (used for plaintext)
        if not lua_code:
            pre_content = soup.find('pre')
            if pre_content:
                lua_code = pre_content.get_text()
        
        # Method 3: Try finding mw-content-text div
        if not lua_code:
            text_content = soup.find('div', {'id': 'mw-content-text'})
            if text_content:
                lua_code = text_content.get_text()
        
        if not lua_code:
            print(f"Could not find weapon data for \"{weapon_name}\" in {url}")
            return False, None
            
        # Create a pattern to match weapon names in the Lua code
        # This looks for ["weapon name"] = { pattern
        weapon_pattern = re.compile(r'\[[\'"](.*?)[\'"]\]\s*=\s*{', re.IGNORECASE)
        
        # Find all weapon names
        weapon_names = weapon_pattern.findall(lua_code)
        
        # Clean up the weapon name for comparison (remove extra spaces and make case-insensitive)
        clean_name = weapon_name.strip().lower()
        
        # Check if the weapon exists
        for existing_name in weapon_names:
            if clean_name == existing_name.strip().lower():
                # If found, try to extract the full entry
                entry_pattern = re.compile(fr'\[[\'"]{re.escape(existing_name)}[\'"]\]\s*=\s*{{.*?}},', re.DOTALL)
                entry_match = entry_pattern.search(lua_code)
                if entry_match:
                    return True, entry_match.group(0)
                return True, None
                
        return False, None
        
    except Exception as e:
        print(f"Error checking weapon existence: {str(e)}")
        return False, None

def main():
    root = tk.Tk()
    
    # Open json only for the theme
    
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            theme = settings.get('theme', 'dark')
    except FileNotFoundError:
        theme = 'dark'  # Default to dark if settings file doesn't exist
        
        
    # Set the theme
    try:
        with open("theme/sv.tcl", 'r') as f:
            root.tk.call("source", f.name)
            style = ttk.Style(master=root)
            style.theme_use(f"sun-valley-{theme}")
    except Exception as e:
        print(f"Error setting theme: {str(e)}")  
    
    # Set photo
    try:
        with open("theme/icon.png", 'r') as f:
            photo = PhotoImage(file=f.name)
            root.iconphoto(False, photo) 
    except Exception as e:
        print(f"Error loading icon: {str(e)}")

    app = WeaponStatsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
