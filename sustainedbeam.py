import re
def processSustainedBeam(text):
    template = {
        'burst':'',
        'burstsshots':'',
        'burstsdelay':'',
        'maxrange':'',
        'total':'',
        'modrange':'',
        'startdamage':'',
        'enddamage':'',
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

    # maxrange
    maxrange = re.search(r'Dur\D+Range[^0-9\n]*([\d@i]+)', text)
    if maxrange:
        template['maxrange'] = re.sub(r"@", "0", maxrange.group(1))
        template['maxrange'] = re.sub(r"i", "1", template['maxrange']) + " s"

    # total
    total = re.search(r'Tot\D+Dur\D+([\d@i]+\.?[\d@i]+)', text)
    if total:
        template['total'] = re.sub(r"@", "0", total.group(1))
        template['total'] = re.sub(r"i", "1", template['total']) + " s"

    # modrange
    modrange = re.search(r'Modifier Ranges\D+(\d+\.?\d*)\D+(\d+\.?\d*)', text)
    if modrange:
        template['modrange'] = modrange.group(1) + " km - " + modrange.group(2) + " km"

    # startdamage
    startdamage = re.search(r'Tot\D+Up\D+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?', text)
    if startdamage:
        template['startdamage'] = startdamage.group(1)
        if startdamage.group(2): template['startdamage'] += " - " + startdamage.group(2)
        template['startdamage'] = re.sub(r"@", "0", template['startdamage'])

    enddamage = re.search(r'Tot\D+Max\D+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?', text)
    if enddamage:
        template['enddamage'] = enddamage.group(1)
        if enddamage.group(2): template['enddamage'] += " - " + enddamage.group(2)
        template['enddamage'] = re.sub(r"@", "0", template['enddamage'])
    
    # damage
    damage = re.search(r'(?!.*Info)^Da[nm]age\D+([\d@]+\.?[\d@]*)[^0-9\n]*([\d@]+\.?[\d@]*)?[^0-9\n]+$', text, re.MULTILINE)
    if(damage):
        template['damage'] = damage.group(1) + " DPS"
        if(damage.group(2)): template['damage'] += " - " + damage.group(2) + " DPS"
        template['damage'] =  re.sub(r"@", "0", template['damage'])
        

    # shielddamage
    shielddamage = re.search(r'Multi[^0-9\n]*(\d+\.?\d*)[^0-9\n]*$', text, re.MULTILINE)
    if shielddamage:
        template['shielddamage'] = shielddamage.group(1) + "x"

    # shieldbypass
    shieldbypass = re.search(r'Gate.*(No|Yes)', text)
    if shieldbypass:
        template['shieldbypass'] = shieldbypass.group(1)

    # objectives
    objectives = re.search(r'Objective\D*(No|Yes)', text)
    if objectives:
        template['objectives'] = objectives.group(1)

    # charge
    charge = re.search(r'Charge[^0-9\r\n]*(\d\.?\d*).+$', text, re.MULTILINE)
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


    # Format the output string
    output = f"['{weapon_name}'] = {{\n"
    for key, value in template.items():
        output += f"    ['{key}'] = '{value}',\n"
    output += "},"
    
    return output
    