import argparse, re, struct
from udsoncan.connections import IsoTPSocketConnection


identifier = {
        'BOOST': 'F1F8',
        'BOOSTMIN': 'FD30',
        'BOOSTMAX': 'FD31',
        'OCTANE': 'F1F9', 
        'OCTANEMIN': 'FD32',
        'OCTANEMAX': 'FD33',
        'ETHANOL': 'F1FD'
    }

params = {
  'tx_padding': 0x55
}
 
def send_raw(data):
    global params
    results = None
    while results == None:
        conn2 = IsoTPSocketConnection('can0', rxid=0x7E8, txid=0x7E0, params=params)
        conn2.tpsock.set_opts(txpad=0x55, tx_stmin=2500000)
        conn2.open()
        conn2.send(data)
        results = conn2.wait_frame()
        conn2.close()
    print(str(results))
    return results


def getSliderValues():
    global identifier
    print("Getting Slider values\n")
    for key in identifier:
        print("    Getting " + key + ", sending: 22" + identifier[key])
        #response = send_raw(bytes.fromhex('22' + identifier[key]))
        response = '67' + identifier[key] + '71'
        rawvalue = int.from_bytes(bytearray.fromhex(response[6:]),'little')
        if re.match('^BOOST.*', key):
            value = rawvalue / 0.047110065099374217 * 0.014503773773 - 15
        elif re.match('^ETHANOL.*', key):
            value = rawvalue / 1.28 + 1
        else:
            value = rawvalue
        print("        " + key + " is " + str(value))
        


def setSliderValue(slider = None, value = None):
    global identifier
    print("Setting " + slider + " with " + value)
    if slider is None:
        print("No slider specified, exiting")
        exit()
    if value is None:
        print("No value specified, exiting")
        exit()
    if re.match('^BOOST.*', slider):
        rawvalue = round((((int(value) + 16) / 0.014503773773) * 0.047110065099374217))
    elif re.match('^ETHANOL.*', slider):
        rawvalue = round(int(value) * 1.28)
    else:
        rawvalue = round(int(value))
    print("    Sending raw value: " + str(bytes([rawvalue]).hex()))
    print("    Sending: 2E" + identifier[slider] + bytes([rawvalue]).hex() )
    #response = send_raw(bytes.fromhex('2E' + identifier[slider] + rawvalue))
    response = "6E" + identifier[slider]
    print("    Response: " + str(response))


    

parser = argparse.ArgumentParser(description='Eurodyne Slider Adjuster')
parser.add_argument('--getSliders', help="Get the slider values from the ECU", action='store_true')
parser.add_argument('--setSlider',help="Used to set a slider value, specified by BOOST, OCTANE, ETHANOL")
parser.add_argument('--value',help="the value that will be passed to the slider, use with --setSlider")


args = parser.parse_args()

if args.getSliders is True:
    getSliderValues()

elif args.setSlider is not None and args.value is not None:
    getSliderValues()
    print("==================")
    setSliderValue(slider = (args.setSlider).upper(), value = (args.value).upper())
    print("==================")
    getSliderValues()

