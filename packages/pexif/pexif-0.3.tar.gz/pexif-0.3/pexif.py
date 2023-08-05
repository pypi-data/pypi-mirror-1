"""
pexif is a module which allows you to view and modify meta-data in
JPEG/JFIF/EXIF files.

The main way to use this is to create an instance of the JpegFile class.
This should be done using one of the static methods fromFile, fromString
or fromFd.

After manipulating the object you can then write it out using one of the
writeFile,writeString or writeFd methods.

The get_exif() method on JpegFile returns the ExifSegment if one exists.

Example:

j = pexif.JpegFile.fromFile("foo.jpg")
xf = j.get_exif()
....
j.writeFile("new.jpg")

"""

import StringIO
import sys
from struct import unpack, pack

try:
    import decimal
except:
    decimal = None

MAX_HEADER_SIZE = 64 * 1024
DELIM = 255
EOI = 0xd9
SOI_MARKER = chr(DELIM) + '\xd8'
EOI_MARKER = chr(DELIM) + '\xd9'

EXIF_OFFSET = 0x8769

TIFF_OFFSET = 6
TIFF_TAG = 0x2a

DEBUG = 0

def debug(*str):
    if DEBUG:
        for each in str:
            print each,
        print


class DefaultSegment:
    """DefaultSegment represents a particluar segment of a JPEG file.
    This class is instantiated by JpegFile when parsing Jpeg files
    and is not intented to be used directly by the programmer. This
    base class is used as a default which doesn't know about the internal
    structure of the segment. Other classes subclass this to provide
    extra information about a particular segment.
    """
    
    def __init__(self, marker, fd, data):
        """The constructor for DefaultSegment takes the marker which
        identifies the segments, a file object which is currently positioned
        as the end of the segment. This allows any subclasses to potentially
        extract extra data from the stream. Data contains the contents of the
        segment."""
        self.marker = marker
        self.parse_data(data)

    def write(self, fd):
        """This method is called by JpegFile when writing out the file. It
        must write out any data in the segment. This shouldn't in general be
        overloaded by subclasses, they should instead override the get_data() method."""
        fd.write('\xff')
        fd.write(pack('B', self.marker))
        data = self.get_data()
        fd.write(pack('>H', len(data) + 2))
        fd.write(data)

    def get_data(self):
        """This method is called by write to generate the data for this segment. It should
        be overloaded by subclasses."""
        return self.data

    def parse_data(self, data):
        """This method is called be init to parse any data for the segment. It should
        be overloaded by subclasses rather than overloading __init__"""
        self.data = data

    def dump(self, fd):
        """This is called by JpegFile.dump() to output a human readable representation of
        the segment. Subclasses should overload this to provide extra information."""
        print >> fd, " Section: [%5s] Size: %6d" % (jpeg_markers[self.marker][0], len(self.data))

class StartOfScanSegment(DefaultSegment):
    """The StartOfScan segment needs to be treated specially as the actual
    image data directly follows this segment, and that data is not included
    in the size as reported in the segment header. This instances of this class
    are created by JpegFile and it should not be subclassed.
    """
    def __init__(self, marker, fd, data):
        DefaultSegment.__init__(self, marker, fd, data)

        # For SOS we also pull out the actual data
        img_data = fd.read()
        self.img_data = img_data[:-2]
        fd.seek(-2, 1)

    def write(self, fd):
        DefaultSegment.write(self, fd)
        fd.write(self.img_data)

    def dump(self, fd):
        print >> fd, " Scan Section:    Size: %6d Image data size: %6d" % (len(self.data), len(self.img_data))

def make_syms(dict):
    """A slightly evil function for generating constant symbols without needless
    duplication. For example given a dictionary: { 1 : ("foo", ...), 2 : ("bar", ...) }
    This function will create two new globals FOO and BAR with values 1 and 2 respectively.
    This avoids a common pattern that was occurring of:
    FOO = 1
    BAR = 2
    names = { FOO : ("foo", ..), BAR : ("bar",...) }

    With two values the gain is not so obvious, but considering a set of 100.
    
    This function takes a dict whose values must be tuples with the first argument
    containing a string. The string value is converted to uppercase and inserted
    into the module global scope.
    """
    
    for key, value in dict.items():
        globals()[value[0].upper()] = key


