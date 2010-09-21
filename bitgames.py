'''

    BitGames.py

    INTRODUCTION:
        TODO: put shortcut to the documention of SAD packets

    CHANGE LOG:

        Version 1.1:
            logger has been added, and verbose commands

        Version 1.0:
            first working version

    TODO-LIST:
        * make a cmdline to show selective info from packet
        * Check CRC correctness
        * add XML output too.
 '''

__version__ = '1.1'
__author__  = "Israel Fruchter (israel.fruchter@gmail.com)"
__date__    = '2009-Jun-15'
__copyright__ = "(C) 2009 Israel Fruchter. GNU GPL 3."

info = '''
    Version: ''' + __version__ + '''

    Author: ''' + __author__ + '''

    Date: ''' + __date__ + '''
'''

import sys
import getopt
import logging
from BitVector import BitVector
from BitPacket import BitStructure, BitField, array, BYTE_SIZE, BIT_SIZE


class BitStructureExt(BitStructure):
    desc = None
    def __init__(self, *arg, **karg):
        BitStructure.__init__(self, *arg, **karg)
    def xml(self, indent = 0):
        '''
        Returns a human-readable representation xml of the structure.
        '''
        s = ''
        for i in range(indent):
            s += ' '
        if (self.desc != None):
            s += '<BitStructure name="%s" desc="%s"' % (self._name, self.desc)
        else:
            s += '<BitStructure name="%s"' % self._name
        for field in self.__fields:
            s += '\n'
            s += field.xml(indent + 3)
        s += '\n'
        for i in range(indent):
            s += ' '
        s += '</BitStructure>'
        return s

    def __str__(self, indent = 0):
        '''
        Returns a human-readable representation of the structure.
        '''
        s = ''
        for i in range(indent):
            s += ' '
        if (self.desc != None):
            s += '(%s = - %s -' % (self._name, self.desc)
        else:
            s += '(%s = ' % self._name
        for field in self.__fields:
            s += '\n'
            s += field.__str__(indent + 3)
        s += ')'
        return s

class BitFieldExt(BitField):
    desc = None

    def xml(self, indent = 0):
        '''
        Prints the name and value of the field with an optional
        indentation.
        '''
        s = ""
        for i in range(indent):
            s += " "
        if (self.desc != None):
            s += '<BitField name="%s"  value="0x%X" desc="%s" />' % (self._name, self.value(), self.desc)
        else:
            s += '<BitField name="%s"  value="0x%X" />' % (self._name, self.value())
        return s

    def __str__(self, indent = 0):
        '''
        Prints the name and value of the field with an optional
        indentation.
        '''
        s = ""
        for i in range(indent):
            s += " "
        if (self.desc != None):
            s += "(%s = 0x%X) - %s -" % (self._name, self.value(), self.desc)
        else:
            s += "(%s = 0x%X)" % (self._name, self.value())
        return s

__usage__ = '''
USAGE:
    bitgames [-v] [-t number] [-i filename]

    -i / --input    : the file hold packet (in HEX)
    -t / --test    : running a unit test by number (currently 1-3)
    -v         : Verbose (run with debug prints)
'''
def usage ():
    ''' print usage for user'''
    print __usage__

LOG = logging.getLogger("simple_example")

def byte_to_hex( byte_str ):
    '''
    Convert a byte string to it's hex string representation e.g. for output.
    '''

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byte_str:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()


    return ''.join( [ "%02X " % ord( x ) for x in byte_str ] ).strip()


def hex_to_byte( hex_str ):
    '''
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    '''
    bytes = []

    hex_str = ''.join( hex_str.split(" ") )
    for i in range(0, len(hex_str), 2):
        bytes.append( chr( int (hex_str[i:i+2], 16 ) ) )

    return ''.join( bytes )

