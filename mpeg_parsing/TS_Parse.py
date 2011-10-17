#!/usr/bin/env python

import sys
import getopt
import os
import bitstring 

TS_PACKET_SIZE = 188
PID_TO_FIND = 0x905
PACKT_TO_START  = 1577717 + 790000  #1577717
PTS_TO_FIND = 8126837 #5426837
LAST_NULL = 0
STRAM_filename = '''C:\signaling\Xad_14_12.ts'''
def readPAT(pack):
    '''
    program_association_section() {
        table_id 8 uimsbf
        section_syntax_indicator 1 bslbf
        '0' 1 bslbf
        reserved 2 bslbf
        section_length 12 uimsbf
        transport_stream_id 16 uimsbf
        reserved 2 bslbf
        version_number 5 uimsbf
        current_next_indicator 1 bslbf
        section_number 8 uimsbf
        last_section_number 8 uimsbf
        for (i = 0; i < N; i++) {
            program_number 16 uimsbf
            reserved 3 bslbf
            if (program_number = = '0') {
                network_PID 13 uimsbf
            }
            else {
                program_map_PID 13 uimsbf
            }
        }
        CRC_32 32 rpchof
    }'''
    pat = {}
    pat['table_id'] = pack.readbytes(1).hex
    pat['section_syntax_indicator'] = pack.readbits(1).uint
    pack.advancebits(3)
    pat['section_length'] = pack.readbits(12).uint
    curPOS = pack.bitpos
    pat['transport_stream_id'] = pack.readbits(16).uint
    pack.advancebits(2)
    pat['version_number'] = pack.readbits(5).uint
    pat['current_next_indicator'] = pack.readbits(1).uint
    pat['section_number'] = pack.readbits(8).uint
    pat['last_section_number'] = pack.readbits(8).uint
    
    while pack.bitpos - curPOS < pat['section_length'] * 8:
        program = {} 
        program['program_number'] = pack.readbits(16).uint
        pack.advancebits(3)
        program['program_map_PID'] = hex(pack.readbits(13).reversebits().uint)
        print program
        
    #print pat
    #print pack
    return "this is pat "

def readField(t, size):
   return (t.bitpos, size, t.readbits(size).uint)
   
def chageField(pack, t, name, value):
   t.overwrite(bitstring.BitString(uint=value,length=pack[name][1]) ,pack[name][0])

def insertSplicePoint(packet_num):
    f = open(STRAM_filename, 'rb')
    
    f.seek(0, packet_num * TS_PACKET_SIZE)
    
    t = bitstring.BitString(data=f.read(188))
    f.close()
    
    print t.hex
    
    #read data and positions
    pack = {}
    pack['sync byte'] = readField(t, 8)
    pack['TEI'] = readField(t, 1)
    pack['PUSI'] = readField(t, 1)
    pack['Transport Priority'] = readField(t, 1)
    pack['PID'] = readField(t, 13)
    pack['Scrambling control'] = readField(t, 2)
    pack['Adaptation field exist'] = readField(t, 1)
    pack['Payload data exist'] = readField(t, 1)
    pack['Continuity counter'] = readField(t, 4)
    
    pack['Adaptation Field Length'] = readField(t, 8)
    pack['Discontinuity indicator'] = readField(t, 1)
    pack['Elementary stream priority indicator'] = readField(t, 1)
    pack['PCR flag'] = readField(t, 1)
    pack['OPCR flag'] = readField(t, 1)
    pack['Splicing point flag'] = readField(t, 1)
    pack['Transport private data flag'] = readField(t, 1)
    pack['Adaptation field extension flag'] = readField(t, 1)
    
    pack['splice countdown'] = readField(t, 8)
    
    #do changes
    chageField(pack, t, 'PID', PID_TO_FIND)
    
    chageField(pack, t, 'Adaptation field exist', 1)
    chageField(pack, t, 'Payload data exist', 0)
    
    chageField(pack, t, 'Adaptation Field Length', 0x2)
    chageField(pack, t, 'Discontinuity indicator', 0)
    chageField(pack, t, 'Elementary stream priority indicator', 0)
    chageField(pack, t, 'PCR flag', 0)
    chageField(pack, t, 'OPCR flag', 0)
    chageField(pack, t, 'Splicing point flag', 1)
    chageField(pack, t, 'Transport private data flag', 0)
    chageField(pack, t, 'Adaptation field extension flag', 0)
    
    chageField(pack, t, 'splice countdown', 0)
    
    print t.hex
    f = os.open(STRAM_filename, os.O_RDWR)
    os.lseek(f, packet_num * TS_PACKET_SIZE, 0)
    os.write(f, t.data)
    os.close(f)
    
