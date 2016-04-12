"""
Lewis Chen
email: hjlewischen@gmail.com

"""

import uuid
import argparse
import re
import struct

##
## Macro
##
DSPDSETUP_TYPES = "./.data/DpsdSetup28.Types"


NV1_START = 0x200000
NV1_END = 0x220000
NV2_START = 0x220000
NV2_END = 0x240000
NV_SIG = "_FVH"
UINT8 = '\x00'
UINT16 = '\x00\x00'
UINT32 = '\x00\x00\x00\x00'
UINT64 = '\x00\x00\x00\x00\x00\x00\x00\x00'
EFI_GUID = UINT64*2
EFI_FVB_ATTRIBUTES_2 = UINT32
EFI_FV_BLOCK_MAP_ENTRY = UINT32 * 2
VAR_SIZE_TYPE = UINT16


##
##  Basic function
##
class Offset():
    def __init__(self, initVal=0):
        self.start = initVal

    def end(self, width):
        self.start += width
        return self.start 


def littlePrint(byte):
    return int.from_bytes(byte, byteorder='little')


##
##    Strcutreus
##
class EFI_FFS_FILE_HEADER:
    pass
    

## PiFirmwareVolume.h
class EFI_FIRMWARE_VOLUME_HEADER:
    def __init__(self, bn):
        o = Offset(0)
        self.ZeroVector = bn[o.start : o.end( len(UINT8) * 16)]
        self.FileSystemGuid = bn[o.start : o.end(len(EFI_GUID))]
        self.FvLength = bn[o.start : o.end(len(UINT64))]
        self.Signature = bn[o.start : o.end(len(UINT32))]
        self.Attributes = bn[o.start: o.end(len(EFI_FVB_ATTRIBUTES_2))]
        self.HeaderLength = bn[o.start : o.end(len(UINT16))]
        self.Checksum = bn[o.start : o.end(len(UINT16))]
        self.ExtHeaderOffset = bn[o.start : o.end(len(UINT16))]
        self.Reserved = bn[o.start : o.end(len(UINT8) * 1)]
        self.Reversion = bn[o.start : o.end(len(UINT8))]
        self.BlockMap = bn[o.start : o.end(len(EFI_FV_BLOCK_MAP_ENTRY) * 1)]
        self.body = bn[o.start:]
        self._length = o.start

## NVRAM.h
class NVAR: 
    def __init__(self, bn):
        o = Offset(0)
        self.Signature = bn[o.start : o.end(len(UINT32))]
        self.size = bn[o.start : o.end(len(VAR_SIZE_TYPE)) ]
        self.next = bn[o.start : o.end(3)]
        self.flags = bn[o.start : o.end(1)]
        self.body = bn[o.start:]

def SortHeader(filename):
    count = 0
    outbuf = []

    with open(filename) as f:
        for line in f.readlines():
            if "SETUP_DATA" in line:    # end of structure
                break

            m = re.match('\s*UINT(\d+)\s.*\[\s*(\d+)\s*\];', line)    #extract array variables
            if (m):
                artype = int(int(m.group(1)) / 8)
                arlen  = int(m.group(2))

                for p in range(artype * arlen):
                    outbuf.append(m.group(0))

                continue

            m = re.match('\s*UINT(\d+)\s.*;', line)   # extract variables
            if (m):
                artype = int(int(m.group(1)) / 8)
                for p in range(artype):
                    outbuf.append(m.group(0))
    return outbuf


def dumpFV(name, nvram):
    # Valiate Signature
    fv = EFI_FIRMWARE_VOLUME_HEADER(nvram)

    try:
        ## The seconde NVRAM may be 0xFF if GC is not active yet
        if fv.Signature.decode() == "_FVH":
            print("%s... created" % name)
    except UnicodeDecodeError:
        return

    # store binary 
    with open(r'./build/'+name, 'wb') as f:
        f.write(nvram)


def dumpNVAR(name, nvram, offset):
    # Valiate Signature
    nv_test = NVAR(nvram[offset:offset+10])
    assert nv_test.Signature.decode() == "NVAR"

    # Get Nvram size
    nv_size = struct.unpack("<h", nv_test.size)[0]

    # output 
    nv_out = nvram[offset : offset + nv_size]

    # store binary 
    with open(r'./build/'+name, 'wb') as f:
        f.write(nv_out)
        print("%s... created" % name)

    return NVAR(nv_out)
        
def SortHeader(filename):
    count = 0
    outbuf = []

    with open(filename) as f:
        for line in f.readlines():
            if "SETUP_DATA" in line:    # end of structure
                break

            m = re.match('\s*UINT(\d+)\s.*\[\s*(\d+)\s*\];', line)    #extract array variables
            if (m):
                artype = int(int(m.group(1)) / 8)
                arlen  = int(m.group(2))

                for p in range(artype * arlen):
                    outbuf.append(m.group(0))

                continue

            m = re.match('\s*UINT(\d+)\s.*;', line)   # extract variables
            if (m):
                artype = int(int(m.group(1)) / 8)
                for p in range(artype):
                    outbuf.append(m.group(0))

    # remove left space
    return [e.lstrip() for e in outbuf]


def str_to_hex(st):
    if st.startswith('0x') or st.startswith('0X'):
            st = st[2:]

    return int(st, 16)
            
    
def main(args):
    # open bin
    with open(args.infile, 'rb') as f:
        byte = f.read()

    # Extract binary
    dumpFV("NVRAM1.bin", byte[NV1_START:NV1_END])
    dumpFV("NVRAM2.bin", byte[NV2_START:NV2_END])

    setup = dumpNVAR("Setup.bin", byte, str_to_hex(args.sd))

    hf = SortHeader(DSPDSETUP_TYPES)
    assert (len(setup.body) ==  len(hf))

    sd_value = list(zip(hf, setup.body))

    outfile = args.infile.rsplit('/')[-1]
    with open(outfile+".sdmp", "w") as f:
        for k,v in sd_value:
            f.write("%s -> %s\n" % (k,v))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description='NVRAM Parser',
                    epilog='Lewis Chen (hjlewischen@gmail.com)')

    parser.add_argument('infile', default='./.data/0GTK.bin',
                       help='BIOS file name')

    parser.add_argument('--sd', default='0x23B34C', 
                    help='Setup NVAR address (Hex)')

    args = parser.parse_args()
    main(args)
    