def DVB_MJD_to_string( bit_structure=None , byte_array=None ):
    '''
    convert 5 byte array to string reprsention time

    from ETSI EN 300 468
    Digital Video Broadcasting (DVB);
    Specification for Service Information (SI) in DVB systems
    '''


    if (byte_array == None):
        byte_array = array.array('B', bit_structure.array())

    if (len(byte_array) != 5):
        LOG.error("No a DVB MJD: size is not 5 bytes")
        return "Didn't parse"
    elif (byte_to_hex(byte_array.tostring()) == "FF FF FF FF FF"):
        LOG.error("No a DVB MJD: 0xFFFFFFFFFF")
        return "Unlimited"
    elif (byte_to_hex(byte_array.tostring()) == "00 00 00 00 00"):
        LOG.error("No a DVB MJD: 0x0000000000")
        return "None"

    LOG.debug( byte_to_hex(byte_array.tostring()))

    bs = BitStructureExt('MJD+UTC')
    bs.append(BitFieldExt('MJD',        BYTE_SIZE * 2))
    bs.append(BitFieldExt('hours',    BYTE_SIZE * 1))
    bs.append(BitFieldExt('mins',    BYTE_SIZE * 1))
    bs.append(BitFieldExt('secs',    BYTE_SIZE * 1))
    bs.set_array (byte_array)
    number = bs['MJD']
    LOG.debug( "DVB_MJD_to_string got MJD: 0x%x" % number)

    Y_tag = int((int (number) - 15078.2) / 365.25)
    M_tag = int( (int (number) - 14956.1 - int (Y_tag * 365.25) ) / 30.6001 )
    D = int(number) - 14956 - int (Y_tag * 365.25) - int (M_tag * 30.6001 )

    if ((M_tag == 14) or (M_tag == 15)):
        K = 1
    else:
        K = 0
    Y = Y_tag + K
    M = M_tag - 1 - K * 12

    time_string = "%s/%s/%s %x:%x:%x " % (D,M,1900+Y, bs['hours'],bs['mins'],bs['secs'])
    LOG.debug(time_string)

    return time_string

def parse_PES_START_INFO ( bs_input , data):
    '''
    Parsing data into  PES_START_INFO and append it to bs_input (BitStructre)
    '''
    LOG.debug("entering parse_PES_START_INFO")
    bs = BitStructureExt('PES_START_INFO')
    bs.append(BitFieldExt('packet_start_code_prefix',        BYTE_SIZE * 3))
    bs.append(BitFieldExt('stream_id',                        BYTE_SIZE * 1)) #defult 0xbd
    bs.append(BitFieldExt('PES_packet_length',                BYTE_SIZE * 2))
    bs_input.append(bs)

    flags = BitStructureExt('PES_HEADER_FLAGS')
    flags.append(BitFieldExt('PES_fixed_value',            BIT_SIZE * 2))
    flags.append(BitFieldExt('PES_scrambling_control',        BIT_SIZE * 2))
    flags.append(BitFieldExt('PES_priority',                BIT_SIZE * 1))
    flags.append(BitFieldExt('data_alignment_indicator',    BIT_SIZE * 1))
    flags.append(BitFieldExt('copyright',                    BIT_SIZE * 1))
    flags.append(BitFieldExt('original_or_copy',            BIT_SIZE * 1))
    flags.append(BitFieldExt('PTS_DTS_flags',                BIT_SIZE * 2))
    flags.append(BitFieldExt('ESCR_flag',                    BIT_SIZE * 1))
    flags.append(BitFieldExt('ES_rate_flag',                BIT_SIZE * 1))
    flags.append(BitFieldExt('DSM_trick_mode_flag',        BIT_SIZE * 1))
    flags.append(BitFieldExt('addtional_copy_info_flag',    BIT_SIZE * 1))
    flags.append(BitFieldExt('PES_CRC_flag',                BIT_SIZE * 1))
    flags.append(BitFieldExt('PES_extention_flag',            BIT_SIZE * 1))

    bs_input.append(flags)
    bs_input.set_array(data)

    if (bs_input.field('PES_HEADER_FLAGS').field('PTS_DTS_flags').value() == 0x2):
        bs_input.append(BitFieldExt('PES_HEADER_PTS_Length', BYTE_SIZE * 1))

        pts = BitStructureExt('PES_HEADER_PTS')

        pts.append(BitFieldExt('Fixed_PTS_HEADER',    BIT_SIZE * 4 ))
        pts.append(BitFieldExt('PTS 32..30',        BIT_SIZE * 3 ))
        pts.append(BitFieldExt('marker bit 1',        BIT_SIZE * 1 ))
        pts.append(BitFieldExt('PTS 29..15',        BIT_SIZE * 15))
        pts.append(BitFieldExt('marker bit 2',        BIT_SIZE * 1 ))
        pts.append(BitFieldExt('PTS 14..0',        BIT_SIZE * 15))
        pts.append(BitFieldExt('marker bit 3',        BIT_SIZE * 1 ))

        bs_input.append(pts)
        bs_input.set_array(data)

        parsed_pts = bs_input.field('PES_HEADER_PTS')
        p1 = BitVector( intVal = parsed_pts['PTS 32..30'], size = 3 )
        p2 = BitVector( intVal = parsed_pts['PTS 29..15'], size = 15)
        p3 = BitVector( intVal = parsed_pts['PTS 14..0'] , size = 15)
        LOG.debug ("PTS in Decimal: "+str(int(p1+p2+p3)))
        pts.desc = "PTS in Decimal: "+str(int(p1+p2+p3))
    else:
        # No PTS in header
        LOG.error("No PTS in header")
        return 1
    LOG.debug("exit parse_PES_START_INFO")
    return 0

