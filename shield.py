import re
def processShield(text):
    template = {
        'capacity' : '',
        'delay' : '',
        'recharge' : '',
        'passive' : '',
        'initialrecharge' : '',  
        'maxtolerance' : '',
        'toleranceregen' : '',
        'regenmult' : '',
        'maxregen' : '',
        'gating' : '',
        }
    


    weapon_name = ""

    

    # capacity
    capacity = re.search(r'Shield Capacity: ([^\n]*) SHP', text)
    if capacity:
        template['capacity'] = re.sub(' ', ',',capacity.group(1)) 

    # delay
    delay = re.search(r'Delay Time: ([^\n]*)', text)
    if delay:
        template['delay'] = delay.group(1)


    # recharge
    recharge = re.search(r'^Shield Recharge[^:]*: ([^\n]*) S', text, re.MULTILINE)
    if recharge:
        template['recharge'] = re.sub(' ', ',',recharge.group(1)) + " SHP/s"

    # passive
    passive = re.search(f'Passive[^:]*: ([^\n]*) S', text)
    if passive:
        template['passive'] = passive.group(1) + " SHP/s"
    
    # initialrecharge
    initialrecharge = re.search(r'Initial[^:]*: ([^\n]*) S', text)
    if initialrecharge:
        template['initialrecharge'] = initialrecharge.group(1) + " SHP/s"


    # maxtolerance
    maxtolerance = re.search(r'^Max[^R:]*: ([^\n]*)', text, re.MULTILINE)
    if maxtolerance:
        template['maxtolerance'] = re.sub(' ', ',',maxtolerance.group(1)) 


    # toleranceregen
    toleranceregen = re.search(r'^Max[^S:]*Regen[^:]*: ([^\n]*)', text, re.MULTILINE)
    if toleranceregen:
        template['toleranceregen'] = toleranceregen.group(1)


    # regenmult
    regenmult = re.search(r'Multiplier[^:]*: ([^\n]*)',text)
    if regenmult:
        template['regenmult'] = regenmult.group(1)


    # maxregen
    maxregen = re.search(r'Max Shield[^:]*: ([^\n]*)', text)
    if maxregen:
        template['maxregen'] = maxregen.group(1)


    # gating
    gating = re.search(r'Gating[^:]*: ([^\n]*)', text)
    if gating:
        template['gating'] = gating.group(1)




    # packaging the output
    # output = f"['{weapon_name}'] = {{\n"
    output = "{{Tooltip|" + template['capacity'] + "|\n"
    output +="{{ShieldInfobox\n"
    for key, value in template.items():
        output += f"| {key} = {value}\n"
    output += "}}}}"

    return output
