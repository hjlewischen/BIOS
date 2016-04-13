import argparse
from strlib import str_to_hex



"""
Use case:
    top/low - Target BIOS which is merge into 
    start/end - Source BIOS which is merge from

 _______ top
 |
 |______ end
 |
 |
 |______ start
 |______ low

"""

def main(args):
    start = str_to_hex(args.start)
    end = str_to_hex(args.end)
    assert start <= end, "start/end value error"
    
    with open(args.tarfile, 'rb') as f:
        TarBiosByte = f.read()

    with open(args.srcfile, 'rb') as f:
        SrcBiosByte = f.read()

    low = 0
    top = len(TarBiosByte)

    if start == low and end == top:
        raise Exception("illegal application, you may want to copy binary")

    elif start == low and end < top:  
        outbuf = SrcBiosByte[start:end] + TarBiosByte[end:]
    
    elif start > low and end < top:
        outbuf = TarBiosByte[low:start] + SrcBiosByte[start:end] + TarBiosByte[end:]

    elif start > low and end == top:
        outbuf = TarBiosByte[low:start] + SrcBiosByte[start:end]

    assert len(outbuf) == len(TarBiosByte), "Merged result is incorrect"
    
    outname = args.tarfile.split('/')[-1]
    with open(outname+"_merged.bin", 'wb') as f:
        f.write(outbuf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description='ROM Swap Utility - merge 2 ROM, Source BIOS to Target BIOS',
                    epilog='Lewis Chen (hjlewischen@gmail.com)')

    parser.add_argument('srcfile', help='Source BIOS wihch is merge from')

    parser.add_argument('tarfile', help='Target BIOS which is merge into')

    parser.add_argument('--start', required=True,
                    help='desired start address on source BIOS')

    parser.add_argument('--end', required=True,
                    help='desired end address on source BIOS')

    parser.add_argument('-v', '--verbose', action="store_true", 
                    help='Verbose message')
    
    args = parser.parse_args()
    main(args)
  
