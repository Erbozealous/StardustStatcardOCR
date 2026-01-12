import re
def processSustainedBeam(text, removeEmpty=False):
    template = {
        'burst':'',
        'burstsshots':'',
        'burstsdelay':'',
        'maxrange':'',
        'total':'',
        'modrange':'',
        'modstartdamage':'',
        'modenddamage':'',
        'damage':'',
        'startdamage':'',
        'enddamage':'',
        'shielddamage':'',
        'shieldbypass':'',
        'hmaxrange':'',
        'htotal':'',
        'healing':'',
        'starthealing':'',
        'endhealing':'',
        'shieldhealing':'',
        'hshieldbypass':'',
        'objectives':'',
        'charge':'',
        'reload':'',
        'range':'',
        'MV':'',
        'dispersion':'',
        'dispersionmax':'',
        'autoaim':'',
        }
    
    # Extract weapon name (assumed to be in the first line)
    lines = text.split('\n')
    weapon_name = next((line for line in lines if line.strip()), "Unknown Weapon")

    # Then exclude the first line from further processing
    text = '\n'.join(lines[1:])

    # burst
    burst = re.search(r'Bursts\D*(\d+)', text)
    if burst:
        template['burst'] = burst.group(1) + " x"
    
    # burstsshots
    burstsshots = re.search(r'Shots Per Burst\D*(\d+)', text)
    if burstsshots:
        template['burstsshots'] = burstsshots.group(1) + " x"

    # burstsdelay
    burstsdelay = re.search(r'Delay Between Bursts[^\d]*([\d]+\.?\d*)', text)
    if burstsdelay:
        template['burstsdelay'] = burstsdelay.group(1) + " s"

    # maxrange
    maxrange = re.search(r'Dur\D+Range[^0-9\n]*([\di]+)', text)
    if maxrange:
        template['maxrange'] = maxrange.group(1) + " s"

    # total
    total = re.search(r'Tot\D+Dur\D+([\di]+\.?[\di]+)', text)
    if total:
        template['total'] = total.group(1) + " s"

    # modrange
    modrange = re.search(r'Modifier Ranges\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if modrange:
        template['modrange'] = modrange.group(1) + " km - " + modrange.group(2) + " km"

    # modstartdamage
    modstartdamage = re.search(r'Starting[^\d]+([\d\.]+)', text)
    if modstartdamage:
        template['modstartdamage'] = modstartdamage.group(1) + " DPS"

    # modenddamage
    modenddamage = re.search(r'Ending[^\d]+([\d\.]+)', text)
    if modenddamage:
        template['modenddamage'] = modenddamage.group(1) + " DPS"

    # startdamage
    startdamage = re.search(r'Close[^\d]+([\d\.]+)[- ]*([\d\.]+)?', text)
    if startdamage:
        template['startdamage'] = startdamage.group(1)
        if startdamage.group(2): template['startdamage'] += " - " + startdamage.group(2)

    enddamage = re.search(r'Damage at[^\d]+([\d\.]+)[- ]*([\d\.]+)?', text)
    if enddamage:
        template['enddamage'] = enddamage.group(1)
        if enddamage.group(2): template['enddamage'] += " - " + enddamage.group(2)
    
    # damage
    damage = re.search(r'Damage: ([\d\.]+)[ -DPS]*([\d\.]+)?', text, re.MULTILINE)
    if(damage):
        template['damage'] = damage.group(1) + " DPS"
        if(damage.group(2)): template['damage'] += " - " + damage.group(2) + " DPS"
        

    # shielddamage
    shielddamage = re.search(r'Multiplier: ([\d\.x]+)$', text, re.MULTILINE)
    if shielddamage:
        template['shielddamage'] = shielddamage.group(1)

    # shieldbypass
    shieldbypass = re.search(r'Gate.*(No|Yes)', text)
    if shieldbypass:
        template['shieldbypass'] = shieldbypass.group(1)


    # Healing section
    
    
    # hmaxrange
    healregex = r'Hea[^0-9\n]*In[\D\d]+'
    # We will preface all healing regexes with this
    
    hmaxrange = re.search(healregex + r'Dur\D+Range[^0-9\n]*([\di]+)', text)
    if hmaxrange:
        template['hmaxrange'] = template['hmaxrange'] + " s"
        
        
    # htotal
    htotal = re.search(healregex + r'Tot\D+Dur\D+([\di]+\.?[\di]+)', text)
    if htotal:
        template['htotal'] = htotal.group(1) + " s"

    # damage
    healing = re.search(r'^Healing[^0-9\n]*([\di]+)[^0-9\n]*([\di]+)', text, re.MULTILINE)
    if(healing):
        template['healing'] = healing.group(1) + " HPS"
        if(healing.group(2)): template['healing'] += " - " + healing.group(2) + " HPS"


    # starthealing
    starthealing = re.search(r'Tot[^0-9\n]*Heal[^0-9\n]*Up\D+([\d]+\.?[\d]*)[^0-9\n]*([\d]+\.?[\d]*)?', text, re.MULTILINE)
    if starthealing:
        template['starthealing'] = starthealing.group(1)
        if starthealing.group(2): template['starthealing'] += " - " + starthealing.group(2)
        template['starthealing'] = template['starthealing']

    endhealing = re.search(r'Tot[^0-9\n]+Hea[^0-9\n]+Max\D+([\d]+\.?[\d]*)[^0-9\n]*([\d]+\.?[\d]*)?', text, re.MULTILINE)
    if endhealing:
        template['endhealing'] = endhealing.group(1)
        if endhealing.group(2): template['endhealing'] += " - " + endhealing.group(2)
        

    # shieldhealing
    shieldhealing = re.search(r'He[^0-9\n]+Multi[^0-9\n]*(\d+\.?\d*)[^0-9\n]*$', text, re.MULTILINE)
    if shieldhealing:
        template['shieldhealing'] = shieldhealing.group(1) + "x"

    # hshieldbypass
    hshieldbypass = re.search(r'Hea[^0-9\n]*In[\D\d]+Gate.*(No|Yes)', text)
    if hshieldbypass:
        template['hshieldbypass'] = hshieldbypass.group(1)


    # objectives
    objectives = re.search(r'Objective\D*(No|Yes)', text)
    if objectives:
        template['objectives'] = objectives.group(1)

    # charge
    charge = re.search(r'Charge[^0-9\r\n]*(\d\.?\d*).+$', text, re.MULTILINE)
    if charge:
        template['charge'] = charge.group(1) + " s"

    # reload
    reload = re.search(r'^Reload\D*(\d*\.?\d*)[^0-9\r\n]*(\d*\.?\d*)?', text, re.MULTILINE)
    if reload:
        if reload.group(2):
            template['reload'] = reload.group(1) + " s - " + reload.group(2) + " s" 
        else:
            template['reload'] = reload.group(1) + " s"

    # range
    range_match = re.search(r'^Max\D*(\d*\.?\d*).*$', text, re.MULTILINE)
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
    dispersion = re.search(r'Angle[^\d]*([\d]+\.?\d*)', text)
    if dispersion:
        template['dispersion'] = dispersion.group(1) + " degrees"

    # dispersionmax
    dispersionmax = re.search(r'Dispersion At[^\d]*([\d]+\.?\d*)', text)
    if dispersionmax:
        template['dispersionmax'] = dispersionmax.group(1) + " m"
    
    # autoaim
    autoaim = re.search(r'Aim', text)
    if autoaim:
        template['autoaim'] = "Yes" # It only appears if the weapon has autoaim, so we set it to "Yes"


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
    