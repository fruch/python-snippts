#!/usr/bin/env python

import sys
import getopt
import os
from BitVector import BitVector 
from BitPacket import BitStructure, BitField, array, BYTE_SIZE, BIT_SIZE
import logging

log = logging.getLogger("simple_example")
TS_file = None
verbose = True
PES_list = []
curr_pack_num = 0 

def ByteToHex( byteStr ):
	'''
	Convert a byte string to it's hex string representation e.g. for output.
	'''

	# Uses list comprehension which is a fractionally faster implementation than
	# the alternative, more readable, implementation below
	#
	#	hex = []
	#	for aChar in byteStr:
	#		hex.append( "%02X " % ord( aChar ) )
	#
	#	return ''.join( hex ).strip()


	return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()
    
def openTSFile(filename):
    return file(filename, "rb", 188 * 1000)
    
def SeekPacket(file_obj, packet_num):
     return file_obj.seek(packet_num * 188)
     
def GetPakcet(file_obj, packet_num):
    global curr_pack_num
    curr_pack_num = packet_num
    return file_obj.read(188)
    

def parseTS_Packet(data):
    #log.debug("entering parseTS_Packet")
    bs = BitStructure('PACKET')
    bs.append(BitField('sync byte',		BIT_SIZE * 8))
    bs.append(BitField('Transport Error Indicator (TEI)', BIT_SIZE * 1)) #defult 0xbd
    bs.append(BitField('Payload Unit Start Indicator',		BIT_SIZE * 1))
    bs.append(BitField('Transport Priority',		BIT_SIZE * 1))
    bs.append(BitField('PID',		BIT_SIZE * 13))
    bs.append(BitField('Scrambling control',		BIT_SIZE * 2))
    bs.append(BitField('Adaptation field exist',		BIT_SIZE * 1))
    bs.append(BitField('Payload data exist',		BIT_SIZE * 1))
    bs.append(BitField('Continuity counter',		BIT_SIZE * 4))
    bs.set_array(data)
    pusi = bs.field('Payload Unit Start Indicator').value()
    pid = bs.field('PID').value()
    if (pusi == 0x1 and pid == 0x906):   
        print "PUSI !!! on: " + str(pid) 
        if (bs.field('Adaptation field exist').value() == 0x1):
            parseTS_Adaptation(bs, data)
        if (bs.field('Payload data exist').value() == 0x1) and (pusi == 0x1):
            parse_PES_START_INFO(bs, data)
            #print bs

def convert_BLOB_TO_PTS ( parsed_pts ):
	pts_vec = BitVector( size = 33 )
	
	pts_vec[0:3] = BitVector( intVal = int( parsed_pts['PTS 32..30'] ) , size=3 )
	pts_vec[3:18] = BitVector( intVal = int( parsed_pts['PTS 29..15'] ), size=15 )
	pts_vec[18:33]  = BitVector( intVal = int( parsed_pts['PTS 14..0']  ), size=15 )
	
	return int(pts_vec)
    
