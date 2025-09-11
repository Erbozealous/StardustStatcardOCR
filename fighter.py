import re
def processFighter(text):
    template = {
        'health': '',
        'evasion': '',
        'respawn': '',
        'squadronsize': '',
        'scramblehealth': '',
        'scrambletime': '',
        'sramblemulti': '',
        'maxrange': '',
        'speed': '',
        'orbit': '',
        'launch': '',
        'weapons': '', 
        }
    
    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = weapon_name = next((line for line in lines if line.strip()), "Unknown Weapon")
    # Then exclude the first line from further processing
    text = '\n'.join(lines[1:])

    # health
    health = re.search(r'Tot[^0-9\n]*Hea[^0-9\n]*(\d+)', text)
    if health:
        template['health'] = health.group(1)

    # evasion
    evasion = re.search(r'Eva[^0-9\n]*Cha[^0-9\n]*(\d+)', text)
    if evasion:
        template['evasion'] = evasion.group(1) + "%"

    # respawn
    respawn = re.search(r'Resp[^0-9\n]*(\d+)', text)
    if respawn:
        template['respawn'] = respawn.group(1) + " s"

    # squadronsize
    suadronsize = re.search(r'Squad[^0-9\n]*(\d+)', text)
    if suadronsize:
        template['squadronsize'] = suadronsize.group(1)

    # scramblehealth
    scramblehealth = re.search(r'Min[^0-9\n]*Hea[^0-9\n]*(\d+)', text)
    if scramblehealth:
        template['scramblehealth'] = scramblehealth.group(1) + " s"

    # scrambletime
    scrambletime = re.search(r'Min[^0-9\n]*Tim[^0-9\n]*(\d+)', text)
    if scrambletime:
        template['scrambletime'] = scrambletime.group(1) + " s"

    # sramblemulti
    sramblemulti = re.search(r'ramb[^0-9\n]+ulti[^0-9\n]*([\d]+\.?[\d]*)', text)
    if sramblemulti:
        template['sramblemulti'] = sramblemulti.group(1) + "x"

    # maxrange
    maxrange = re.search(r'ange[^0-9\d]*([\d]+)', text)
    if maxrange:
        template['maxrange'] = maxrange.group(1) + " m"

    # speed
    speed = re.search(r'ee[^0-9\n]*([\d]+)', text)
    if speed:
        template['speed'] = speed.group(1) + " m/s"

    # orbit
    orbit = re.search(r'Orb.*eed[^a-zA-Z0-9\n]*([\d]+|No)', text)
    if orbit:
        if orbit.group(1) == "No":
            template['orbit'] = "No Orbit"
        else:
            template['orbit'] = orbit.group(1) + " m/s"

    # launch
    launch = re.search(r'vior[^a-zA-Z0-9\n]([\w\s][^\n]+)', text)
    if launch:
        template['launch'] = launch.group(1).strip()

    # weapons
    weapons = re.search(r'Armaments[\n ]*([\w\s]+ >).*\n([\w\s][^\n]+ >)?.*\n?([\w\s][^\n]+ >)?', text)
    
    
    # prune last 2 chars from weapons if they exist



    if weapons:
        template['weapons'] = "{{Tooltip|" + weapons.group(1)[:-2] + "|{{FighterWeaponInfobox|" + weapons.group(1)[:-2] + "}}}}"
        if(weapons.group(2)):
            template['weapons'] += " <br> {{Tooltip|" + weapons.group(2)[:-2] + "|{{FighterWeaponInfobox|" + weapons.group(2)[:-2] + "}}}}"
        if(weapons.group(3)):
            template['weapons'] += " <br> {{Tooltip|" + weapons.group(3)[:-2] + "|{{FighterWeaponInfobox|" + weapons.group(3)[:-2] + "}}}}"



     # packaging the output
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"

    return output