def make_syms2(dict):
    for key, value in dict.items():
        globals()[value[1]] = key

exif_types = {
    1: ("byte", 1),
    2: ("ascii", 1), 
    3: ("short", 2),
    4: ("long", 4),
    5: ("rational", 8),
    7: ("undefined", 1),
    9: ("slong", 4),
    10: ("srational", 8)
    }
make_syms(exif_types)

def exif_type_size(type):
    """Return the size of a type"""
    return exif_types.get(type)[1]

class Rational:
    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __repr__(self):
        return "%s / %s" % (self.num, self.den)

    def as_tuple(self):
        return (self.num, self.den)

class IfdData:
    """Base class for IFD"""
    
    name = "Generic Ifd"
    tags = {}
    embedded_tags = {}

    def special_handler(self, tag, data):
        pass

    def ifd_handler(self, data):
        pass

    def extra_ifd_data(self, offset):
        return ""


    def has_key(self, key):
        return self[key] != None

    def __getitem__(self, key):
        for entry in self.entries:
            if key == entry[0]:
                return entry[2]
        return None

    def __setitem__(self, key, value):
        found = 0
        for i in range(len(self.entries)):
            if key == self.entries[i][0]:
                found = 1
                entry = list(self.entries[i])
                if value is None:
                    del self.entries[i]
                else:
                    entry[2] = value
                    self.entries[i] = tuple(entry)
                break
        if not found:
            # Find type...
            # Not quite enough yet...
            self.entries.append((key, self.tags[key][2], value))
        return

    def __init__(self, e, offset, exif_file, data = None):
        self.exif_file = exif_file
        self.e = e
        self.entries = []
        if data is None:
            return

        num_entries = unpack(e + 'H', data[offset:offset+2])[0]
        next = unpack(e + "I", data[offset+2+12*num_entries:offset+2+12*num_entries+4])[0]
        debug("OFFSET %s - %s" % (offset, next))
        
        for i in range(num_entries):
            start = (i * 12) + 2 + offset
            debug("START: ", start)
            entry = unpack(e + "HHII", data[start:start+12])
            tag, type, components, the_data = entry

            debug("%s %s %s %s %s" % (hex(tag), type,
                                      exif_type_size(type), components,
                                      the_data))
            byte_size = exif_type_size(type) * components


            if tag in self.embedded_tags:
                actual_data = self.embedded_tags[tag](e, the_data, exif_file, data)
            else:
                if byte_size > 4:
                    debug(" ...offset %s" % the_data)
                    the_data = data[the_data:the_data+byte_size]
                else:
                    the_data = data[start+8:start+8+byte_size]

                if type == 1 or type == 7:  # byte, undef
                    actual_data = list(the_data)
                elif type == 2: # ascii
                    actual_data = the_data.strip('\0')
                elif type == 3: # short
                    actual_data = list(unpack(e + ("H" * components), the_data))
                elif type == 4: # long
                    actual_data = list(unpack(e + ("I" * components), the_data))
                elif type == 9: # slong
                    actual_data = list(unpack(e + ("i" * components), the_data))
                elif type == 5 or type == 10: # rational/srational
                    if type == 5: t = "II"
                    else: t = "ii"
                    actual_data = []
                    for i in range(components):
                        #print "Length of data", len(data)
                        actual_data.append(Rational(*unpack(e + t, the_data[i*8:i*8+8])))
                else:
                    raise "Pants, can't handle this"

                if (byte_size > 4):
                    debug("%s" % actual_data)

                self.special_handler(tag, actual_data)
            entry = (tag, type, actual_data)
            self.entries.append(entry)

            debug("%-40s %-10s %6d %s" % (self.tags.get(tag, (hex(tag), 0))[0],
                                          exif_types[type],
                                          components, actual_data))
        self.ifd_handler(data)

    def isifd(self, other):
        """Return true if other is an IFD"""
        return issubclass(other.__class__, IfdData)

    def getdata(self, e, offset, last = 0):
        data_offset = offset+2+len(self.entries)*12+4
        output_data = ""

        out_entries = []

        # Add any specifc data for the particular type
        extra_data = self.extra_ifd_data(data_offset)
        data_offset += len(extra_data)
        output_data += extra_data

        for tag, type, the_data in self.entries:
            magic_type = type
            if (self.isifd(the_data)):
                debug("-> Magic..");
                sub_data, next_offset = the_data.getdata(e, data_offset, 1)
                the_data = [data_offset]
                debug("<- Magic", next_offset, data_offset, len(sub_data), data_offset + len(sub_data))
                data_offset += len(sub_data)
                assert(next_offset == data_offset)
                output_data += sub_data
                magic_type = type
                if type != 4:
                    magic_components = len(sub_data)
                else:
                    magic_components = 1
                type = 4 # LONG
                byte_size = 4
            else:
                magic_components = components = len(the_data)
                byte_size = exif_type_size(type) * components

            if type == BYTE or type == UNDEFINED:
                actual_data = "".join(the_data)
            elif type == ASCII:
                actual_data = the_data + '\0'
                byte_size += 1
            elif type == SHORT:
                actual_data = pack(e + ("H" * components), *the_data)
            elif type == LONG:
                actual_data = pack(e + ("I" * components), *the_data)
            elif type == SLONG:
                actual_data = pack(e + ("i" * components), *the_data)
            elif type == RATIONAL or type == SRATIONAL:
                if type == RATIONAL: t = "II"
                else: t = "ii"
                actual_data = ""
                for i in range(components):
                    actual_data += pack(e + t, *the_data[i].as_tuple())
            else:
                raise "Pants, can't handle this", type
            if (byte_size) > 4:
                output_data += actual_data
                debug(".. offset", data_offset)
                actual_data = pack(e + "I", data_offset) 
                data_offset += byte_size
            else:
                actual_data = actual_data + '\0' * (4 - len(actual_data))
            out_entries.append((tag, magic_type,
                                magic_components, actual_data))

        data = pack(e + 'H', len(self.entries))
        for entry in out_entries:
            data += pack(self.e + "HHI", *entry[:3])
            data += entry[3]

        next_offset = data_offset
        if last:
            data += pack(self.e + "I", 0)
        else:
            data += pack(self.e + "I", next_offset)
        data += output_data

        debug("Returning...", next_offset, offset+len(data))
        assert (next_offset == offset+len(data))
        debug("   OK!")

        return data, next_offset

    def dump(self, f, indent = ""):
        """Dump the IFD file"""
        print >> f, indent + "<--- %s start --->" % self.name
        for entry in self.entries:
            tag, type, data = entry
            if (self.isifd(data)):
                data.dump(f, indent + "    ")
            else:
                if len(data) == 1:
                    data = data[0]
                print >> f, indent + "  %-40s %s" % \
                      (self.tags.get(tag, (hex(tag), 0))[0], data)
        print >> f, indent + "<--- %s end --->" % self.name

