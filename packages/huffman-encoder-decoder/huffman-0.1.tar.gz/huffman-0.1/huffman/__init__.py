# Copyright (C) Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
# USA
 
"""
A module for performing huffman encoding and decoding.
"""

import struct
import operator
from array import array
from collections import defaultdict

from huffman.heapq_ext import Heap

try:
    import psyco
    psyco.full()
except ImportError:
    from warnings import warn
    warn("Psyco not found, your decompression time will suffer with this.")

__version__ = "0.1"
__author__ = "Guilherme Polo <ggpolo@gmail.com>"

def char_freq(file_obj, frequency_table):
    """Build a frequency table from chars read from input file."""
    content = [ ]
    freq = defaultdict(int)
    for line in file_obj:
        content.append(line)
        for ch in line:
            freq[ch] += 1

    # Create a leaf node for each item in freq
    for ch, weight in freq.items():
        frequency_table[ch] = weight

    return content


def read_header(f_in, frequency_table):
    """Reads a huffman header."""
    header = f_in.read(1024) # 256 symbols, 4 bytes each

    # unpack the same way it was packed, and build a frequency table
    unpacked_header = struct.unpack('256I', header)
    for ch_indx, weight in enumerate(unpacked_header):
        # several symbols with 0 weight were possibly stored, but we do
        # not need them
        if weight:
            frequency_table[chr(ch_indx)] = weight


def write_header(f_out_obj, frequency_table):
    """Write to file output a huffman header."""
    header = (struct.pack('I', frequency_table[chr(i)].weight) \
                for i in xrange(256))
    f_out_obj.write(''.join(header))


def codify_to_huffman(f_in_content, f_out_obj, codes):
    """input_content is that list that was returned at charfreq,
    f_out is the file output and codes are the generated codes for 
    input data."""
    bstr = ''.join([codes[ch] for line in f_in_content for ch in line])
    bstr_len_by8, remaining = divmod(len(bstr), 8)

    bstrs = [bstr[i << 3:(i + 1) << 3] for i in xrange(bstr_len_by8)]

    obstrs = [int(obstr, 2) for obstr in bstrs]

    if remaining:
        # we need to complete last byte, so make sure it is a good 8-bit 
        # string
        obstrs.append(int(bstr[-remaining:].ljust(8, '0'), 2))

    # write the code that identifies end of huffman encoding
    # this is actually the last byte in the file.
    obstrs.append((8 - remaining) % 8) # last byte code
    f_out_obj.write(struct.pack('%dB' % len(obstrs), *obstrs))


def dec2bin(dec_list):
    return array('c', ['1' if ((1 << i) & dec) else '0' for dec in dec_list \
                                for i in xrange(7, -1, -1)])

def read_encoded(file_obj):
    """Reads a file compressed by huffman algorithm."""
    content = [ch for line in file_obj for ch in line]

    bstrs = dec2bin(struct.unpack('%dB' % len(content), ''.join(content)))

    end_code = int(bstrs[-8:].tostring(), 2)
    
    del bstrs[- 8 - end_code:] # remove end code and extra bytes from string
    return bstrs.tostring()


def decode_huffman(f_out_obj, root, binstr):
    """Expects a file object and a binstr that is returned from 
    read_encoded."""
    start = root
    for b in binstr:
        root = root.left if b == '0' else root.right

        if root.left is None and root.right is None:
            # found a leaf node, you found a symbol then
            f_out_obj.write(root.data)
            root = start


class HuffNode(object):
    """Representation of a node in a 'Huffman tree'."""

    def __init__(self, weight, data, left=None, right=None):
        self.weight = weight
        self.data = data
        self.left = left
        self.right = right

    def __cmp__(self, other_node):
        """Compare nodes by their weight."""
        return cmp(self.weight, other_node)


