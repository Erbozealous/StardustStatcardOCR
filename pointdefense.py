import re
def processPointDefense(text, removeEmpty=False):
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
    accuracyvalues = re.search(r'^Accuracy Values.*\n(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?', text, re.MULTILINE)
    if accuracyvalues:
        accuracyvalues_string = accuracyvalues.group(1)
        num = 2
        while accuracyvalues.group(num):
            accuracyvalues_string += " <br> " + accuracyvalues.group(num)
            num+=1
        template['accuracy'] = accuracyvalues_string

    
    # Missile Accuracy
    missileaccuracy = re.search(r'Missile Accuracy Values.*\n(.+km).*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?Spacecraft', text, re.MULTILINE)
    if missileaccuracy:
        missile_mod_string = missileaccuracy.group(1)
        num = 2
        while missileaccuracy.group(num):
            missile_mod_string += " <br> " + missileaccuracy.group(num)
            num+=1
        template['missileaccuracy'] = missile_mod_string
    

    
     # spacecraftaccuracy
    spacecraftaccuracy = re.search(r'Spacecraft Accuracy Values.*\n(.+km).*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?(.+km)?.*\n?', text, re.MULTILINE)
    if spacecraftaccuracy:
        space_mod_string = spacecraftaccuracy.group(1)
        num = 2
        while spacecraftaccuracy.group(num):
            space_mod_string += " <br> " + spacecraftaccuracy.group(num)
            num+=1
        template['spacecraftaccuracy'] = space_mod_string



    # missilehitchance
    missilehitchance = re.search(r'Missile Hitchance\D+(\d+)', text)
    if missilehitchance:
        template['missilehitchance'] = missilehitchance.group(1) + "%"

    # spacecrafthitchance
    spacecrafthitchance = re.search(r'Spacecraft Hitchance\D+(\d+)', text)
    if spacecrafthitchance:
        template['spacecrafthitchance'] = spacecrafthitchance.group(1) + "%"
    
    # Extract Accuracy
    accuracy = re.search(r'^(?!.*Values|.*Info)Accuracy\D+(\d+.?\d).$', text, re.MULTILINE)
    # Accuracy is mutually exclusive with other forms of accuracy
    if accuracy and (not missileaccuracy or not spacecraftaccuracy) and (not accuracyvalues or not modrange or not missilehitchance or not spacecrafthitchance):
        template['accuracy'] = accuracy.group(1) + "%"

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
        if(removeEmpty):
            if value:
                output += f"    ['{key}'] = '{value}',\n"
        else:
            output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
    return output

