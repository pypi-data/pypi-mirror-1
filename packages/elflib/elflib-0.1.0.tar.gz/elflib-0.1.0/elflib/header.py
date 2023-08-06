import platform
from array import array
from struct import pack, unpack, calcsize


# see /usr/include/elf.h for more details

EI_NIDENT = 16

VARS = [
  ('Half', 'e_type'),         # Object file type
  ('Half', 'e_machine'),      # Architecture
  ('Word', 'e_version'),      # Object file version
  ('Addr', 'e_entry'),        # Entry point virtual address
  ('Off',  'e_phoff'),        # Program header table file offset
  ('Off',  'e_shoff'),        # Section header table file offset
  ('Word', 'e_flags'),        # Processor-specific flags
  ('Half', 'e_ehsize'),       # ELF header size in bytes
  ('Half', 'e_phentsize'),    # Program header table entry size
  ('Half', 'e_phnum'),        # Program header table entry count
  ('Half', 'e_shentsize'),    # Section header table entry size
  ('Half', 'e_shnum'),        # Section header table entry count
  ('Half', 'e_shstrndx')      # Section header string table index
]

class Header(object):

    def __init__(self, addrbits=None):
        if addrbits is None:
            addrbits = int(platform.architecture()[0].rstrip('bits'))

        if addrbits == 32:
            ptr = 'L'
        elif addrbits == 64:
            ptr = 'Q'
        else:
            raise NotImplementedError
        typmap = {'Half': 'H', 'Word': 'L', 'Addr': ptr, 'Off': ptr}

        self.fmt = ''.join(typmap[typ] for typ, name in VARS)
        self.size = EI_NIDENT + calcsize(self.fmt)

    def read(self, fi):
        self.data = fi.read(self.size)
        self.set_attrs()

    def set_attrs(self):
        self.e_ident = array('c', self.data[:EI_NIDENT])
        tmp = unpack(self.fmt, self.data[EI_NIDENT:])
        for i, (typ, name) in enumerate(VARS):
            setattr(self, name, tmp[i])

    def write(self, fo):
        self.set_data()
        fo.write(self.data)

    def set_data(self):
        self.data = self.e_ident.tostring()
        args = [self.fmt] + [getattr(self, name) for typ, name in VARS]
        self.data += pack(*args)

    def display(self):
        print 'ELF Header (size=%i):' % self.size
        print '    %s' % self.e_ident
        for typ, name in VARS:
            val = getattr(self, name)
            if typ == 'Addr':
                val = hex(val)
            print '    %-11s = %12s (%s)' % (name, val, typ)


if __name__ == '__main__':
    import sys

    eh = Header()

    fi = open(sys.argv[1], 'rb')
    eh.read(fi)
    fi.close()

    eh.display()

    fo = open('out', 'wb')
    eh.write(fo)
    fo.close()
