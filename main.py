import pytesseract
from PIL import Image, ImageGrab
import re
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import io
from tkinter import messagebox
import subprocess
import tempfile
import os
import platform

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
                result = process_image_to_template(file_path, self.weapon_type.get())
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
                
                result = process_image_from_pil(image, self.weapon_type.get())
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
                result = process_image_from_pil(image, self.weapon_type.get())
                
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


def process_image_from_pil(image, weapon_type='pointdefense'):
    # Extract text using pytesseract
    text = pytesseract.image_to_string(image)
    print("Extracted text from image:")
    print("---START OF TEXT---")
    print(text)
    print("---END OF TEXT---")
    return process_text_to_template(text, weapon_type)

def process_image_to_template(image_path, weapon_type='pointdefense'):
    # Read the image using PIL
    image = Image.open(image_path)
    
    # Extract text from image using pytesseract
    text = pytesseract.image_to_string(image)
    
    # Initialize the template with empty values
    template = {
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
    }
    
    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = next((line for line in lines if line.strip()), "Unknown Weapon")
    
    # Process text and fill template
    # Look for specific patterns in the text
    if "Spacecraft Damage:" in text:
        damage_match = re.search(r'Spacecraft Damage:.*?(\d+\s*-\s*\d+)', text)
        if damage_match:
            template['spacedamage'] = damage_match.group(1)
    
    # Extract Maximum Range
    range_match = re.search(r'Maximum Range:.*?(\d+(?:\.\d+)?\s*km)', text)
    if range_match:
        template['range'] = range_match.group(1)
    
    # Extract Muzzle Velocity
    mv_match = re.search(r'Muzzle Velocity:.*?(\d+\s*m/s)', text)
    if mv_match:
        template['MV'] = mv_match.group(1)
    
    # Extract Reload Time
    reload_match = re.search(r'Reload:.*?(\d+(?:\.\d+)?\s*s)', text)
    if reload_match:
        template['reload'] = reload_match.group(1)
    
    # Extract Accuracy
    accuracy_match = re.search(r'Accuracy:.*?(\d+%)', text)
    if accuracy_match:
        template['accuracy'] = accuracy_match.group(1)
    
    # Extract Prioritized Type
    type_match = re.search(r'Prioritized Type:.*?([\w\s]+)', text)
    if type_match:
        template['prioritizedtype'] = type_match.group(1).strip()
    
    # Extract Prioritized Proximity
    prox_match = re.search(r'Prioritized Proximity:.*?([\w\s]+)', text)
    if prox_match:
        template['prioritizedprox'] = prox_match.group(1).strip()
    
    # Format the output string
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
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

