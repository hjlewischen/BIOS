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


off = 0  # offset

def off2(width):
    global off

    off = off + width
    return off


## PiFirmwareVolume.h
class EFI_FIRMWARE_VOLUME_HEADER:
    def __init__(self, bn):
        global off
        off = 0  # offset
        self.ZeroVector = bn[ off: off2( len(UINT8) * 16)]
        self.FileSystemGuid = bn[ off : off2(len(EFI_GUID))]
        self.FvLength = bn[ off : off2(len(UINT64))]
        self.Signature = bn[ off : off2(len(UINT32))]
        self.Attributes = bn[ off : off2(len(EFI_FVB_ATTRIBUTES_2))]
        self.HeaderLength = bn[ off : off2(len(UINT16))]
        self.Checksum = bn[ off : off2(len(UINT16))]
        self.ExtHeaderOffset = bn[ off : off2(len(UINT16))]
        self.Reserved = bn[ off : off2( len(UINT8) * 1)]
        self.Reversion = bn[ off : off2( len(EFI_FV_BLOCK_MAP_ENTRY) * 1)]
        self._length = off
    
        
# open bin
with open(r'.\.data\0GTK.bin', 'rb') as f:
    byte = f.read()

# find NVRAM FV
nvram = byte[NV_START:NV_END]

# Valiate Signature
fv = EFI_FIRMWARE_VOLUME_HEADER(nvram)
assert fv.Signature.decode() == "_FVH"



