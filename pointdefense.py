import re
def processPointDefense(text):
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
    weapon_name = re.sub(r"@", "0", next((line for line in lines if line.strip()), "Unknown Weapon"))
    
    # Process text and fill template
    # Look for specific patterns in the text
    
    damage_match = re.search(r'Spacecraft Da[mn]age\D+(\d+)\D+(\d+)', text)
    if damage_match:
        template['spacedamage'] = damage_match.group(1) + " - " + damage_match.group(2)
    
    # Extract Maximum Range
    range_match = re.search(r'Maximum Range\D+([0-9]+)', text)
    if range_match:
        template['range'] = range_match.group(1) + " km"
    
    # Extract Muzzle Velocity
    mv_match = re.search(r'Muzzle Velocity\D+(\d+)', text)
    if mv_match:
        template['MV'] = mv_match.group(1) + " m/s"
    
    # Extract Reload Time
    reload_match = re.search(r'Reload[^@.]*([\d@]+\.?\d*)', text)
    if reload_match:
        # Replace '@' with '0' and append seconds
        template['reload'] = re.sub(r"@", "0", reload_match.group(1)) + " s"
    
    # Modifier Accuracy
    modrange_match = re.search(r'^((?!Missile|Spacecraft).)*Accuracy Values.*\n(.+k[mn])?\n(.+k[mn])?\n(.+k[mn])?', text)
    if modrange_match:
        modrange_string = modrange_match.group(1) + " <br> " + modrange_match.group(2)
        if modrange_match.group(3): modrange_string+=" <br> " + modrange_match.group(3)
        template['accuracyvalues'] = re.sub(r"kn", r"km", modrange_string)


    # Extract Accuracy
    accuracy_match = re.search(r'Accuracy\D*(\d+.?\d)', text)
    if accuracy_match:
        template['accuracy'] = accuracy_match.group(1) + "%"
    
    # Extract Prioritized Type
    type_match = re.search(r'Prioritized Type.* ([\w\s][^\n]+)', text)
    if type_match:
        template['prioritizedtype'] = type_match.group(1).strip()
    
    # Extract Prioritized Proximity
    prox_match = re.search(r'Prioritized Proximity.* ([\w\s][^\n]+)', text)
    if prox_match:
        template['prioritizedprox'] = prox_match.group(1).strip()
    
    # Format the output string
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
    return output

