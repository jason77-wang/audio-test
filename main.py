#!/usr/bin/env python3

import os
import binascii
from intelnhlt import NhltTable

controller_has_dsp = False
dmic_nums = 0

def check_dsp_existing():
    global controller_has_dsp
    val = os.popen('lspci -nnvv')
    print ('Does the audio controller has dsp capability',end="")
    for temp in val.readlines():
        if (temp.find("audio") != -1 or temp.find("1f.3") != -1):
            if ((temp.find("0403") != -1 and temp.find("80") != -1) or
                (temp.find("0401") != -1)):
                controller_has_dsp = True
                print ("  YES")
    if (controller_has_dsp != True):
        print ("  NO")

    
def main():
    check_dsp_existing()

    nhlt = NhltTable()
    nhlt.reset()
    nhlt.load()
    dmic_nums = nhlt.DmicNumbers
    #check_num_of_dmics_in_NHLT()
    print ("The number of DMICS defined in the Intel NHLT table is ", dmic_nums)
    
    if (dmic_nums != 0 and controller_has_dsp != 0):
        print ("This is an Intel NHLT DMIC machine")
    else:
        print ("This is an Legacy HDA audio machine")


if __name__ == '__main__':
    main()

