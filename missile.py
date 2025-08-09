import re
def processMissile(text):
    template = {
        'burst':'',
        'burstsshots':'',
        'burstsdelay':'',
        'damage':'',
        'shielddamage':'',
        'shieldbypass':'',
        'ASW':'',
        'HP':'',
        'disruption':'',
        'objectives':'',
        'charge':'',
        'reload':'',
        'range':'',
        'MV':'',
        'autoaim':'',
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


    # damage
    damage = re.search(r'(?!.*Info)Da[nm]age\D+([\d@]+\.?[\d@]*)\D+([\d@]+\.?[\d@]*)$', text, re.MULTILINE)
    if(damage):
       template['damage'] =  re.sub(r"@", "0", damage.group(1) + " - " + damage.group(2))
        

    # shielddamage
    shielddamage = re.search(r'Shield Damage Multiplier\D*(\d+\.?\d*)', text)
    if shielddamage:
        template['shielddamage'] = shielddamage.group(1) + "x"

    # shieldbypass
    shieldbypass = re.search(r'Gate.*(No|Yes)', text)
    if shieldbypass:
        template['shieldbypass'] = shieldbypass.group(1)

    # ASW
    asw = re.search(r'Lock[^0-9@i]*([\di@]*)', text)
    if asw:
        template['ASW'] = re.sub(r"@", "0", asw.group(1))
        template['ASW'] = re.sub(r"i", "1" , template['ASW']) + " m"


    # HP
    missileHP = re.search(r'HP[^0-9\n\r]*([\d@]+)', text)
    if missileHP:
        template['HP'] = re.sub(r"@", "0", missileHP.group(1)) + " HP"

    # disruption
    disruption = re.search(r'mmune.*(No|Yes)', text)
    if disruption:
        template['disruption'] = disruption.group(1)

    # objectives
    objectives = re.search(r'Objective\D*(No|Yes)', text)
    if objectives:
        template['objectives'] = objectives.group(1)

    # charge
    charge = re.search(r'^Charge\D*(\d*\.?\d*)', text, re.MULTILINE)
    if charge:
        template['charge'] = re.sub(r"@", "0", charge.group(1)) + " s"

    # reload
    reload = re.search(r'^Reload\D*(\d*\.?\d*)[^0-9\r\n]*(\d*\.?\d*)?', text, re.MULTILINE)
    if reload:
        if reload.group(2):
            template['reload'] = re.sub(r"@", "0", reload.group(1) + " s - " + reload.group(2) + " s" )
        else:
            template['reload'] = re.sub(r"@", "0", reload.group(1)) + " s"

    # range
    range_match = re.search(r'Max\D*(\d*\.?\d*)', text)
    if range_match:

        # Catch edge case where OCR reads X0 as X2
        if int(range_match.group(1)) and int(range_match.group(1)) % 10 == 2:
            template['range'] = str(int(range_match.group(1)) - 2) + " km"

    # MV
    muzzlevelocity = re.search(r'eed\D*(\d+)', text)
    if muzzlevelocity:
            template['MV'] = muzzlevelocity.group(1) + " m/s"


    # autoaim
    autoaim = re.search(r'Aim', text)
    if autoaim:
        template['autoaim'] = "Yes" # It only appears if the weapon has autoaim, so we set it to "Yes"
    # Honestly it's a missile of course aim is always "Yes" so we can skip this part if we want to


     # packaging the output
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"

    
    
    
    return output