class IfdInterop(IfdData):
    name = "Interop"
    tags = {
        # Interop stuff
        0x0001: ("Interoperability index", "InteroperabilityIndex"),
        0x0002: ("Interoperability version", "InteroperabilityVersion"),
        0x1000: ("Related image file format", "RelatedImageFileFormat"),
        0x1001: ("Related image file width", "RelatedImageFileWidth"),
        0x1002: ("Related image file length", "RelatedImageFileLength"),            
        }

class CanonIFD(IfdData):
    tags = {
        0x0006: ("Image Type", "ImageType"),
        0x0007: ("Firmware Revision", "FirmwareRevision"),
        0x0008: ("Image Number", "ImageNumber"),
        0x0009: ("Owner Name", "OwnerName"),
        0x000c: ("Camera serial number", "SerialNumber"),
        0x000f: ("Customer functions", "CustomerFunctions")
        }
    name = "Canon"

def IfdMakerNote(e, offset, exif_file, data):
    """Factory function for creating MakeNote entries"""
    if exif_file.make == "Canon":
        return CanonIFD(e, offset, exif_file, data)
    else:
        raise ExifFile.InvalidFile("Unknown maker: %s. Can't currently handle this." % exif_file.make)

class IfdGPS(IfdData):
    name = "GPS"
    tags = {
        0x0: ("GPS tag version", "GPSVersionID", BYTE, 4),
        0x1: ("North or South Latitude", "GPSLatitudeRef", ASCII, 2),
        0x2: ("Latitude", "GPSLatitude", RATIONAL, 3),
        0x3: ("East of West Longitude", "GPSLongitudeRef", ASCII, 2),
        0x4: ("Longitude", "GPSLongitude", RATIONAL, 3),
        0x5: ("Altitude reference", "GPSAltitudeRef", BYTE, 1),
        0x6: ("Altitude", "GPSAltitude", RATIONAL, 1)
        }