def parse_SAD_PAYLOAD ( bs_input , data):
    '''
    Parsing data into  SAD_PAYLOAD and append it to bs_input (BitStructre)
    '''
    flags = BitStructureExt('SAD_FLAGS')
    flags.append(BitFieldExt('payload_format',  BIT_SIZE * 4))
    flags.append(BitFieldExt('reserved',         BIT_SIZE * 3))
    flags.append(BitFieldExt('CRC_flag',         BIT_SIZE * 1))
    bs_input.append(flags)
    bs_input.set_array(data)
    bs_input.append(BitFieldExt('desc_loop_length', BYTE_SIZE * 2))
    bs_input.set_array(data)

    LOG.debug("desc_loop_length : " + str( bs_input['desc_loop_length']))

    test = int(bs_input['desc_loop_length'])
    if (test > 0):
        #bs_input.append(BitFieldExt('descriptors', BYTE_SIZE * test ))
        parse_DESCRIPTORS(bs_input, data, test ,0)
    else:
        LOG.debug("parse_SAD_PAYLOAD: No descriptors")

    bs_input.append(BitFieldExt('rules_loop_length', BYTE_SIZE * 2))
    bs_input.set_array(data)

    test = int(bs_input['rules_loop_length'])
    if (test > 0):
        # bs_input.append(BitFieldExt('rules', BYTE_SIZE * test ))
        parse_RULES_PAYLOAD(bs_input, data, test)
    else:
        LOG.debug( "parse_SAD_PAYLOAD: No rules" )
    if (bs_input.field('SAD_FLAGS').field('CRC_flag').value() == 0x1):
        bs_input.append(BitFieldExt('CRC_32', BYTE_SIZE * 8))
        # TODO: actully test the CRC
        bs_input.set_array(data)
    else:
        LOG.debug( "parse_SAD_PAYLOAD: No CRC" )
    return 0

def parse_SYNC_EVENT_DESC( bs_input , data, bytes_to_read):
    '''
    parse SYNC_EVENT_DESC descriptor return the number of byte left
    in the descriptor payload
    '''
    desc = BitStructureExt('SYNC_EVENT_DESC')
    desc.append(BitFieldExt('descriptor_len',            BYTE_SIZE * 1    ))
    desc.append(BitFieldExt('sync_event_context',        BYTE_SIZE * 1    ))
    desc.append(BitFieldExt('sync_event_id',            BYTE_SIZE * 2    ))
    desc.append(BitFieldExt('sync_event_id_instance',    BYTE_SIZE * 1    ))
    desc.append(BitFieldExt('2 Bit reserverd',            BIT_SIZE    * 2    ))
    desc.append(BitFieldExt('tick_format',                BIT_SIZE    * 6    ))
    desc.append(BitFieldExt('reference_offset_ticks',    BYTE_SIZE * 2    ))
    desc.append(BitFieldExt('sync_event_data_length',    BYTE_SIZE * 1    ))

    bs_input.append(desc)
    bs_input.set_array(data)

    #    Check if this desc. has data in it, and take it
    sync_event_data_length = bs_input.field('SYNC_EVENT_DESC').field('sync_event_data_length').value()
    if (sync_event_data_length > 0):
            bs_input.field('SYNC_EVENT_DESC').append(
                BitFieldExt('sync_event_data_byte',     sync_event_data_length))

    #    remove the length of this descriptor
    descriptor_len = bs_input.field('SYNC_EVENT_DESC').field('descriptor_len').value()
    LOG.debug( "descriptor_len: " + str( descriptor_len ))
    bytes_to_read -= (descriptor_len + 2)

    LOG.debug( "bytes_to_read: " + str(bytes_to_read) )

    return bytes_to_read


