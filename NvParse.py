"""
Lewis Chen
email: hjlewischen@gmail.com

"""

import uuid
import argparse
import re
import struct
import logging
import sys
import ipdb
from strlib import str_to_hex

##
## Macro
##
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
EFI_FV_FILETYPE = UINT8
EFI_FFS_FILE_ATTRIBUTES = UINT8
EFI_FFS_FILE_STATE = UINT8

##
##  Basic function
##
class Offset():
    def __init__(self, initVal=0):
        self.start = initVal

    def end(self, width):
        self.start += width
        return self.start 


def byte_to_int(byte):
    return int.from_bytes(byte, byteorder='little')

def byte_to_hex(byte):
    return hex(byte_to_int(byte))


##
##    Strcutreus
##

class CHECKSUM:  
    def __init__(self, bn):
        o = Offset(0)
        self.Header = bn[o.start : o.end(len(UINT8))]
        self.File = bn[o.start : o.end(len(UINT8))]

class EFI_FFS_INTEGRITY_CHECK:
    def __init__(self, bn, o):
        # Union structure, either Checksum or Checksum16
        self.Checksum16 = bn[o.start : o.end(len(UINT16))]
        self.Checksum = CHECKSUM(self.Checksum16)


## PiFirmwareFile.h
class EFI_FFS_FILE_HEADER:
    def __init__(self, bn, o):
        self.Name = bn[o.start : o.end(len(EFI_GUID))]
        self.IntegrityCheck = EFI_FFS_INTEGRITY_CHECK(bn, o)
        self.Type = bn[o.start : o.end(len(EFI_FV_FILETYPE))]
        self.Attributes = bn[o.start : o.end(len(EFI_FFS_FILE_STATE))]
        self.Size = bn[o.start: o.end(len(UINT8)*3)]
        self.State = byte_to_hex(bn[o.start : o.end(len(EFI_FFS_FILE_STATE))])


class EFI_FV_BLOCK_MAP_ENTRY:
    def __init__(self, bn, o):
        self.NumBlocks = byte_to_int(bn[o.start : o.end(len(UINT32))])
        self.Length = byte_to_int(bn[o.start : o.end(len(UINT32))])
        self.terminated = True if (self.NumBlocks == 0 and self.Length == 0) else False

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

        # An array of run-length encoded FvBlockMapEntry structures. The array is
        # terminated with an entry of {0,0}.
        self.BlockMap = []
        while True:
            bm = EFI_FV_BLOCK_MAP_ENTRY(bn, o)
            self.BlockMap.append(bm)
            if bm.terminated:
                break;

        self.ffs = EFI_FFS_FILE_HEADER(bn, o)
        self._length = o.start

## NVRAM.h
class NVAR: 
    def __init__(self, bn):
        o = Offset(0)
        self.Signature = bn[o.start : o.end(len(UINT32))]
        self.size = bn[o.start : o.end(len(VAR_SIZE_TYPE)) ]
        self.next = bn[o.start : o.end(3)]
        self.flags = bn[o.start : o.end(1)]
        self.HeaderSize = o.start
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


def ExtractFv(name, nvram):
    # Valiate Signature
    fv = EFI_FIRMWARE_VOLUME_HEADER(nvram)

    print ("State:%s" % fv.ffs.State)

    try:
        ## The seconde NVRAM may be 0xFF if GC is not active yet
        if fv.Signature.decode() == "_FVH":
            print("%s... created" % name)
    except UnicodeDecodeError:
        return

    # store binary 
    with open(r'./build/'+name, 'wb') as f:
        f.write(nvram)

    return fv


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


    
def main(args):

    logging.basicConfig(level=logging.DEBUG if args.verbose==True else logging.INFO)

    # open bin
    with open(args.infile, 'rb') as f:
        byte = f.read()

    # Extract binary
    print ("NVRAM: 0x%x" % NV1_START)
    fv = ExtractFv("NVRAM1.bin", byte[NV1_START:NV1_END])

    print ("NVRAM: 0x%x" % NV2_START)
    fv = ExtractFv("NVRAM2.bin", byte[NV2_START:NV2_END])
    ipdb.set_trace()

    setup = dumpNVAR("Setup.bin", byte, str_to_hex(args.sd))

    hf = SortHeader(args.tp)
    assert len(setup.body)== len(hf), "Setup size is not match"


    sd_value = list(zip(hf, setup.body))

    outfile = args.infile.rsplit('/')[-1]
    with open(outfile+".nvarmp", "w") as f:
        for k,v in sd_value:
            f.write("%s -> %s\n" % (k,v))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description='NVRAM Parser',
                    epilog='Lewis Chen (hjlewischen@gmail.com)')

    parser.add_argument('infile', default='./.data/0GTK.bin',
                   help='BIOS file name')

    parser.add_argument('--tp', default='./.data/DpsdSetup42.Types',
                   help='types definitions')

    parser.add_argument('--sd', default='0x23B34C', 
                    help='Setup NVAR address (Hex)')

    parser.add_argument('-v', '--verbose', action="store_true", 
                    help='Verbose message')
    
    args = parser.parse_args()
    main(args)
    