make_syms2(IfdGPS.tags)

class IfdExtendedEXIF(IfdData):
    tags = {
        # Exif IFD Attributes
        # A. Tags relating to version
        0x9000: ("Exif Version", "ExifVersion"),
        0xA000: ("Supported Flashpix version", "FlashpixVersion"),
        # B. Tag relating to Image Data Characteristics
        0xA001: ("Color Space Information", "ColorSpace"),
        # C. Tags relating to Image Configuration
        0x9101: ("Meaning of each component", "ComponentConfiguration"),
        0x9102: ("Image compression mode", "CompressedBitsPerPixel"),
        0xA002: ("Valid image width", "PixelXDimension"),
        0xA003: ("Valid image height", "PixelYDimension"),
        # D. Tags relatin to User informatio
        0x927c: ("Manufacturer notes", "MakerNote"),
        0x9286: ("User comments", "UserComment"),
        # E. Tag relating to related file information
        0xA004: ("Related audio file", "RelatedSoundFile"),
        # F. Tags relating to date and time
        0x9003: ("Date of original data generation", "DateTimeOriginal"),
        0x9004: ("Date of digital data generation", "DateTimeDigitized"),
        0x9290: ("DateTime subseconds", "SubSecTime"),
        0x9291: ("DateTime original subseconds", "SubSecTimeOriginal"),
        0x9292: ("DateTime digitized subseconds", "SubSecTimeDigitized"),
        # G. Tags relating to Picture taking conditions
        0x829a: ("Exposure Time", "ExposureTime"),
        0x829d: ("F Number", "FNumber"),
        0x8822: ("Exposure Program", "ExposureProgram"),    
        0x8824: ("Spectral Sensitivity", "SpectralSensitivity"),
        0x8827: ("ISO Speed Rating", "ISOSpeedRatings"),
        0x8829: ("Optoelectric conversion factor", "OECF"),
        0x9201: ("Shutter speed", "ShutterSpeedValue"),
        0x9202: ("Aperture", "ApertureValue"),
        0x9203: ("Brightness", "BrightnessValue"),
        0x9204: ("Exposure bias", "ExposureBiasValue"),
        0x9205: ("Maximum lens apeture", "MaxApertureValue"),
        0x9206: ("Subject Distance", "SubjectDistance"),
        0x9207: ("Metering mode", "MeteringMode"),
        0x9208: ("Light mode", "LightSource"),
        0x9209: ("Flash", "Flash"),
        0x920a: ("Lens focal length", "FocalLength"),
        0x9214: ("Subject area", "Subject area"),
        0xa20b: ("Flash energy", "FlashEnergy"),
        0xa20c: ("Spatial frequency results", "SpatialFrquencyResponse"),
        0xa20e: ("Focal plane X resolution", "FocalPlaneXResolution"),
        0xa20f: ("Focal plane Y resolution", "FocalPlaneYResolution"),
        0xa210: ("Focal plane resolution unit", "FocalPlaneResolutionUnit"),
        0xa214: ("Subject location", "SubjectLocation"),
        0xa215: ("Exposure index", "ExposureIndex"),
        0xa217: ("Sensing method", "SensingMethod"),
        0xa300: ("File source", "FileSource"),
        0xa301: ("Scene type", "SceneType"),
        0xa302: ("CFA pattern", "CFAPattern"),
        0xa401: ("Customer image processing", "CustomerRendered"),
        0xa402: ("Exposure mode", "ExposureMode"),
        0xa403: ("White balance", "WhiteBalance"),
        0xa404: ("Digital zoom ratio", "DigitalZoomRation"),
        0xa405: ("Focal length in 35mm film", "FocalLengthIn35mmFilm"),
        0xa406: ("Scene capture type", "SceneCaptureType"),
        0xa407: ("Gain control", "GainControl"),
        
        # H. Other tags
        0xa420: ("Unique image ID", "ImageUniqueID"),
        }
    embedded_tags = {
        0x927c: IfdMakerNote,
        }
    name = "Extended EXIF"