def parse_SPLICE_EVENT_DESC( bs_input , data, bytes_to_read):
    '''
    parse SPLICE_EVENT_DESC descriptor return the number of byte left
    in the descriptor payload
    '''
    desc = BitStructureExt('SPLICE_EVENT_DESC')
    desc.append(BitFieldExt('descriptor_len',            BYTE_SIZE     * 1    ))
    desc.append(BitFieldExt('2 Bit reserverd',            BIT_SIZE    * 2 ))
    desc.append(BitFieldExt('tick_format',                BIT_SIZE    * 6    ))
    desc.append(BitFieldExt('absolute_ticks',            BYTE_SIZE     * 4    ))
    desc.append(BitFieldExt('splice_event_data_length',BYTE_SIZE     * 1    ))

    bs_input.append(desc)
    bs_input.set_array(data)

    #    Check if this desc. has data in it, and take it
    splice_event_data_length = bs_input.field('SPLICE_EVENT_DESC').field('splice_event_data_length').value()
    if (splice_event_data_length > 0):
            bs_input.field('SPLICE_EVENT_DESC').append(
                BitFieldExt('splice_event_data_byte',     splice_event_data_length))

    #    remove the length of this descriptor
    descriptor_len = bs_input.field('SPLICE_EVENT_DESC').field('descriptor_len').value()
    LOG.debug( "descriptor_len: " + str( descriptor_len ))
    bytes_to_read -= descriptor_len + 2

    LOG.debug( "bytes_to_read: " + str ( bytes_to_read ))

    return bytes_to_read

def parse_SUBST_AD_DESC( bs_input , data, bytes_to_read):

    desc = BitStructureExt('SUBST_AD_DESC')
    desc.append(BitFieldExt('descriptor_len',            BYTE_SIZE * 1 ))
    desc.append(BitFieldExt('outPoint',                BIT_SIZE  * 1 ))
    desc.append(BitFieldExt('opportunityType',            BIT_SIZE  * 2 ))
    desc.append(BitFieldExt('reserved',                BIT_SIZE  * 5 ))
    bs_input.append(desc)
    bs_input.set_array(data)

    outPoint = bs_input.field('SUBST_AD_DESC').field('outPoint').value()

    if(outPoint):
        desc.append(BitFieldExt('auto_return',        BIT_SIZE * 1 ))
        desc.append(BitFieldExt('durationFlag',    BIT_SIZE * 1 ))
        desc.append(BitFieldExt('duration_format',    BIT_SIZE * 6 ))
        bs_input.set_array(data)

        auto_return = bs_input.field('SUBST_AD_DESC').field('auto_return').value()
        durationFlag = bs_input.field('SUBST_AD_DESC').field('durationFlag').value()

        if(auto_return & durationFlag):
            desc.append(BitFieldExt('duration',    BYTE_SIZE * 4 ))
        else:
            LOG.debug( "parse_SUBST_AD_DESC: NO duration" )

    desc.append(BitFieldExt('numIds', BYTE_SIZE * 1 ))

    bs_input.set_array(data)
    numIds = desc.field('numIds').value()

    LOG.debug( "numIds: "+ str(numIds) )
    for i in range(0, numIds):
        numIds_bs = BitStructureExt('NUM_ID')
        numIds_bs.append(BitFieldExt('idType',        BYTE_SIZE * 1    ))
        numIds_bs.append(BitFieldExt('id_length',    BYTE_SIZE * 1    ))
        numIds_bs.append(BitFieldExt('id_bytes',    BYTE_SIZE * 4    ))
        bs_input.field('SUBST_AD_DESC').append(numIds_bs)

    bs_input.set_array(data)

    #    Check if this desc. has data in it, and take it
    #    remove the length of this descriptor
    descriptor_len = bs_input.field('SUBST_AD_DESC').field('descriptor_len').value()
    LOG.debug(  "descriptor_len: " + str( descriptor_len ))
    bytes_to_read -= descriptor_len + 2
    LOG.debug(  "bytes_to_read: " + str( bytes_to_read ))

    return bytes_to_read

