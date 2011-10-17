
def edcs_encode(number, debug=False):
	''' from wikipedia:  
	   1. Write it in binary.
	   2. Count the bits and write down that number of bits in binary (X).
	   3. Use the binary digit written in step 1 again, remove the leading bit and write down the remaining bits (Y).
	   4. Append the second binary digit (Y) to the first binary digit (X).
	   5. Count the bits written in step 2 (X), subtract 1 from that number and prepend that many zeros.
	
	>>>for i in range(17):
	>>>    print  i+1, edcs_encode(i+1)
	1 1
	2 0100
	3 0101
	4 01100
	5 01101
	6 01110
	7 01111
	8 00100000
	9 00100001
	10 00100010
	11 00100011
	12 00100100
	13 00100101
	14 00100110
	15 00100111
	16 001010000
	17 001010001
	'''
	from BitVector import BitVector
	# 1. Write it in binary.
	number_in_bits = BitVector( intVal = number)
	if debug: print "number_in_bits=", number_in_bits
	# 2. Count the bits and write down that number of bits in binary (X).
	x = len(str(number_in_bits))
	x_bit = BitVector( intVal = x)	
	if debug: print "x=", x, x_bit
	
	# 3. Use the binary digit written in step 1 again, 
	#   remove the leading bit and write down the remaining bits (Y). 
	if len(number_in_bits) > 1:
		y_bit = number_in_bits[1:]
		y = y_bit.intValue()
		if debug: print "y=",y,  y_bit
	else:
		y_bit = None
		
	#4. Append the second binary digit (Y) to the first binary digit (X).
	if y_bit is not None :
		out =  x_bit + y_bit
	else:
		out = x_bit
	if debug: print "out=", out
	#5. Count the bits written in step 2 (X), 
	#   subtract 1 from that number and prepend that many zeros.
	lead_zeros = len(str(x_bit)) - 1
	if debug: print "zeros=", lead_zeros
	out = BitVector(bitstring='0'*lead_zeros) + out
	 
	return out
	
def edcs_decode(bitstream):
	''' TODO:'''
	
	pass