class IfdTIFF(IfdData):
    """
    """

    tags = {
        # Private Tags
        0x8769: ("Exif IFD Pointer", "ExifOffset", LONG), 
        0xA005: ("Interoparability IFD Pointer", "InteroparabilityIFD", LONG),
        0x8825: ("GPS Info IFD Pointer", "GPSIFD", LONG),
        # TIFF stuff used by EXIF

        # A. Tags relating to image data structure
        0x100: ("Image width", "ImageWidth", LONG),
        0x101: ("Image height", "ImageHeight", LONG),
        0x102: ("Number of bits per component", "BitsPerSample", SHORT),
        0x103: ("Compression Scheme", "Compression", SHORT),
        0x106: ("Pixel Composition", "PhotometricInterpretion", SHORT),
        0x112: ("Orientation of image", "Orientation", SHORT),
        0x115: ("Number of components", "SamplesPerPixel", SHORT),
        0x11c: ("Image data arrangement", "PlanarConfiguration", SHORT),
        0x212: ("Subsampling ration of Y to C", "YCbCrSubsampling", SHORT),
        0x213: ("Y and C positioning", "YCbCrCoefficients", SHORT),
        0x11a: ("X Resolution", "XResolution", RATIONAL),
        0x11b: ("Y Resolution", "YResolution", RATIONAL),
        0x128: ("Unit of X and Y resolution", "ResolutionUnit", SHORT),

        # B. Tags relating to recording offset
        0x111: ("Image data location", "StripOffsets", LONG),
        0x116: ("Number of rows per strip", "RowsPerStrip", LONG),
        0x117: ("Bytes per compressed strip", "StripByteCounts", LONG),
        0x201: ("Offset to JPEG SOI", "JPEGInterchangeFormat", LONG),
        0x202: ("Bytes of JPEG data", "JPEGInterchangeFormatLength", LONG),

        # C. Tags relating to image data characteristics

        # D. Other tags
        0x132: ("File change data and time", "DateTime", ASCII),
        0x10f: ("Camera Make", "Make", ASCII),
        0x110: ("Camera Model", "Model", ASCII),
    }
    
    embedded_tags = {
        0xA005: IfdInterop,
        EXIF_OFFSET: IfdExtendedEXIF,
        0x8825: IfdGPS,
        }

    name = "TIFF Ifd"

    def special_handler(self, tag, data):
        if tag == Make:
            self.exif_file.make = data

    def new_gps(self):
        if self.has_key(GPSIFD):
            raise ValueError, "Already have a GPS Ifd" 
        gps = IfdGPS(self.e, 0, self.exif_file)
        gps[GPSVersionID] = ['\x02', '\x02', '\x00', '\x00']
        self[GPSIFD] = gps
        return gps

make_syms2(IfdTIFF.tags)

class IfdThumbnail(IfdTIFF):
    name = "Thumbnail"

    def ifd_handler(self, data):
        size = None
        offset = None
        for (tag, type, val) in self.entries:
            if (tag == 0x201):
                offset = val[0]
            if (tag == 0x202):
                size = val[0]
        if size is None or offset is None:
            raise ExifFile.InvalidFile("Thumbnail doesn't have an offset and/or size")
        self.jpeg_data = data[offset:offset+size]
        if len(self.jpeg_data) != size:
            raise ExifFile.InvalidFile("Not enough data for JPEG thumbnail. Wanted: %d got %d" %
                                       (size, len(self.jpeg_data)))

    def extra_ifd_data(self, offset):
        for i in range(len(self.entries)):
            entry = self.entries[i]
            if entry[0] == 0x201:
                # Print found field and updating
                new_entry = (entry[0], entry[1], [offset])
                self.entries[i] = new_entry
        return self.jpeg_data