def parse_DESCRIPTORS ( bs_input , data, bytes_to_read , desc_number):

    if (bytes_to_read <= 0):
        LOG.debug( "parse_DESCRIPTORS: finished" )
        return -1;

    desc_tag_name = 'descriptor_tag' + str(desc_number)
    bs_input.append(BitFieldExt(desc_tag_name, BYTE_SIZE * 1))
    LOG.debug( "bytes_to_read: " + str( bytes_to_read ))
    bytes_to_read - 2
    LOG.debug( "bytes_to_read: " + str( bytes_to_read ))
    bs_input.set_array(data)

    test = int(bs_input[desc_tag_name])
    if (test==5):
        # parse Desciptor
        bytes_to_read = parse_SYNC_EVENT_DESC(bs_input,data,bytes_to_read)
        # parse next descriptor
        parse_DESCRIPTORS(bs_input,data,bytes_to_read, desc_number + 1)
    elif (test==0x80):
        # parse Desciptor
        # call parse_DESCRIPTORS
        LOG.critical ( "PCR_OFFSET_DESC isn't supported yet" )
    elif (test==0x81):
        # parse Desciptor
        bytes_to_read = parse_SPLICE_EVENT_DESC(bs_input,data,bytes_to_read)
        # parse next descriptor
        parse_DESCRIPTORS(bs_input,data,bytes_to_read, desc_number + 1)
    elif (test==0x82):
        # parse Desciptor
        bytes_to_read = parse_SUBST_AD_DESC(bs_input,data,bytes_to_read)
        # parse next descriptor
        parse_DESCRIPTORS(bs_input,data,bytes_to_read, desc_number + 1)
    else:
        LOG.critical ("parse_DESCRIPTORS: no such decriptor: "+str( test ))
        LOG.debug( bs_input )
        return -1

def parse_RULES_PAYLOAD( bs_input , data, bytes_to_read):

    rule_payload = BitStructureExt('RULES_PAYLOAD')
    rule_payload.append(BitFieldExt('version',     BIT_SIZE * 4    ))
    rule_payload.append(BitFieldExt('availType',    BIT_SIZE * 4    ))
    rule_payload.append(BitFieldExt('expiryDate',    BIT_SIZE * 40    ))
    rule_payload.append(BitFieldExt('numSpots',    BIT_SIZE * 8    ))
    bs_input.append(rule_payload)

    LOG.debug (DVB_MJD_to_string(rule_payload.field('expiryDate'), None ))

    bs_input.set_array(data)
    numSpots = rule_payload.field('numSpots').value()
    LOG.debug( "numSpots: "+ str(numSpots) )

    for i in range(0, numSpots):
        spot = BitStructureExt('SPOT_'+str(i))
        spot.append(BitFieldExt('spotIdFlag',        BIT_SIZE * 1    ))
        spot.append(BitFieldExt('reserved',         BIT_SIZE * 7    ))

        bs_input.field('RULES_PAYLOAD').append(spot)
        bs_input.set_array(data)

        LOG.debug("spotIdFlag: "+str(spot['spotIdFlag'] ))
        if (spot['spotIdFlag']):
            spot.append(BitFieldExt('spotId',         BIT_SIZE * 32    ))
        else:
            LOG.debug(" NO spotId for this spot")

        spot.append(BitFieldExt('numSubstitutions',BIT_SIZE * 8    ))
        bs_input.set_array(data)

        numSubstitutions = spot['numSubstitutions']
        LOG.debug( "numSubstitutions: "+ str(numSubstitutions) )
        for j in range(0, numSubstitutions):
            sub = BitStructureExt('SUBSTITUTION_'+str(j))
            sub.append(BitFieldExt('ruleStartDate',    BIT_SIZE * 40    ))
            sub.append(BitFieldExt('ruleEndDate',        BIT_SIZE * 40    ))
            sub.append(BitFieldExt('profileLength',    BIT_SIZE * 8    ))
            spot.append(sub)

            bs_input.set_array(data)
            sub.field('ruleStartDate').desc     = DVB_MJD_to_string(sub.field('ruleStartDate'), None)
            sub.field('ruleEndDate').desc         = DVB_MJD_to_string(sub.field('ruleEndDate'),     None)
            profileLength = sub['profileLength']
            if (profileLength > 0):
                sub.append(BitFieldExt('profileByte',    BYTE_SIZE * profileLength))
                bs_input.set_array(data)
                sub.field('profileByte').desc = ProfileByte_to_string(sub.field('profileByte'), profileLength)
            else:
                LOG.error(" NO Rule for this Substitutions")

            sub.append(BitFieldExt('numAds',    BIT_SIZE * 8    ))
            bs_input.set_array(data)


            numAds = sub['numAds']
            LOG.debug( "numAds: "+ str(numAds) )
            for k in range(0, numAds):
                ad = BitStructureExt('AD_'+str(k))
                ad.append(BitFieldExt('reserved',    BIT_SIZE * 1    ))
                ad.append(BitFieldExt('indirectID',BIT_SIZE * 7    ))
                ad.append(BitFieldExt('adID',        BIT_SIZE * 32    ))
                ad.append(BitFieldExt('duration',    BIT_SIZE * 16    ))
                sub.append(ad)
                bs_input.set_array(data)
