import re
def processLaser(text):
    template = {
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
            }
    
    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = re.sub(r"@", "0", next((line for line in lines if line.strip()), "Unknown Weapon"))

    # burst
    burst = re.search(r'Bursts\D*(\d+)', text)
    if burst:
        template['burst'] = burst.group(1) + " x"
    
    # burstsshots
    burstsshots = re.search(r'Shots Per Burst\D*(\d+)', text)
    if burstsshots:
        template['burstsshots'] = burstsshots.group(1) + " x"

    # burstsdelay
    burstsdelay = re.search(r'Delay Between Bursts[^@\d]*([\d@]+\.?\d*)', text)
    if burstsdelay:
        template['burstsdelay'] = re.sub(r"@", "0", burstsdelay.group(1)) + " s"

    # modrange
    modrange = re.search(r'Modifier Ranges\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if modrange:
        template['modrange'] = modrange.group(1) + " km - " + modrange.group(2) + " km"

    # startdamage
    startdamage = re.search(r'Starting Damage\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if startdamage:
        template['startdamage'] = startdamage.group(1) + " - " + startdamage.group(2)

    enddamage = re.search(r'Ending Damage\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if enddamage:
        template['enddamage'] = enddamage.group(1) + " - " + enddamage.group(2)
    
    # damage
    damage = re.search(r'(?!.*Info)Damage\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if(damage):
        template['damage'] = damage.group(1) + " - " + damage.group(2)

    # shielddamage
    shielddamage = re.search(r'Shield Damage Multiplier\D*(\d+\.?\d*)', text)
    if shielddamage:
        template['shielddamage'] = shielddamage.group(1) + "x"

    # shieldbypass
    shieldbypass = re.search(r'Shield Gate Bypass.*(No|Yes)', text)
    if shieldbypass:
        template['shieldbypass'] = shieldbypass.group(1)

    # objectives
    objectives = re.search(r'Objective\D*(No|Yes)', text)
    if objectives:
        template['objectives'] = objectives.group(1)

    # charge
    charge = re.search(r'Charge\D*(\d*\.?\d*)', text)
    if charge:
        template['charge'] = re.sub(r"@", "0", charge.group(1)) + " s"

    # reload
    reload = re.search(r'Reload\D*(\d*\.?\d*)\D*(\d*\.?\d*)?', text)
    if reload:
        if reload.group(2):
            template['reload'] = re.sub(r"@", "0", reload.group(1) + " s - " + reload.group(2) + " s" )
        else:
            template['reload'] = re.sub(r"@", "0", reload.group(1)) + " s"

    # range
    range_match = re.search(r'Max\D*(\d*\.?\d*)', text)
    if range_match:
        template['range'] = range_match.group(1) + " km"

    # MV
    muzzlevelocity = re.search(r'zz\D*(\d+|Instant)', text)
    if muzzlevelocity:
        if muzzlevelocity.group(1) == "Instant":
            template['MV'] = "Instant"
        else:
            template['MV'] = muzzlevelocity.group(1) + " m/s"
    
    # dispersion
    dispersion = re.search(r'Angle[^@\d]*([\d@]+\.?\d*)', text)
    if dispersion:
        template['dispersion'] = re.sub(r"@", "0", dispersion.group(1)) + " degrees"

    # dispersionmax
    dispersionmax = re.search(r'Dispersion At[^@\d]*([\d@]+\.?\d*)', text)
    if dispersionmax:
        template['dispersionmax'] = re.sub(r"@", "0", dispersionmax.group(1)) + " m"
    
    # autoaim
    autoaim = re.search(r'Aim', text)
    if autoaim:
        template['autoaim'] = "Yes" # It only appears if the weapon has autoaim, so we set it to "Yes"

    


     # packaging the output
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"

    return output
