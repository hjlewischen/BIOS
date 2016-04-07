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


class Offset(int):
    def __init__(cls, initValue=0):
        return int.__new__(cls, initValue)
        self.begin = initValue

    def off2(self, width):
        self.offset = self.offset + width
        return self.offset


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
        self.ZeroVector = bn[o: o2( len(UINT8) * 16)]
        self.FileSystemGuid = bn[ off : off2(len(EFI_GUID))]
        self.FvLength = bn[ off : off2(len(UINT64))]
        self.Signature = bn[ off : off2(len(UINT32))]
        self.Attributes = bn[ off : off2(len(EFI_FVB_ATTRIBUTES_2))]
        self.HeaderLength = bn[ off : off2(len(UINT16))]
        self.Checksum = bn[ off : off2(len(UINT16))]
        self.ExtHeaderOffset = bn[ off : off2(len(UINT16))]
        self.Reserved = bn[ off : off2(len(UINT8) * 1)]
        self.Reversion = bn[ off : off2(len(UINT8))]
        self.BlockMap = bn[ off : off2(len(EFI_FV_BLOCK_MAP_ENTRY) * 1)]
        self._length = off
    
        
# open bin
with open(r'.\.data\0GTK.bin', 'rb') as f:
    byte = f.read()

# find NVRAM FV
nvram = byte[NV_START:NV_END]

# Valiate Signature
fv = EFI_FIRMWARE_VOLUME_HEADER(nvram)
assert fv.Signature.decode() == "_FVH"



