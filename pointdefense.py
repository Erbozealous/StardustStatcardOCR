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
    
    # Then exclude the first line from further processing
    text = '\n'.join(lines[1:])
    
    
    # Process text and fill template
    # Look for specific patterns in the text
    
    damage_match = re.search(r'Spacecraft Da[mn]age\D+(\d+)\D+(\d+)', text)
    if damage_match:
        template['spacedamage'] = damage_match.group(1) + " - " + damage_match.group(2)
    
    # Extract Maximum Range
    range_match = re.search(r'Maximum Range\D+([0-9]+\.?\d*)', text)
    if range_match:
        template['range'] = range_match.group(1) + " km"
    
    # Extract Muzzle Velocity
    mv_match = re.search(r'Muzzle Velocity[^\dIi]+(\d+|Instant)', text)
    if mv_match:
        if mv_match.group(1) == "Instant":
            template['MV'] = "Instant"
        else:
            template['MV'] = mv_match.group(1) + " m/s"
    
    # Extract Reload Time
    reload = re.search(r'Reload[^@\d]*([\d@]+\.?\d*)', text)
    if reload:
        # Replace '@' with '0' and append seconds
        template['reload'] = re.sub(r"@", "0", reload.group(1)) + " s"
    
    # modrange
    modrange = re.search(r'Modifi\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if modrange:
        template['modrange'] = modrange.group(1) + " km - " + modrange.group(2) + " km"


    # accuracyvalues
    accuracyvalues = re.search(r'^((?!Missile|Spacecraft).)*Accuracy Values.*\n(.+k[mn])?\n(.+k[mn])?\n(.+k[mn])?', text, re.MULTILINE)
    if accuracyvalues:
        print(accuracyvalues.group(2))
        print(accuracyvalues.group(3))
        print(accuracyvalues.group(4))
        accuracyvalues_string = accuracyvalues.group(2) + " <br> " + accuracyvalues.group(3)
        if accuracyvalues.group(4): accuracyvalues_string+=" <br> " + accuracyvalues.group(4)
        template['accuracyvalues'] = re.sub(r"kn", r"km", accuracyvalues_string)
        template['accuracyvalues'] = re.sub(r"@", "0", template['accuracyvalues']) # Replace '@' with '0'


    # Missile Accuracy
    missileaccuracy = re.search(r'Missile Accuracy Values.*\n(.+k[mn])?\n(.+k[mn])?\n(.+k[mn])?', text)
    if missileaccuracy:
        missile_mod_string = missileaccuracy.group(1) + " <br> " + missileaccuracy.group(2)
        if missileaccuracy.group(3): missile_mod_string+=" <br> " + missileaccuracy.group(3)
        template['missileaccuracy'] = re.sub(r"kn", r"km", missile_mod_string)
        # resub again to replace @ with 0
        template['missileaccuracy'] = re.sub(r"@", "0", template['missileaccuracy'])


     # spacecraftaccuracy
    spacecraftaccuracy = re.search(r'Spacecraft Accuracy Values.*\n(.+k[mn])?\n(.+k[mn])?\n(.+k[mn])?', text)
    if spacecraftaccuracy:
        space_mod_string = spacecraftaccuracy.group(1) + " <br> " + spacecraftaccuracy.group(2)
        if spacecraftaccuracy.group(3): space_mod_string+=" <br> " + spacecraftaccuracy.group(3)
        template['spacecraftaccuracy'] = re.sub(r"kn", r"km", space_mod_string)
        # resub again to replace @ with 0
        template['spacecraftaccuracy'] = re.sub(r"@", "0", template['spacecraftaccuracy'])

    # Extract Accuracy
    accuracy = re.search(r'^(?!.*Values|.*Info)Accuracy\D+(\d+.?\d).$', text, re.MULTILINE)
    # Accuracy is mutuall exclusive with other forms of accuracy
    if accuracy and (not missileaccuracy or not spacecraftaccuracy) and (not accuracyvalues or not modrange or not missilehitchance or not spacecrafthitchance):
        template['accuracy'] = accuracy.group(1) + "%"
        

    # missilehitchance
    missilehitchance = re.search(r'Missile Hitchance\D+(\d+)', text)
    if missilehitchance:
        template['missilehitchance'] = missilehitchance.group(1) + "%"

    # spacecrafthitchance
    spacecrafthitchance = re.search(r'Spacecraft Hitchance\D+(\d+)', text)
    if spacecrafthitchance:
        template['spacecrafthitchance'] = spacecrafthitchance.group(1) + "%"
    
    # Extract Prioritized Type
    type_match = re.search(r'Type.* ([\w\s][^\n]+)', text)
    if type_match:
        template['prioritizedtype'] = type_match.group(1).strip()
    
    # Extract Prioritized Proximity
    prox_match = re.search(r'Prox.* ([\w\s][^\n]+)', text)
    if prox_match:
        template['prioritizedprox'] = prox_match.group(1).strip()
    
    # Format the output string
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
    return output

