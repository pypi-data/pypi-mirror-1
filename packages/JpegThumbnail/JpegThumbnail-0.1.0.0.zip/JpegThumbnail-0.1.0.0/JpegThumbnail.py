"""simple and fast JPEG thumbnail reader

Requirements
------------

* Python Imaging Library


Features
--------

* supports EXIF thumbnail

* supports Adobe Photoshop thumbnail

* import a partial JPEG data


An example
----------
::

    from cStringIO import StringIO
    import Image
    import JpegThumbnail

    try:
        thumbnail = JpegThumbnail.read(filelikeobject or filename)
    except JpegThumbnail.error:
        "parse error"
    except IOError:
        "open or read error"
    else:
        im = Image.open(StringIO(thumbnail))
        im.show()


Notes
-----

* In most case, JPEG thumbnail size is about 100 pixel.

* In most case, thumbnail is found in early 10KiB of file data.
  In bad case, it's found in ealry 100KiB.


History
-------

0.1.0.0
~~~~~~~

* first release


"""
# see JPEG format information:
# http://hp.vector.co.jp/authors/VA032610/JPEGFormat
import sys
import os
import struct
from cStringIO import StringIO
# Python Imaging Library
from JpegImagePlugin import MARKER

error = struct.error


def openfile(file):
    if isinstance(file, str):
        file = file.decode(sys.getfilesystemencoding())

    if isinstance(file, basestring):
        file = __builtins__.open(file, 'rb')

    assert(hasattr(file, 'read') and \
           hasattr(file, 'seek') and \
           hasattr(file, 'tell'))

    return file


class JpegParser(object):
    """JPEG parser base"""

    def __init__(self, file):
        self.file = openfile(file)
        self._stopped = False

    def stop(self):
        self._stopped = True

    def parse(self):
        self._stopped = False

        s = self.file.read(1)
        if s != '\xff':
            raise error('not a JPEG file')

        while not self._stopped:
            s = s + self.file.read(1)
            marker = struct.unpack('>H', s)[0]

            if marker in MARKER:
                name, descr, handle = MARKER[marker]
                if handle: # segment with data
                    size = struct.unpack('>H', self.file.read(2))[0] - 2
                    handler = getattr(self, 'handle' + name, None)
                    if handler:
                        data = self.file.read(size)
                        handler(data)
                    else:
                        self.file.seek(size, os.SEEK_CUR) #skip
                s = self.file.read(1)

            elif marker in (0x0000, 0xffff, ):
                s = '\xff'
            else:
                raise error('no marker found')


class ExifReader(object):

    magic = 'Exif\0\0'
    typeinfo = {
        0x0001: 'B',
        0x0002: 's',
        0x0003: 'H',
        0x0004: 'L',
        0x0005: 'Q',
        0x0006: 'B',
        0x0007: 'B',
        0x0008: 'H',
        0x0009: 'L',
        0x000A: 'Q',
        0x000B: 'L',
        0x000C: 'Q',
        }
    fp = None
    index = -1
    processed = []
    endian = ''

    def __init__(self, data):
        # check and skip the magic header
        if not data.startswith(self.magic):
            raise error('not an EXIF')
        data = data[len(self.magic):]

        self.fp = StringIO(data)

        endian = self.fp.read(2)
        if endian == 'MM':
            self.endian = '>' #big
        elif endian == 'II':
            self.endian = '<' #little
        else:
            raise error('unknown endian')

        magic = struct.unpack(self.endian + 'H', self.fp.read(2))[0]
        if magic not in (0x002A, 0x2A00, ):
            raise error('not tiff')

    def __iter__(self):
        self.index = -1
        while 1:
            pos = struct.unpack(self.endian + 'L', self.fp.read(4))[0]
            if pos == 0 or pos in self.processed:
                break
            self.processed.append(pos)
            self.fp.seek(pos)
            self.index += 1

            ntags = struct.unpack(self.endian + 'H', self.fp.read(2))[0]
            tags = self.fp.read(ntags * 12)
            for i in range(ntags):
                #self.tag = self.fp.read(12)
                self.tag = tags[i * 12:(i + 1) * 12]
                yield struct.unpack(self.endian + 'H', self.tag[:2])[0]

    def _convvalue(self, type, count, value):
        length = struct.calcsize(self.typeinfo[type]) * count
        value = struct.unpack(self.endian + str(count) + self.typeinfo[type],
                              value[:length])[0]
        return value

    @property
    def curvalue(self):
        tag, type, count, value = struct.unpack(self.endian + 'HHL4s',
                                                self.tag)
        length = struct.calcsize(self.typeinfo[type]) * count

        # value in offset
        if length <= 4:
            pass

        # value in other area
        else:
            address = struct.unpack(self.endian + 'L', value)[0]
            oldpos = self.fp.tell()
            try:
                self.fp.seek(address)
                value = self.fp.read(length)
            finally:
                self.fp.seek(oldpos)

        value = self._convvalue(type, count, value)
        return type, value


class PhotoshopResourceReader(object):

    magic = 'Photoshop 3.0\0'

    def __init__(self, data):
        # check and skip the magic header
        if not data.startswith(self.magic):
            raise error('not an Adobe Photoshop metadata')
        data = data[len(self.magic):]

        self.fp = StringIO(data)

    def __iter__(self):
        while 1:
            signature = self.fp.read(4)
            if not signature: break
            if signature != '8BIM':
                raise error('abnormal data found')

            id = struct.unpack('>H', self.fp.read(2))[0]
            name = self.fp.read(ord(self.fp.read(1)) or 1) # Pascal String
            size = struct.unpack('>L', self.fp.read(4))[0]

            data = self.fp.read(size)
            if size & 1: self.fp.read(1) # align even byte

            yield id, name, data


class JpegThumbnailReader(JpegParser):
    """read embedded JPEG thumbnail"""

    thumbnail = ''

    def handleAPP1(self, data):
        """process EXIF metadata"""
        try:
            metadata = ExifReader(data)
        except Exception:
            return

        pos, size = 0, 0
        for tag in metadata:
            if metadata.index != 1: continue
            if tag == 0x0201:
                pos = metadata.curvalue[1]
            if tag == 0x0202:
                size = metadata.curvalue[1]
            if pos and size:
                metadata.fp.seek(pos)
                self.thumbnail = metadata.fp.read(size)
                self.stop()
                return

    def handleAPP13(self, data):
        """process Photoshop metadata"""
        try:
            metadata = PhotoshopResourceReader(data)
        except Exception:
            return

        for irb in metadata:
            if irb[0] == 0x040C:
                #format, width, height, widthbytes, size, \
                #compressionsize, bitspixel, planes = struct.unpack(
                #    '>LLLLLLHH', irb[2][:28])
                self.thumbnail = irb[2][28:]
                self.stop()
                return


def read(file):
    reader = JpegThumbnailReader(file)
    reader.parse()
    return reader.thumbnail


if __name__ == '__main__':
    sys.modules['JpegThumbnail'] = sys.modules[__name__]
    from distutils.core import setup
    setup(
        name='JpegThumbnail',
        version='0.1.0.0',
        license='PSF',
        description=__doc__.splitlines()[0],
        long_description=__doc__,
        author='chrono-meter@gmx.net',
        author_email='chrono-meter@gmx.net',
        url='http://pypi.python.org/pypi/JpegThumbnail',
        platforms='independent',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Graphics',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        py_modules=['JpegThumbnail', ],
        )