def process_text_to_template(text, weapon_type='pointdefense'):
    # Initialize the template with empty values based on weapon type
    template = get_template_for_type(weapon_type)
    
    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = next((line for line in lines if line.strip()), "Unknown Weapon")
    
    # Process text and fill template
    print("\nSearching for patterns:")
    
    # Look for Spacecraft Damage (handle with or without colon)
    damage_patterns = [
        r'Spacecraft Damage:?\s*(\d+\s*-\s*\d+)',
        r'Spacecraft Damage\s*(\d+\s*-\s*\d+)'
    ]
    for pattern in damage_patterns:
        damage_match = re.search(pattern, text, re.IGNORECASE)
        if damage_match:
            template['spacedamage'] = damage_match.group(1)
            print(f"Spacecraft Damage found: {damage_match.group(1)}")
            break
    else:
        print("No Spacecraft Damage match found")
    
    # Extract Maximum Range (handle with or without colon, and km/kn variations)
    range_patterns = [
        r'Maximum Range:?\s*(\d+(?:\.\d+)?\s*k[mn])',
        r'Maximum Range\s*(\d+(?:\.\d+)?\s*k[mn])'
    ]
    for pattern in range_patterns:
        range_match = re.search(pattern, text, re.IGNORECASE)
        if range_match:
            template['range'] = range_match.group(1)
            print(f"Range found: {range_match.group(1)}")
            break
    else:
        print("No Range match found")
    
    # Extract Muzzle Velocity (handle with or without colon)
    mv_patterns = [
        r'Muzzle Velocity:?\s*(\d+(?:\.\d+)?\s*m/s)',
        r'Muzzle Velocity\s*(\d+(?:\.\d+)?\s*m/s)'
    ]
    for pattern in mv_patterns:
        mv_match = re.search(pattern, text, re.IGNORECASE)
        if mv_match:
            template['MV'] = mv_match.group(1)
            print(f"Muzzle Velocity found: {mv_match.group(1)}")
            break
    else:
        print("No Muzzle Velocity match found")
    
    # Extract Reload Time (handle with or without colon and optional space before s)
    reload_patterns = [
        r'Reload:?\s*(\d+(?:\.\d+)?)\s*s?',
        r'Reload\s*(\d+(?:\.\d+)?)\s*s?'
    ]
    for pattern in reload_patterns:
        reload_match = re.search(pattern, text, re.IGNORECASE)
        if reload_match:
            # Always ensure the value ends with " s"
            value = reload_match.group(1).strip()
            template['reload'] = f"{value} s"
            print(f"Reload Time found: {value} s")
            break
    for pattern in reload_patterns:
        reload_match = re.search(pattern, text, re.IGNORECASE)
        if reload_match:
            template['reload'] = reload_match.group(1)
            print(f"Reload Time found: {reload_match.group(1)}")
            break
    else:
        print("No Reload Time match found")
    
    # Extract Accuracy (handle with or without colon)
    accuracy_patterns = [
        r'Accuracy:?\s*(\d+%)',
        r'Accuracy\s*(\d+%)',
        r'Accuracy:?\s*(\d+)\s*%',
        r'Accuracy\s*(\d+)\s*%'
    ]
    for pattern in accuracy_patterns:
        accuracy_match = re.search(pattern, text, re.IGNORECASE)
        if accuracy_match:
            acc_value = accuracy_match.group(1)
            if not acc_value.endswith('%'):
                acc_value = f"{acc_value}%"
            template['accuracy'] = acc_value
            print(f"Accuracy found: {acc_value}")
            break
    else:
        print("No Accuracy match found")

    # Process weapon type specific patterns
    if weapon_type == 'laser' or weapon_type == 'beam' or weapon_type == 'missile':
        # Extract Burst info
        burst_patterns = [
            r'Burst:?\s*(\d+)',
            r'Burst Count:?\s*(\d+)'
        ]
        for pattern in burst_patterns:
            burst_match = re.search(pattern, text, re.IGNORECASE)
            if burst_match:
                template['burst'] = burst_match.group(1)
                print(f"Burst found: {burst_match.group(1)}")
                break
        else:
            print("No Burst match found")

        # Extract Burst Shots
        burst_shots_patterns = [
            r'Burst Shots:?\s*(\d+)',
            r'Shots per Burst:?\s*(\d+)'
        ]
        for pattern in burst_shots_patterns:
            shots_match = re.search(pattern, text, re.IGNORECASE)
            if shots_match:
                template['burstsshots'] = shots_match.group(1)
                print(f"Burst Shots found: {shots_match.group(1)}")
                break
        else:
            print("No Burst Shots match found")

        # Extract Burst Delay
        burst_delay_patterns = [
            r'Burst Delay:?\s*(\d+(?:\.\d+)?)\s*s?',
            r'Delay between Bursts:?\s*(\d+(?:\.\d+)?)\s*s?'
        ]
        for pattern in burst_delay_patterns:
            delay_match = re.search(pattern, text, re.IGNORECASE)
            if delay_match:
                value = delay_match.group(1).strip()
                template['burstsdelay'] = f"{value} s"
                print(f"Burst Delay found: {value} s")
                break
        else:
            print("No Burst Delay match found")

    # Laser-specific patterns
    if weapon_type == 'laser':
        # Extract damage values
        damage_patterns = {
            'startdamage': r'Starting Damage:?\s*(\d+(?:\.\d+)?)',
            'enddamage': r'Ending Damage:?\s*(\d+(?:\.\d+)?)',
            'damage': r'Base Damage:?\s*(\d+(?:\.\d+)?)',
            'shielddamage': r'Shield Damage:?\s*(\d+(?:\.\d+)?)',
            'shieldbypass': r'Shield Bypass:?\s*(\d+(?:\.\d+)?)',
        }
        for key, pattern in damage_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                template[key] = match.group(1)
                print(f"{key} found: {match.group(1)}")

        # Extract dispersion
        dispersion_patterns = {
            'dispersion': r'Dispersion:?\s*(\d+(?:\.\d+)?)',
            'dispersionmax': r'Maximum Dispersion:?\s*(\d+(?:\.\d+)?)',
        }
        for key, pattern in dispersion_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                template[key] = match.group(1)
                print(f"{key} found: {match.group(1)}")

    # Beam-specific patterns
    elif weapon_type == 'beam':
        # Extract healing values
        healing_patterns = {
            'starthealing': r'Starting Healing:?\s*(\d+(?:\.\d+)?)',
            'endhealing': r'Ending Healing:?\s*(\d+(?:\.\d+)?)',
            'healing': r'Base Healing:?\s*(\d+(?:\.\d+)?)',
            'shieldhealing': r'Shield Healing:?\s*(\d+(?:\.\d+)?)',
            'hshieldbypass': r'Healing Shield Bypass:?\s*(\d+(?:\.\d+)?)',
        }
        for key, pattern in healing_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                template[key] = match.group(1)
                print(f"{key} found: {match.group(1)}")

        # Extract total and range values
        total_patterns = {
            'total': r'Total Damage:?\s*(\d+(?:\.\d+)?)',
            'htotal': r'Total Healing:?\s*(\d+(?:\.\d+)?)',
            'maxrange': r'Maximum Range:?\s*(\d+(?:\.\d+)?)',
            'hmaxrange': r'Healing Range:?\s*(\d+(?:\.\d+)?)',
        }
        for key, pattern in total_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                template[key] = match.group(1)
                print(f"{key} found: {match.group(1)}")

    # Missile-specific patterns
    elif weapon_type == 'missile':
        # Extract missile-specific values
        missile_patterns = {
            'HP': r'Hit Points:?\s*(\d+)',
            'ASW': r'Anti-Submarine:?\s*(\d+)',
            'disruption': r'Disruption:?\s*(\d+)',
        }
        for key, pattern in missile_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                template[key] = match.group(1)
                print(f"{key} found: {match.group(1)}")

    # Common fields for all weapon types
    if weapon_type != 'pointdefense':
        # Extract objectives and charge
        objectives_pattern = r'Objectives:?\s*(\d+)'
        match = re.search(objectives_pattern, text, re.IGNORECASE)
        if match:
            template['objectives'] = match.group(1)
            print(f"Objectives found: {match.group(1)}")

        charge_pattern = r'Charge Time:?\s*(\d+(?:\.\d+)?)\s*s?'
        match = re.search(charge_pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            template['charge'] = f"{value} s"
            print(f"Charge Time found: {value} s")

        # Extract auto-aim
        autoaim_pattern = r'Auto-?aim:?\s*(\d+)'
        match = re.search(autoaim_pattern, text, re.IGNORECASE)
        if match:
            template['autoaim'] = match.group(1)
            print(f"Auto-aim found: {match.group(1)}")

    # Point Defense specific patterns (original code)
    if weapon_type == 'pointdefense':
        # Extract Prioritized Type
        type_patterns = [
        r'Prioritized Type:?\s*([^\n]+)',
        r'Prioritized Type\s*([^\n]+)'
        ]   
    for pattern in type_patterns:
        type_match = re.search(pattern, text, re.IGNORECASE)
        if type_match:
            value = type_match.group(1).strip()
            # Remove any "BACK" text and extra whitespace
            value = re.sub(r'\s*BACK.*$', '', value)
            template['prioritizedtype'] = value
            print(f"Prioritized Type found: {value}")
            break
    else:
        print("No Prioritized Type match found")

    # Extract Prioritized Proximity
    prox_patterns = [
        r'Prioritized Proximity:?\s*([^\n]+)',
        r'Prioritized Proximity\s*([^\n]+)'
    ]
    for pattern in prox_patterns:
        prox_match = re.search(pattern, text, re.IGNORECASE)
        if prox_match:
            value = prox_match.group(1).strip()
            # Remove any "BACK" text and extra whitespace
            value = re.sub(r'\s*BACK.*$', '', value)
            template['prioritizedprox'] = value
            print(f"Prioritized Proximity found: {value}")
            break
    else:
        print("No Prioritized Proximity match found")
    
    # Format the output string
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
    return output

def main():
    root = tk.Tk()
    app = WeaponStatsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