def parse_PES_START_INFO ( bs_input , data):
    '''
    Parsing data into  PES_START_INFO and append it to bs_input (BitStructre)
    '''
    #log.debug("entering parse_PES_START_INFO")
    bs = BitStructure('PES_START_INFO')
    bs.append(BitField('packet_start_code_prefix',		BYTE_SIZE * 3))
    bs.append(BitField('stream_id',						BYTE_SIZE * 1)) #defult 0xbd
    bs.append(BitField('PES_packet_length',				BYTE_SIZE * 2))
    bs_input.append(bs)

    flags = BitStructure('PES_HEADER_FLAGS')
    flags.append(BitField('PES_fixed_value',			BIT_SIZE * 2))
    flags.append(BitField('PES_scrambling_control',		BIT_SIZE * 2))
    flags.append(BitField('PES_priority',				BIT_SIZE * 1))
    flags.append(BitField('data_alignment_indicator',	BIT_SIZE * 1))
    flags.append(BitField('copyright',					BIT_SIZE * 1))
    flags.append(BitField('original_or_copy',			BIT_SIZE * 1))
    flags.append(BitField('PTS_DTS_flags',				BIT_SIZE * 2))
    flags.append(BitField('ESCR_flag',					BIT_SIZE * 1))
    flags.append(BitField('ES_rate_flag',				BIT_SIZE * 1))
    flags.append(BitField('DSM_trick_mode_flag',		BIT_SIZE * 1))
    flags.append(BitField('addtional_copy_info_flag',	BIT_SIZE * 1))
    flags.append(BitField('PES_CRC_flag',				BIT_SIZE * 1))
    flags.append(BitField('PES_extention_flag',			BIT_SIZE * 1))

    bs_input.append(flags)
    bs_input.set_array(data)

    if (bs_input.field('PES_HEADER_FLAGS').field('PTS_DTS_flags').value() == 0x2):
        bs_input.append(BitField('PES_HEADER_PTS_Length', BYTE_SIZE * 1))

        pts = BitStructure('PES_HEADER_PTS')

        pts.append(BitField('Fixed_PTS_HEADER',	BIT_SIZE * 4 ))
        pts.append(BitField('PTS 32..30',		BIT_SIZE * 3 ))
        pts.append(BitField('marker bit 1',		BIT_SIZE * 1 ))
        pts.append(BitField('PTS 29..15',		BIT_SIZE * 15))
        pts.append(BitField('marker bit 2',		BIT_SIZE * 1 ))
        pts.append(BitField('PTS 14..0',		BIT_SIZE * 15))
        pts.append(BitField('marker bit 3',		BIT_SIZE * 1 ))

        bs_input.append(pts)
        bs_input.set_array(data)

        parsed_pts = bs_input.field('PES_HEADER_PTS')
        decimal_pts = convert_BLOB_TO_PTS(parsed_pts)
        if (decimal_pts == 5426837):
            print "found !!!"
            print bs_input
            print curr_pack_num
        print "PTS in Decimal: "+str(decimal_pts)
        parsed_pts.desc = "PTS in Decimal: "+str(decimal_pts)
		
    else:
        # No PTS in header
        #log.error("No PTS in header")
        return 1
    #log.debug("exit parse_PES_START_INFO")
    return 0
  
'''
Adaptation Field Length 	8 	Number of bytes in the adaptation field immediately following this byte
Discontinuity indicator 	1 	Set to 1 if a discontinuity occurred in the continuity counter of the TS packet
Random Access indicator 	1 	Set to 1 if the PES packet in this TS packet starts a video/audio sequence
Elementary stream priority indicator 	1 	1 = higher priority
PCR flag 	1 	1 means adaptation field does contain a PCR field
OPCR flag 	1 	
Splicing point flag 	1 	1 means presence of splice countdown field in adaptation field
Transport private data flag 	1 	1 means presence of private data bytes in adaptation field
Adaptation field extension flag 	1 	1 means presence of adaptation field extension
''' 

def parseTS_Adaptation(bs_input, data): 
    #log.debug("parseTS_Adaptation")
    bs_input.append(BitField('Adaptation Field Length',		BIT_SIZE * 8))
    bs_input.append(BitField('Discontinuity indicator', BIT_SIZE * 1)) #defult 0xbd
    bs_input.append(BitField('Random Access indicator',		BIT_SIZE * 1))
    bs_input.append(BitField('Elementary stream priority indicator',		BIT_SIZE * 1))
    bs_input.append(BitField('PCR flag',		BIT_SIZE * 1))
    bs_input.append(BitField('OPCR flag',		BIT_SIZE * 1))
    bs_input.append(BitField('Splicing point flag',		BIT_SIZE * 1))
    bs_input.append(BitField('Transport private data flag',		BIT_SIZE * 1))
    bs_input.append(BitField('Adaptation field extension flag',		BIT_SIZE * 1))
    bs_input.set_array(data)
    adaptation_length = bs_input.field('Adaptation Field Length').value()
    if (adaptation_length > 0x1):
        bs_input.append(BitField('Adaptation Data',		BIT_SIZE * adaptation_length))
        #print bs_input
        

def changeTS_packet(packet_num):
    TS_file.Close()
    TS_file = file(filename, "wb")
    TS_file.seek(packet_num * 188)
    pack = TS_file.read(188)
    print ByteToHex(pack)
    
    
def main():
    # set debug level
    if (verbose):
        verbose_level = logging.DEBUG
    else:
        verbose_level = logging.INFO
    # Log everything, and send it to stderr.
    # create logger
    log = logging.getLogger("simple_example")
    log.setLevel(verbose_level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(verbose_level)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    log.addHandler(ch)

    log.debug("open file")
    TS_file = openTSFile('''C:\signaling\Xad_14_12.ts''')
    print TS_file
    SeekPacket(TS_file, 1577717)
    for i in range(1000000):
        pack = GetPakcet(TS_file, i)
        data = array.array('B', pack)
        #print len(pack)
        #print ByteToHex(pack)
        try:
            parseTS_Packet(data)
        except ValueError:
            pass
            #print i
            #print ByteToHex(pack)
    
if __name__ == "__main__":
	main()