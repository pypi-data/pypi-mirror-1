import sys

from huffman import Huff, Unhuff

def usage():
    return """Usage: %s <operation> input_file output_file
    Possible operations:
        e   ->  Encode
        d   ->  Decode"""

def main(args):
    op_control = {
            'e': Huff,
            'd': Unhuff
            }

    op, in_file, out_file = args[1:]

    if not op in op_control:
        print>>sys.stderr, "Invalid operation %r" % op
        print>>sys.stderr, usage() % args[0]
        return 1

    # Perform operation
    op_control[op](in_file, out_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(usage() % sys.argv[0])

    main(sys.argv)