class ExifSegment(DefaultSegment):
    """ExifSegment encapsulates the Exif data stored in a JpegFile. An ExifSegment
    contains two Image File Directories (IFDs). One is attribute information and
    the other is a thumbnail. This module doesn't provide any useful functions for
    manipulating the thumbnail, but does provide a get_attributes returns an AttributeIfd
    instances which allows you to manipulate the attributes in a Jpeg file."""
    
    def parse_data(self, data):
        """Overloads the DefaultSegment method to parse the data of
        this segment. Can raise InvalidFile if we don't get what we expect."""
        self.data = data
        exif = unpack("6s", data[:6])[0]
        exif = exif.strip('\0')

        if (exif != "Exif"):
            raise JpegFile.InvalidFile("Bad Exif Marker. Got <%s>, expecting <Exif>" % exif)

        tiff_data = data[TIFF_OFFSET:]
        data = None # Don't need or want data for now on..
        
        tiff_endian = tiff_data[:2]
        if tiff_endian == "II":
            e = "<"
        elif tiff_endian == "MM":
            e = ">"
        else:
            raise JpegFile.InvalidFile("Bad TIFF endian header. Got <%s>, "
                                       "expecting <II> or <MM>" % tiff_endian)

        tiff_tag, tiff_offset = unpack(e + 'HI', tiff_data[2:8])

        if (tiff_tag != TIFF_TAG):
            raise JpegFile.InvalidFile("Bad TIFF tag. Got <%x>, expecting <%x>" % (tiff_tag, TIFF_TAG))

        # Ok, the header parse out OK. Now we parse the IFDs contained in
        # the APP1 header.
        
        # We use this loop, even though we can really only expect and support
        # two IFDs, the Attribute data and the Thumbnail data
        ifds = []
        offset = tiff_offset
        count = 0

        while offset:
            count += 1
            num_entries = unpack(e + 'H', tiff_data[offset:offset+2])[0]
            start = 2 + offset + (num_entries*12)
            if (count == 1):
                ifd = IfdTIFF(e, offset, self, tiff_data)
            elif (count == 2):
                ifd = IfdThumbnail(e, offset, self, tiff_data)
            else:
                raise ExifFile.InvalidFile()
            ifds.append(ifd)

            # Get next offset
            offset = unpack(e + "I", tiff_data[start:start+4])[0]

        self.ifds = ifds
        self.e = e

    def dump(self, f):
        for ifd in self.ifds:
            ifd.dump(f)

    def get_data(self):
        ifds_data = ""
        next_offset = 8
        for ifd in self.ifds:
            debug("OUT IFD")
            new_data, next_offset = ifd.getdata(self.e, next_offset, ifd == self.ifds[-1])
            ifds_data += new_data
            
        data = ""
        data += "Exif\0\0"
        data += "II"
        data += pack(self.e + "HI", 42, 8)
        data += ifds_data
        
        return data

    def get_primary(self):
        """Return the attributes image file descriptor."""
        return self.ifds[0]


jpeg_markers = {
    0xc0: ("SOF0", DefaultSegment),
    0xc2: ("SOF2",DefaultSegment),
    0xc4: ("DHT", DefaultSegment),

    0xda: ("SOS", StartOfScanSegment),
    0xdb: ("DQT", DefaultSegment),
    
    0xe0: ("APP0", DefaultSegment),
    0xe1: ("APP1", ExifSegment),
    0xe2: ("APP2", DefaultSegment),
    0xe3: ("APP3", DefaultSegment),
    0xe4: ("APP4", DefaultSegment),
    0xe5: ("APP5", DefaultSegment),
    0xe6: ("APP6", DefaultSegment),
    0xe7: ("APP7", DefaultSegment),
    0xe8: ("APP8", DefaultSegment),
    0xe9: ("APP9", DefaultSegment),
    0xea: ("APP10", DefaultSegment),
    0xeb: ("APP11", DefaultSegment),
    0xec: ("APP12", DefaultSegment),
    0xed: ("APP13", DefaultSegment),
    0xee: ("APP14", DefaultSegment),
    0xef: ("APP15", DefaultSegment),
    
    0xfe: ("COM", DefaultSegment),
    }

make_syms(jpeg_markers)