class HuffStructure(dict):
    """Data structure used in this Huffman implementation."""
    def __init__(self):
        self.codes = { } # symbols codes
        self.tree_built = False

        # cache for ordered items
        self.cached = False
        self._cached = None

    def __setitem__(self, key, value):
        """When doing huffstruct[key] = val, a new HuffNode is created,
        if val is not a HuffNode, where val is its weight and key its data. 
        If val is a HuffNode, set a new node to the key."""
        if not isinstance(value, HuffNode):
            value = HuffNode(value, key)

        dict.__setitem__(self, key, value)
        # since the dict was updated, the cache is not valid anymore.
        self.cached = False

    def __getitem__(self, key):
        """Return a new HuffNode with 0 weight and key as its data, in 
        case of trying to access an inexistant key."""
        if dict.__contains__(self, key):
            value = dict.__getitem__(self, key)
        else:
            value = HuffNode(0, key)
            # new node created, cache is invalid
            self.cached = False

        return value

    def __delitem__(self, key):
        """Upon item deletion we need to invalidate cache."""
        dict.__delitem__(self, key)
        self.cached = False

    def ordered_items(self):
        """Return items ordered by weight, so it is easier and faster
        to build the tree later."""
        return self._cached_order()

    def build_tree(self):
        """Build tree from ordered items."""
        items = self.ordered_items()

        while True:
            if len(items) == 1:
                # tree has been built
                break

            # get the two first nodes, the ones with lowest weight
            node_left = items.pop()
            node_right = items.pop()
            
            weight_sum = node_left[1].weight + node_right[1].weight 
            repr_str = node_left[0] + node_right[0]

            # construct a binary tree
            father = HuffNode(weight_sum, repr_str)
            father.left = node_left[1]
            father.right = node_right[1]

            # add father to the dict
            items.push((repr_str, father))

        self.tree_built = True
        return items.pop()[1] # root

    def generate_codes(self, root, code=''):
        """Generate codes from built tree by travessing it."""
        if not self.tree_built:
            self.build_tree()

        if root.left is None and root.right is None:
            # a leaf node here, the code for this symbol should be complete
            self.codes[root.data] = code
        else:
            self.generate_codes(root.left, code + '0')
            self.generate_codes(root.right, code + '1')

    def _cached_order(self):
        """Return cached items ordered or order them now and cache."""
        if self.cached:
            treeheap = self._cached
        else:
            items = dict(self).items()

            treeheap = Heap(items, operator.itemgetter(1), True)
            self._cached = treeheap
            self.cached = True

        return treeheap


class HuffBase(object):
    """Base class for encoding and decoding Huffman files."""

    def __init__(self, file_in, file_out, encoding=True):
        if encoding:
            in_mode = 'r'
            out_mode = 'wb'
        else:
            in_mode = 'rb'
            out_mode = 'w'

        self.file_in = open(file_in, in_mode)
        self.file_out = open(file_out, out_mode)

        self.root = None
        self.freq_table = HuffStructure()

    def gen_codes(self):
        """Build tree and generate codes for current nodes on it."""
        self.root = self.freq_table.build_tree()
        self.freq_table.generate_codes(self.root)

    def cleanup(self):
        self.file_in.close()
        self.file_out.close()


class Huff(HuffBase):
    def __init__(self, file_in, file_out):
        HuffBase.__init__(self, file_in, file_out)

        self.content = char_freq(self.file_in, self.freq_table)
        write_header(self.file_out, self.freq_table)
        self.gen_codes()

        self.file_in.seek(0)
        self.encode_input()
        self.cleanup()

    def encode_input(self):
        codify_to_huffman(self.content, self.file_out, self.freq_table.codes)


class Unhuff(HuffBase):
    def __init__(self, file_in, file_out):
        HuffBase.__init__(self, file_in, file_out, False)
        
        read_header(self.file_in, self.freq_table)
        self.gen_codes()
        self.decode_input()
        self.cleanup()

    def decode_input(self):
        binstr = read_encoded(self.file_in)
        decode_huffman(self.file_out, self.root, binstr)