def main():
    s = bitstring.BitString(filename = STRAM_filename )
    
    s.seekbyte(TS_PACKET_SIZE * PACKT_TO_START)
    
    for i in range(10000000):
        if s.peekbyte() == '0x47':
            t = s.readbytes(TS_PACKET_SIZE)
            pack = {}
            pack['sync byte'] = t.readbytes(1).hex
            pack['TEI'] = t.readbits(1).uint
            pack['PUSI'] = t.readbits(1).uint
            pack['Transport Priority'] = t.readbits(1).uint
            pack['PID'] = t.readbits(13).uint
            pack['Scrambling control'] = t.readbits(2).uint
            pack['Adaptation field exist'] = t.readbits(1).uint
            pack['Payload data exist'] = t.readbits(1).uint
            pack['Continuity counter'] = t.readbits(4).uint
            
            if pack['PID'] == 0x1FFF:
                #save last null position
                LAST_NULL = i+PACKT_TO_START
                
            if not pack['PID'] == PID_TO_FIND:
                continue 
                
            if pack['PID'] == 0:
                print readPAT(t)
                continue
               
            if pack['PUSI'] == 0x1:
                
                if pack['Adaptation field exist'] == 0x1:
                    adaptation = {}
                    adaptation['Adaptation Field Length'] = t.readbytes(1).uint
                    adaptation['Discontinuity indicator'] = t.readbits(1).uint
                    adaptation['Random Access indicator'] = t.readbits(1).uint
                    adaptation['Elementary stream priority indicator'] = t.readbits(1).uint
                    adaptation['PCR flag'] = t.readbits(1).uint
                    adaptation['OPCR flag'] = t.readbits(1).uint
                    adaptation['Splicing point flag'] = t.readbits(1).uint
                    adaptation['Transport private data flag'] = t.readbits(1).uint
                    adaptation['Adaptation field extension flag'] = t.readbits(1).uint
                    adaptation['data'] = t.readbytes(adaptation['Adaptation Field Length'] - 1).hex
                    
                   
                if pack['Payload data exist'] == 0x1:
                    ES_start_info = {}
                    
                    t.advancebytes(6)
                    '''ES_start_info['packet_start_code_prefix'] = t.readbytes(3).uint
                    ES_start_info['stream_id'] = t.readbytes(1).uint
                    ES_start_info['PES_packet_length'] = t.readbytes(2).uint'''
                    
                    t.advancebits(8)
                    '''ES_start_info['PES_fixed_value'] = t.readbits(2).uint
                    ES_start_info['PES_scrambling_control'] = t.readbits(2).uint
                    ES_start_info['PES_priority'] = t.readbits(1).uint
                    ES_start_info['data_alignment_indicator'] = t.readbits(1).uint
                    ES_start_info['copyright'] = t.readbits(1).uint
                    ES_start_info['original_or_copy'] = t.readbits(1).uint'''
                    
                    ES_start_info['PTS_DTS_flags'] = t.readbits(2).uint
                    t.advancebits(6)
                    '''ES_start_info['ESCR_flag'] = t.readbits(1).uint
                    ES_start_info['ES_rate_flag'] = t.readbits(1).uint
                    ES_start_info['DSM_trick_mode_flag'] = t.readbits(1).uint
                    ES_start_info['addtional_copy_info_flag'] = t.readbits(1).uint
                    ES_start_info['PES_CRC_flag'] = t.readbits(1).uint
                    ES_start_info['PES_extention_flag'] = t.readbits(1).uint'''
                    
                    if ES_start_info['PTS_DTS_flags'] == 0x2:
                        pts = bitstring.BitString(length=33)
                        t.advancebytes(1)
                        t.advancebits(4)
                        pts.overwrite( t.readbits(3) ) # 'PTS 32..30'
                        t.advancebits(1)
                        pts.overwrite( t.readbits(15) )# 'PTS 29..15'
                        t.advancebits(1)
                        pts.overwrite( t.readbits(15) )# 'PTS 14..0'
                        t.advancebits(1)
                        print "no:%i pid:%i pts:%i" % (i, pack['PID'], pts.uint)
                        if (pts.uint == PTS_TO_FIND):
                            print "found on packet no:" + str(i+PACKT_TO_START)
                            print pack
                            print adaptation
                            print pts.uint
                            print t.hex
                            break           
    
    del s
    print "end"
    print LAST_NULL
    insertSplicePoint( LAST_NULL )
    
if __name__ == "__main__":
	main()