class JpegFile:
    """JpegFile object. You should create this using one of the static methods
    fromFile, fromString or fromFd. The JpegFile object allows you to examine and
    modify the contents of the file. To write out the data use one of the methods
    writeFile, writeString or writeFd. To get an ASCII dump of the data in a file
    use the dump method."""
    
    def fromFile(filename):
        """Return a new JpegFile object from a given filename."""
        return JpegFile(open(filename, "rb"), filename=filename)
    fromFile = staticmethod(fromFile)

    def fromString(str):
        """Return a new JpegFile object taking data from a string."""
        return JpegFile(StringIO.StringIO(str), "from buffer")
    fromString = staticmethod(fromString)

    def fromFd(fd):
        """Return a new JpegFile object taking data from a file object."""
        return JpegFile(fd, "fd <%d>" % fd.fileno())
    fromFd = staticmethod(fromFd)

    class InvalidFile(Exception):
        """This exception is raised if a given file is not able to be parsed."""
        pass
    
    def __init__(self, input, filename=None):
        """JpegFile Constructor. input is a file object, and filename is a string used to name the file.
        (filename is used only for display functions). You shouldn't use this function directly, but rather
        call one of the static methods fromFile, fromString or fromFd."""
        self.filename = filename
        
        # input is the file descriptor
        soi_marker = input.read(len(SOI_MARKER))

        # The very first thing should be a start of image marker
        if (soi_marker != SOI_MARKER):
            raise self.InvalidFile("Error reading soi_marker. Got <%s> should be <%s>" %
                                   (soi_marker, SOI_MARKER))

        # Now go through and find all the blocks of data
        segments = []
        while 1:
            head = input.read(2)
            delim, mark  =  unpack(">BB", head)
            if (delim != 255):
                raise self.InvalidFile("Error, expecting delmiter. Got <%s> should be <%s>" %
                                       (delim, DELIM))
            if mark == EOI:
                break
            head2 = input.read(2)
            size = unpack(">H", head2)[0]
            data = input.read(size-2)
            segments.append(jpeg_markers[mark][1](mark, input, data))

        self._segments = segments

    def writeString(self):
        """Write the JpegFile out to a string. Returns a string."""
        f = StringIO.StringIO()
        self.writeFd(f)
        return f.getvalue()

    def writeFile(self, filename):
        """Write the JpegFile out to a file named filename."""
        output = open(filename, "wb")
        self.writeFd(output)

    def writeFd(self, output):
        """Write the JpegFile out on the file object output."""
        output.write(SOI_MARKER)
        for segment in self._segments:
            segment.write(output)
        output.write(EOI_MARKER)

    def dump(self, f = sys.stdout):
        """Write out ASCII representation of the file on a given file object. Output
        default to stdout."""
        print >> f, "<Dump of JPEG %s>" % self.filename
        for segment in self._segments:
            segment.dump(f)

    def get_exif(self):
        """get_exif returns a ExifSegment if one exists for this file, otherwise
        it returns None."""
        for segment in self._segments:
            if segment.marker == APP1:
                return segment
        return None

    def get_geo(self):
        """Return a tuple of (latitude, longitude)."""
        gps = self.get_exif().get_primary()[GPSIFD]

        (deg, min, sec) =  gps[GPSLatitude]
        lat = (float(deg.num) / deg.den) + (1/60.0 * float(min.num) / min.den) + (1/3600.0 * float(sec.num) / sec.den)
        if gps[GPSLatitudeRef] == "S":
            lat = -lat
        
        (deg, min, sec) =  gps[GPSLongitude]
        lng = (float(deg.num) / deg.den) + (1/60.0 * float(min.num) / min.den) + (1/3600.0 * float(sec.num) / sec.den)
        if gps[GPSLatitudeRef] == "W":
            lng = -lng

        return lat, lng

    SEC_DEN = 50000000

    def _parse(val):
        sign = 1
        if val < 0:
            val  = -val
            sign = -1
            
        deg = int(val)
        other = (val - deg) * 60
        minutes = int(other)
        secs = (other - minutes) * 60
        secs = int(secs * JpegFile.SEC_DEN)
        return (sign, deg, minutes, secs)

    _parse = staticmethod(_parse)
        
    def set_geo(self, lat, lng):
        """Set the GeoLocation to a given lat and lng"""
        attr = self.get_exif().get_primary()
        gps = attr[GPSIFD]
        if gps is None:
            gps = attr.new_gps()

        sign, deg, min, sec = JpegFile._parse(lat)
        ref = "N"
        if sign < 0:
            ref = "S"

        gps[GPSLatitudeRef] = ref
        gps[GPSLatitude] = [Rational(deg, 1), Rational(min, 1), Rational(sec, JpegFile.SEC_DEN)]
        
        sign, deg, min, sec = JpegFile._parse(lng)
        ref = "E"
        if sign < 0:
            ref = "W"
        gps[GPSLongitudeRef] = ref
        gps[GPSLongitude] = [Rational(deg, 1), Rational(min, 1), Rational(sec, JpegFile.SEC_DEN)]
        
