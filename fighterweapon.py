import re
def processFighterWeapon(text):
    # This is the biggest template so far this is gonna be horrible to write
    template = {
        'shipfiringrange': '',
        'shipmaxrange': '',
        'shipactive': '',
        'shippassive': '',

        'damage': '',
        'shieldmulti': '',
        'shieldbypass': '',

        'heal': '',
        'healmulti': '',
        'healbypass': '',

        'fighterfiringrange': '',
        'fightermaxrange': '',
        'fighteractive': '',
        'fighterpassive': '',
        'fighterdamage': '',

        'bursts': '',
        'burstsshots': '',
        'burstsdelay': '',

        'objectives': '',
        'reload': '',
        'ammo': '',
        'speed': '',
        }
    

    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = re.sub(r"@", "0", next((line for line in lines if line.strip()), "Unknown Weapon"))

    # This one is a little different as the weapon name is prefixed with the parent fighter so we can just remove all text before the ]
    weapon_name = re.sub(r".*\] ", "", weapon_name)

    # Then exclude the first line from further processing
    text = '\n'.join(lines[1:])


    # Like in sustained beam there will be lines with the exact same prefix so we need to be careful with the order

    # Against Ship
    # Section is headed with "Against Ship" so we will preface all our regexes with that
    
    againstShipSection = r'(?s)gain[^0-9\n]+hip\b.*?'

    # shipfiringrange
    shipfiringrange = re.search(againstShipSection + r'Fir[^@0-9\n]+([@\d]+)', text)
    if shipfiringrange:
        template['shipfiringrange'] = shipfiringrange.group(1)
    
    # shipmaxrange
    shipmaxrange = re.search(againstShipSection + r'Max[^@0-9\n]+([@\d]+)', text)
    if shipmaxrange:
        template['shipmaxrange'] = shipmaxrange.group(1)

    # shipactive
    shipactive = re.search(againstShipSection + r'Act[^0-9\n]+ity:? ([^\n]*)', text)
    if shipactive:
        template['shipactive'] = shipactive.group(1)

    # shippassive
    shippassive = re.search(againstShipSection + r'Pas[^0-9\n]+ity:? ([^\n]*)', text)
    if shippassive:
        template['shippassive'] = shippassive.group(1)
    

    # Damage information
    # Guess what! Another prefix! Yay!
    damageSection = r'(?s)Da[mn][^@0-9\n]+tion\b.*?'


    # damage
    damage = re.search(damageSection + r'Da[mn][^@0-9\n]+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?', text)
    if(damage):
        template['damage'] = damage.group(1) + " - " + damage.group(2) 
    
    # shieldmulti
    shieldmulti = re.search(damageSection + r'Multi[^0-9@\n]+([@\d]+\.?[@\d]*)', text)
    if shieldmulti:
        template['shieldmulti'] = shieldmulti.group(1) + "x"

    # shieldbypass
    shieldbypass = re.search(damageSection + r'Byp[^0-9\n]+(Yes|No)', text)
    if shieldbypass:
        template['shieldbypass'] = shieldbypass.group(1)
    

    # I bet you can't guess what comes next
    healSection = r'(?s)Hea[^@0-9\n]+tion\b.*?'

    # Thank god we can just copy the damage information section

    # heal
    heal = re.search(healSection + r'Hea[^0-9@\n]+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?', text)   
    if(heal):
        template['heal'] = heal.group(1) + " - " + heal.group(2)

    # healmulti
    healmulti = re.search(healSection + r'Multi[^0-9@\n]+([@\d]+\.?[@\d]*)', text)
    if healmulti:
        template['healmulti'] = healmulti.group(1) + "x"

    # healbypass
    healbypass = re.search(healSection + r'Byp[^0-9\n]+(Yes|No)', text)
    if healbypass:
        template['healbypass'] = healbypass.group(1) 


    # Spacecraft Stats
    fighterSection = r'(?s)gai[^@0-9\n]+aft\b.*?'

     # shipfiringrange
    fighterfiringrange = re.search(fighterSection + r'Fir[^@0-9\n]+([@\d]+)', text)
    if fighterfiringrange:
        template['fighterfiringrange'] = fighterfiringrange.group(1)
    
    # shipmaxrange
    fightermaxrange = re.search(fighterSection + r'Max[^@0-9\n]+([@\d]+)', text)
    if fightermaxrange:
        template['fightermaxrange'] = fightermaxrange.group(1)

    # shipactive
    fighteractive = re.search(fighterSection + r'Act[^0-9\n]+ity:? ([^\n]*)', text)
    if fighteractive:
        template['fighteractive'] = fighteractive.group(1)

    # shippassive
    fighterpassive = re.search(fighterSection + r'Pas[^0-9\n]+ity:? ([^\n]*)', text)
    if fighterpassive:
        template['fighterpassive'] = fighterpassive.group(1)

    # fighterdamage
    fighterdamage = re.search(fighterSection + r'Da[mn][^0-9@]+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?', text)
    if(fighterdamage):
        template['fighterdamage'] = fighterdamage.group(1) + " - " + fighterdamage.group(2)

    # Burst section


     # burst
    burst = re.search(r'^Bursts[^0-9\n]+([\d@]+)', text, re.MULTILINE)
    if burst:
        template['burst'] = burst.group(1) + " x"
    
    # burstsshots
    burstsshots = re.search(r'hots[^0-9\n]+([\d@]+)', text)
    if burstsshots:
        template['burstsshots'] = burstsshots.group(1) + " x"

    # burstsdelay
    burstsdelay = re.search(r'Del[^@\d]*([\d@]+\.?[@\d]*)', text)
    if burstsdelay:
        template['burstsdelay'] = burstsdelay.group(1) + " s"


    # Other information

    # objectives
    objectives = re.search(r'Obj[^0-9\n@]*(Yes|No)', text)
    if objectives:
        template['objectives'] = objectives.group(1)


    # reload
    reload = re.search(r'^Reload\D*(\d*\.?\d*)[^0-9\r\n]*(\d*\.?\d*)?', text, re.MULTILINE)
    if reload:
        template['reload'] = reload.group(1) + " - " + reload.group(2) + " s"
    
    # ammo
    # either num or infinite
    ammo = re.search(r'ount[^0-9@]+([\d@]+|nite)', text)
    if ammo:
        if ammo.group(1).lower() == "nite":
            template['ammo'] = "Infinite"
        else:
            template['ammo'] = ammo.group(1)

    # speed
    speed = re.search(r'eed[^0-9\n@]*([\d@]+|Instant)', text)
    if speed:
        if speed.group(1) == "Instant":
            template['speed'] = "Instant"
        else:
            template['speed'] = speed.group(1) + " m/s"

    # for loop to remove all @
    for key, value in template.items():
        template[key] = re.sub(r"@", "0", value)

    # packaging the output
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"

    return output