"""

Substitute_rules_Payload() {
    version    4
    availType    4
    expiryDate    40
    numSpots    8
    for(int i=0; i<numSpots; i++) {
        spotIdFlag    1
        reserved    7
        if(spotIdFlag==1) {
            spotId    32
        }
        numSubstitutions    8
        for(int j=0; j<numSubstitutions; j++) {
            rule {
                ruleStartDate    40
                ruleEndDate    40
                profileLength    8
                for(int p=0; p<profileLength; p++) {
                    profileByte    8
                }
            }
            numAds    8
            for(int n=0; n<numAds; n++) {
                reserved    7
                indirectID    1
                adID    32
                duration    16
            }
        }
    }
}

"""

def ProfileByte_to_string ( profileByte , length , data=None):
    '''
    Parse the profile byte and return a string represntion of it

    Table 3    Data Type Definitions
    DataType Value    Data Length    Mnemonic    Description
    0x00    8 bits    uimsbf    This specifies that the proceeding data byte defines an evaluation that should take place. The set of valid values is defined in Table 4

    0x01    16 bits    uimsbf (MSBF)    This signals that the data represents a Profile attribute. The STB shall retrieve the value associated with this Profile Attribute.
    0x02    16 bits    uimsbf (MSBF)    A 16 bit unsigned int value
    0x03    32 bits    uimsbf (MSBF)    A 32 bit unsigned int value
    0x04    8 bits    uimsbf (MSBF)    An 8 bit unsigned int value
    0x05    variable    blsbf    A null terminated ASCII string of variable length.


    Table 4    Operator data values
    Data Value    Description
    0x01    Signals an "equals" comparison
    0x02     Signals a "less than" comparison
    0x03    Signals a "greater than" comparison
    0x04    Signals a "less than or equals" comparison
    0x05    Signals a "greater than or equals" comparison
    0x06    Signals a "not" comparison
    0x07    Signals a "not equals" comparison
    0x08    Signals an "AND"  comparison
    0x09    Signals an "OR" comparison
    '''
    operators = [ "==", "<", ">", "<=", ">=", "!=", "and", "or"]
    one_opt = ["!"]

    if (data == None):
        data = array.array('B', profileByte.array())

    bs = BitStructureExt("PROFILE")
    byte_to_read = length
    i = 0
    s = []

    while (byte_to_read > 0):
        LOG.debug ("ProfileByte_to_string: byte_to_read = " + str(byte_to_read))
        bs.append(BitFieldExt('Type_' +str(i) ,    BYTE_SIZE * 1))
        byte_to_read -= 1
        bs.set_array(data)
        type = bs['Type_' + str(i) ]
        if (type == 0x0):
            # take 8 bits
            bs.append(BitFieldExt('Value_' +str(i) ,    BIT_SIZE * 8))
            byte_to_read -= 1
            bs.set_array(data)
            predicte = bs['Value_' +str(i)]
            if (predicte == 0x01):
                s.append("==")
            elif (predicte == 0x02):
                s.append("<")
            elif (predicte == 0x03):
                s.append(">")
            elif (predicte == 0x04):
                s.append("<=")
            elif (predicte == 0x05):
                s.append(">=")
            elif (predicte == 0x06):
                s.append("!")
            elif (predicte == 0x07):
                s.append("!=")
            elif (predicte == 0x08):
                s.append("and")
            elif (predicte == 0x09):
                s.append("or")
            else:
                LOG.error ("Not a valid predicte inside a profile Byte: " + str (predicte))
                return "ERROR !!! in ProfileByte_to_string"
        elif (type == 0x1):
            # take 16 bits
            bs.append(BitFieldExt('Value_' +str(i) ,    BYTE_SIZE * 2))
            byte_to_read -= 2
            bs.set_array(data)
            value = bs['Value_' +str(i)]
            s.append("A" + str(value))
        elif (type == 0x2):
            # take 16 bits
            bs.append(BitFieldExt('Value_' +str(i) ,    BYTE_SIZE * 2))
            byte_to_read -= 2
            bs.set_array(data)
            value = bs['Value_' +str(i)]
            s.append(str(value))
        elif (type == 0x3):
            #take 32 bits
            bs.append(BitFieldExt('Value_' +str(i) ,    BYTE_SIZE * 4))
            byte_to_read -= 4
            bs.set_array(data)
            value = bs['Value_' +str(i)]
            s.append(str(value))
        elif (type == 0x4):
            #take 8 bits
            bs.append(BitFieldExt('Value_' +str(i) ,    BIT_SIZE * 8))
            byte_to_read -= 1
            bs.set_array(data)
            value = bs['Value_' +str(i)]
            s.append(str(value))
        elif (type == 0x5):
            # take how to take null terminated ???
            LOG.error ("No Support for null terminated vaule yet. ")
            return "ERROR !!! in ProfileByte_to_string"
        else:
            LOG.error ("No a valid type inside a profile Byte: " + str(type) )
            return "ERROR !!! in ProfileByte_to_string"
        i += 1

    temp_str = ""
    stack = []
    for item in s:
        if item in operators:
            temp_str = "( " + str(stack.pop(-2)) + " " + str(item)+" " +str(stack.pop(-1))+ " )"
            LOG.debug (temp_str)
            stack.append(temp_str)
        elif item in one_opt:
            temp_str = str(item)+"( " +str(stack.pop(-1))+ " )"
            LOG.debug (temp_str)
            stack.append(temp_str)
        else:
            stack.append(item)

    LOG.debug (str(stack))
    #Data Type Definitions

    return str(stack.pop(-1))

