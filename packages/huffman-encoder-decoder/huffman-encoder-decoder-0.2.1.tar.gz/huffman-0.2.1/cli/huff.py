import sys
from huffman import Huff, Unhuff

def usage():
    return """Usage: %s <operation> input_file output_file
    Possible operations:
        e   -> Encode
        d   -> Decode"""

def exit(msg):
    raise SystemExit(msg)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        exit(usage() % sys.argv[0])
    
    op_control = {'e': Huff,
                  'd': Unhuff}

    op, in_file, out_file = sys.argv[1:]

    if not op in op_control:
        exit(usage() % sys.argv[0])
    
    # Perform operation
    op_control[op](in_file, out_file)
