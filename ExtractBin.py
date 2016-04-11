import uuid

NV_START = 0x200000
NV_END = 0x220000
NV_SIG = "_FVH"
UINT8 = '\x00'
UINT16 = '\x00\x00'
UINT32 = '\x00\x00\x00\x00'
UINT64 = '\x00\x00\x00\x00\x00\x00\x00\x00'
EFI_GUID = UINT64*2
EFI_FVB_ATTRIBUTES_2 = UINT32
EFI_FV_BLOCK_MAP_ENTRY = UINT32 * 2


class Offset():
    def __init__(self, initVal=0):
        self.start = initVal

    def end(self, width):
        self.start += width
        return self.start 


def littlePrint(byte):
    return int.from_bytes(byte, byteorder='little')

class EFI_FFS_FILE_HEADER:
    def __init__(self, bn):
        global off
        off = 0 #offset
    

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
    
        
# open bin
with open(r'.\.data\0GTK.bin', 'rb') as f:
    byte = f.read()

# find NVRAM FV
nvram = byte[NV_START:NV_END]

# Valiate Signature
fv = EFI_FIRMWARE_VOLUME_HEADER(nvram)
assert fv.Signature.decode() == "_FVH"



