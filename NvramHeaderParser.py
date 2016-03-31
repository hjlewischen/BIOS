import argparse
import re


def main(args):
    count = 0
    outbuf = []

    with open(args.infile) as f:
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

        print ('\n'.join(outbuf))
        print ("Variables: %d (0x%X)" % (len(outbuf), len(outbuf)))

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    description='NVRAM Header Processor',
                    epilog='Lewis Chen (hjlewischen@gmail.com)')

    parser.add_argument('infile', metavar='INPUT', type=str, nargs='*', default="DpsdSetup.Types",
                    help='NVRAM header file *,types')

    parser.add_argument('outfile', metavar='OUTPUT', type=str, nargs='*', default="DpsdSetup.out",
                    help='NVRAM header file *,types')

    args = parser.parse_args()
    main(args)
    
