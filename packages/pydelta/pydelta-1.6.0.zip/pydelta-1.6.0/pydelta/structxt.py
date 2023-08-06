def splitwithout(textin, spliton, start, end=""):
	"""
	Splits textin in a similar manner to textin.split(spliton), but ignoring
	spliton where it occurs between start and end markers. E.g. 
	'a,<b,c>' could be split into ['a', '<b,c>'], rather than ['a', '<b', 'c>'].
	
	If end is not specified, start is used as a toggle, e.g. for "quotation
	marks".
	"""
	outbits = []
	buf = ""
	if end == "":
		within = False
		while True:
			nextsplit = textin.find(spliton)
			nextinout = textin.find(start)
			if nextsplit == -1:
				outbits.append(textin)
				break
			elif (nextsplit < nextinout and not within) or (nextsplit > nextinout and within):
				buf += textin[:nextsplit]
				textin = textin[nextsplit+len(spliton):]
				outbits.append(buf)
				buf = ""
			else:
				buf += textin[:nextsplit]
				textin = textin[nextsplit:]
				
	else:
		within = 0
		while True:
			nextsplit = textin.find(spliton)
			nextin = textin.find(start)
			nextout = textin.find(end)
			if nextsplit == -1:
				outbits.append(textin)
				break
			if nextin == -1:
				nextin = len(textin) + 1
			if nextout == -1:
				nextout = len(textin) + 1
			if nextsplit < nextin and within == 0:
				buf += textin[:nextsplit]
				textin = textin[nextsplit+len(spliton):]
				outbits.append(buf)
				buf = ""
			elif nextsplit < nextin and nextsplit < nextout:
				buf += textin[:nextsplit+len(spliton)]
				textin = textin[nextsplit+len(spliton):]
			elif nextin < nextout:
				buf += textin[:nextin+len(start)]
				textin = textin[nextin+len(start):]
				within += 1
			else:
				buf += textin[:nextout+len(end)]
				textin = textin[nextout+len(end):]
				if within > 0:
					within -= 1
					
	return outbits