def ParsePacket_No_TS_Header( packet_byte_array ):

    bs = BitStructureExt('PACKET')
    bs.set_array(packet_byte_array)
    LOG.debug( "Parsing Start !!!!")
    parse_PES_START_INFO( bs , packet_byte_array)
    parse_SAD_PAYLOAD(bs, packet_byte_array)
    LOG.debug( "Parsing End !!!!")
    return (bs, packet_byte_array)

import unittest

class BitGamesTest(unittest.TestCase):
    def setUp(self): pass
    def testDavidPacket(self):
        # david packet
        data = array.array('B', hex_to_byte("000001bd008b8c80052100010001810021050801000101113e80008106030000000000820d80c300000bb801010401020304005711ffffffffff018000000001020000000000ffffffffff 13 01000f01001400020100020402000100080006 01000000000102ee0000000000ffffffffff13 01000f0100140002010002040200010008000601000000000102ee00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
        (bs, data) = ParsePacket_No_TS_Header(data)
        print bs
    def testStreamPacket(self):
        # stream packet
        data = array.array('B', hex_to_byte("000001bd002e8180052b925721bd860021050801000178d17f88008106c3001323d400820d9fc3000002ee010104000000010000"))

        (bs, data) = ParsePacket_No_TS_Header(data)
        print bs
    def testMyPacket(self):
        # my packet
        data = array.array('B', hex_to_byte("000001BD003D8C80052100010001810021050801000101113E80008106110000000000820DA0D100000BB8010104010203040007110000000000000000000000000000"))

        (bs, data) = ParsePacket_No_TS_Header(data)
        print bs
    def testMJD_UTC_Convertion(self):
        #test mjd + utc convertion
        test_data = array.array('B',hex_to_byte("D641 10 29 40"))
        res = DVB_MJD_to_string(None ,  test_data )
        self.assertEqual( "18/1/2009 10:29:40 ", str(res))

        #unlimited
        test_data = array.array('B',hex_to_byte("FFFFFFFFFF"))
        res = DVB_MJD_to_string(None ,  test_data )
        self.assertEqual( "Unlimited", str(res))

        #wrong size
        test_data = array.array('B',hex_to_byte("FFFFFFFF"))
        res = DVB_MJD_to_string(None ,  test_data )
        self.assertEqual( "Didn't parse", str(res))

    def testProfileByte_Convertion(self):
        #test profile byte convertion
        test_data = array.array('B', hex_to_byte("01 000f 01 0014 00 02 01 0002 04 02 00 01 00 08 00 06"))
        test_bs = BitStructureExt('TEST')
        test_bs.set_array(test_data)
        self.assertEqual( 19 ,  len( test_data ) )
        self.assertEqual('!( ( ( A15 < A20 ) and ( A2 == 2 ) ) )',
            ProfileByte_to_string(test_bs, len( test_data ), test_data))

    def testFailure_Convertion(self):
        #test profile byte convertion
        test_data = array.array('B', hex_to_byte("01 000f 01 0014 00 02 01 0002 04 02 00 01 00 08 00 06"))
        test_bs = BitStructureExt('TEST')
        test_bs.set_array(test_data)
        self.assertEqual( 19 ,  len( test_data ) )
        self.assertEqual('',
            ProfileByte_to_string(test_bs, len( test_data ), test_data))

    def testExecption_Convertion(self):
        raise "execption test"
        self.assertEqual('',
            ProfileByte_to_string(test_bs, len( test_data ), test_data))
def handle_args():
    ''' handle command line arg '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:ti:v", ["help", "output=", "test", "input="])
    except getopt.GetoptError, err:
        #print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    params = {}
    params['output'] = None
    params['verbose'] = False
    params['verbose_level'] = None
    params['testing'] = False
    params['input_filename'] = None

    for opt, param in opts:
        if opt == "-v":
            params['verbose'] = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-o", "--output"):
            params['output'] = param
        elif opt in ("-i", "--input"):
            params['input_filename'] = param
        elif opt in ("-t", "--test"):
            params['testing'] = True
        else:
            assert False, "unhandled option"
    return params
def configure_debug(params):
    # set debug level
    if (params['verbose']):
        verbose_level = logging.DEBUG
    else:
        verbose_level = logging.INFO
    # Log everything, and send it to stderr.
    LOG.setLevel(verbose_level)
    # create console handler and set level to debug
    con_handler = logging.StreamHandler()
    con_handler.setLevel(verbose_level)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
    # add formatter to con_handler
    con_handler.setFormatter(formatter)
    # add con_handler to logger
    LOG.addHandler(con_handler)

def main():
    '''main function'''
    params = handle_args()
    configure_debug(params)
    data = None
    # TEST PACKET

    if (params['testing']):
        from xmlrunner import XmlTestRunner
        runner = XmlTestRunner()
        runner.run(unittest.makeSuite(BitGamesTest))
        sys.exit()

    # open a file
    if(params['input_filename'] != None):
        try:
            data_file = open(params['input_filename'])
        except IOError, err:
            print err
            sys.exit(2)

        data = array.array('B', hex_to_byte(data_file.readline()))

    if (data == None):
        print "No data input !!!"
        usage()
        sys.exit(2)

    (bits, data) = ParsePacket_No_TS_Header(data)

    print bits
    print str(bits.xml())
    print byte_to_hex(data.tostring())

if __name__ == "__main__":
    main()