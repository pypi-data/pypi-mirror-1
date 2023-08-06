#===========================================================================#
#                             PyDELTA                                       #
#                                                                           #
#                A General-Purpose Python Library for                       #
#        Reading Text Files in DELTA (DEscription Language for              #
#                          TAxonomy) Format                                 #
#                                                                           #
#                  Copyright 2008 Mauro J. Cavalcanti                       #
#                         maurobio@gmail.com                                #
#                                                                           #                  
#          Copyright 2010 Mauro J. Cavalcanti & Thomas Kluyver              #
#                  maurobio@gmail.com, takowl@gmail.com                     # 
#                                                                           #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program. If not, see <http://www.gnu.org/licenses/>.    # 
#                                                                           #
#   REVISION HISTORY:                                                       #
#    Version 1.00, 04 Aug 2008 - Initial implementation (Mauro Cavalcanti)  #
#    Version 1.50, 09 Feb 2010 - Substantial reworking (Thomas Kluyver)     #
#    Version 1.51. 21 Feb 2010 - Minor bug fixes (Thomas Kluyver)           # 
#    Version 1.52, 23 Feb 2010 - Improved split function (Thomas Kluyver)   #
#    Version 1.53, 24 Feb 2010 - Changes to demo program (Mauro Cavalcanti) #
#===========================================================================#
"""
This module reads and manipulates descriptive biological data stored
in the DELTA (DEscription Language for TAxonomy) format. For more details,
see:
http://www.delta-intkey.com/www/programs.htm

This is part of the FreeDELTA project:
http://freedelta.sourceforge.net/

===============
Usage example (uses grass genera example files):
import pydelta

Example = pydelta.tDelta("grass/chars", "grass/items", "grass/specs")
# One multistate character (char_type==CT['UM']), one numeric (CT['RN'])
print Example.chars[4].feature, Example.chars[4].states
print Example.chars[26].feature, Example.chars[26].unit

#Print their values out for each item that has them
for i, item in enumerate(Example.items):
	print ""
	print item.name
	if 4 in item.attributes:
		culm_state = item.attributes[4]
		if culm_state.isdigit(): # Some of them are "1/2", i.e. mixed.
			print " Culms:", culm_state, "(" + Example.chars[4].states[int(culm_state)-1] + ")"
		else:
			print " Culms:", culm_state
	if 26 in item.attributes:
		print " Spikelets", item.attributes[26], Example.chars[26].unit
"""
# For splitting strings while ignoring splitters within comments.
import structxt

#----- Character types
CT= {'UM':2, 'OM':3, 'IN':4, 'RN':5, 'TE':8}

#---- Extreme character values
EXTRVAL_LOW  = 1  # extreme low value
EXTRVAL_HIGH = 2  # extreme high value

#---- Special character values
VARIABLE = -999999
UNKNOWN  = -999998
NOTAPPLI = -999997

#----- CONFOR directives (can be "*TEXT" or "* TEXT", so check for the
#         * separately
showDirective   = "SHOW"
itemDirective   = "ITEM DESCRIPTIONS"
charDirective   = "CHARACTER LIST"
typeDirective   = "CHARACTER TYPES"
depDirective    = "DEPENDENT CHARACTERS"
cnoteDirective  = "CHARACTER NOTES"
cimgDirective   = "CHARACTER IMAGES"
timgDirective   = "TAXON IMAGES"
impvalDirective = "IMPLICIT VALUES"

#----- PANKEY directives
headingDirective = "HEADING"
altCharDirective = "CHARACTER DESCRIPTIONS"

#----- Delta character description class
class tCharDescr(object):
	"The description of a single character, including its unit or possible states."
	def __init__(self):
		self.feature = ""
		self.unit = ""
		self.states = []
		self.char_type = CT['UM']
		self.notes = ""
		self.images = []
		self.implicit = None # Will be replaced when an implicit value is read.

#----- Delta item description class
class tItemDescr(object):
	"The description of a single item, including its attributes (character states)."
	def __init__(self):
		self.name = ""
		self.comment = ""
		self.attributes = {}
		self.images = []
		self.charlist = None
		
	def get_val_or_implicit(self, char):
		"""
		Returns the value associated with this item for a given character
		number, or if this cannot be found, the implicit value. This will only
		work if the item has been linked to a tDeltaCharList (this occurs
		automatically when a suitable specifications file is parsed).
		"""
		if char in self.attributes:
			return self.attributes[char]
		return self.charlist[char].implicit

#===== tDeltaCharList ====================================================

class tDeltaCharList(list):
	"""
	A list of available characters, and possible states for each.
	Items can be retrieved using DELTA's 1-based indexing, so the first
	character is charlist[1], not charlist[0]. Negative indices work as
	normal, so charlist[-1] is the last item.
	
	Instantiate by passing in the filename. If a separate file of
	character notes is present, its name can be passed in to the argument
	cnotes_fname.
	
	If you don't want to parse the file when instantiating it, use the argument
	parse=False. The parse_characters (and parse_cnotes) method can then be
	called later.
	"""
	#----- Constructor
	def __init__(self, fname, cnotes_fname = None, parse = True): 
		self.fname = fname # name of Delta character list file
		self.cnote_fname = cnotes_fname
		self.fchars = None
		self.directives = []
		self.title = ""
		if parse: # immediate parsing indicator
			self.parse_characters()
			if cnotes_fname:
				self.parse_cnotes()
			
	#----- DELTA uses 1-based lists, so adjust to work with a 1-based list
	def __getitem__(self,ix):
		"Retrieve a single item using DELTA's 1-based index."
		if ix == 0:
			raise IndexError, "Use 1-based indexing for DELTA"
		elif ix > 0:
			return super(tDeltaCharList,self).__getitem__(ix-1)
		elif ix < 0:
			return super(tDeltaCharList,self).__getitem__(ix)
	
	def __getslice__(self,i,j):
		"Retrieve a slice using DELTA's 1-based index."
		if i > 0:
			i -= 1
		if j > 0:
			j -= 1
		return super(tDeltaCharList,self).__getslice__(i,j)
		
	#----- Parses the character list file and extracts the character and character state names
	def parse_characters(self):
		"""
		Parses the list of characters from the file. Only needs to be called
		externally if you specified parse=False when creating the character
		list, or if you want to reload the characters.
		"""
		self.fchars = open(self.fname, "r")
				
		#--- Reading loop
		while True:
			#--- Processing the line
			cline = self.fchars.readline()
			if not cline: break
			if not cline.strip(): 
				continue
			
			if cline[0] == '*':
				#--- Reading a directive
				self.directives.append(cline)
				
				if cline.find(showDirective) != -1:
					self.title = cline.partition(showDirective)[-1].strip()
				elif cline.find(charDirective) != -1:
					chardesc = ""
					while not chardesc: # Hook onto first item before looping
						chardesc = self.fchars.readline().strip()
					while True:
						cline = self.fchars.readline()
						if not cline: #EOF -add last item
							self.append(self.__read_character(chardesc))
							break
						cline = cline.strip()
						if not cline:
							continue #Blank line
							
						if cline[0] == "#": #Next item
							self.append(self.__read_character(chardesc))
							chardesc = cline
						else:   # Add line to current item.
							chardesc += " " +cline
							
		self.fchars.close()
		return True
		
	def parse_cnotes(self):
		"""
		Parses character notes from a separate, specified file, adding
		them to the appropriate characters.
		
		This is called automatically if a cnotes file is specified when creating
		a tDeltaCharList or tDelta object. If calling it manually, ensure that
		itemlist.cnote_fname is set beforehand.
		"""
		self.fcnotes = open(self.cnote_fname,"r")
		self.cnotedirectives = []
		
		#--- Reading loop
		while True:
			#--- Processing the line
			cline = self.fcnotes.readline()
			if not cline: break #EOF
			cline = cline.strip()
			if not cline: continue #Blank line
			
			if cline[0] == '*':
				#--- Reading a directive
				self.cnotedirectives.append(cline)
				
				if cline.find(cnoteDirective) != -1:
					cnotetxt = ""
					while not cnotetxt: # Hook onto first item before looping
						cnotetxt = self.fcnotes.readline().strip()
					while True:
						cline = self.fcnotes.readline()
						if not cline: #EOF -add last item
							charnum, note = self.__read_cnote(cnotetxt)
							self[charnum].notes = note
							break
						cline = cline.strip()
						if not cline:
							continue #Blank line
							
						if cline[0] == "#": #Next item
							charnum, note = self.__read_cnote(cnotetxt)
							self[charnum].notes = note
							cnotetxt = cline
						else:   # Add line to current item.
							cnotetxt += " " +cline
							
		self.fcnotes.close()
		return True
		
	
	#--- Methods returning character list information
	
	#----- Set or change the character list filename
	def set_filename(self, fname, parse):
		"""
		Change the file from which characters are read. Specify parse=False to
		keep the existing characters, otherwise it will load from the new file.
		"""
		if not self.fchars.closed:
			self.fchars.close()
		self.fchars = open(fname, "r")
		if parse:
			self.parse_characters()

	#----- Reads the feature of a character
	def __read_character(self, cline): 
		char = tCharDescr()
		cbits = structxt.splitwithout(cline,'/',start="<",end=">")
		#cbits = cline.split('/')
		char.feature = cbits[0][cbits[0].find('.')+1:].lstrip()
		if len(cbits) <= 3:
			char.char_type = CT['IN']
			if cbits[1]:
				char.unit = cbits[1].strip()
		else:
			for cstate in cbits[1:-1]:
				char.states.append(cstate[cstate.find('.')+1:].strip())
			char.char_type = CT['UM']
		# These character types may be overridden when a Specs file is read.
		
		return char
	
	#----- Reads a character note, returns it with the relevant character number
	def __read_cnote(self,cnotetxt):
		bits = cnotetxt.partition(". ")
		num = int(bits[0].strip('# '))
		return (num, bits[2])

#===== tDeltaItemList ========================================================

class tDeltaItemList(list):
	"""
	A list of items (e.g. species). Individual items can be retrieved using
	DELTA's 1-based indexing (i.e. the first item is itemlist[1], not itemlist[0]).
	
	Instantiate simply by passing it the filename to use. If you don't want
	it to parse the file straight away, use the argument parse=False. The
	parse_items method can then be used later.
	"""
	#----- Constructor
	def __init__(self, fname, parse = True): 
		self.fname = fname # name of Delta items file
		self.fitems = None
		self.directives = []
		self.title = ""
		if parse: # immediate parsing indicator
			self.parse_items()
		
	#----- Parses the items list file and extracts the item names and taxon attributes
	def parse_items(self):
		"""
		Parse the list of items from the file. Only needs to be called
		externally if you specified parse=False when creating the item list,
		or if you want to reload the items from file.
		"""
		#--- Open the items file
		self.fitems = open(self.fname, "r")
		
		i = 0
		while True:
			#--- Processing the line
			cline = self.fitems.readline()
			if not cline: break
			if not cline.strip(): 
				continue
			if cline[0] == '*':
				#--- Reading a directive
				self.directives.append(cline)

				if cline.find(showDirective) != -1:
					self.title = cline.partition(showDirective)[-1].strip()
				elif cline.find(itemDirective) != -1:
					itemdesc = ""
					while not itemdesc: # Hook onto first item before looping
						itemdesc = self.fitems.readline().strip()
					while True:
						cline = self.fitems.readline()
						if not cline: #EOF -add last item
							self.append(self.__read_item(itemdesc))
							break
						if not cline.strip():
							continue #Blank line
							
						if cline.strip()[0] == "#": #Next item
							self.append(self.__read_item(itemdesc))
							itemdesc = cline.strip()
						else:   # Add line to current item.
							itemdesc += " " + cline.strip()
					
		self.fitems.close()
		return True
	
	#--- Methods returning item list information
	
	#----- Set or change the item list filename
	def set_filename(self, fname, parse=True):
		"""
		Change the file from which items are read. Specify parse=False to keep
		the existing items, otherwise it will load from the new file.
		"""
		if not self.fitems.closed:
			self.fitems.close()
		self.fname = fname
		self.fitems = open(fname, "r")
		if parse:
			self.parse_items()
	
	#----- DELTA uses 1-based lists, so adjust to work with a 1-based list
	def __getitem__(self,ix):
		"Retrieve single items using DELTA's 1-based index."
		if ix == 0:
			raise IndexError, "Use 1-based indexing for DELTA"
		elif ix > 0:
			return super(tDeltaItemList,self).__getitem__(ix-1)
		elif ix < 0:
			return super(tDeltaItemList,self).__getitem__(ix)
			
	def __getslice__(self,i,j):
		"Retrieve a slice using DELTA's 1-based index."
		if i > 0:
			i -= 1
		if j > 0:
			j -= 1
		return super(tDeltaItemList,self).__getslice__(i,j)
	
	#----- Reads an item
	def __read_item(self, cline):
		#-- Is given a line starting with #, and reads an item
		item = tItemDescr()
		cline = cline.strip('\t\n #')

		item = tItemDescr()
		item.name, dummy, attrlst = cline.partition('/')
		item.comment = item.name[item.name.find('<'):]
		item.attributes = extract_attributes(attrlst)
		return item

#===== Delta specifications =============================================

class tDeltaSpecs(object):
	"""
	Optional database specifications from a DELTA specs file.
	
	Instantiate by passing it the file name, and the already-constructed
	tDeltaCharList and tDeltaItemList objects for the database.
	
	If you don't want to parse the file yet, use the parse=False argument. The
	parse_specs method can then be called later.
	"""
	#----- Constructor
	def __init__(self, fname, chars, items, parse = True):
		self.fname = fname # name of Delta specs file
		self.fspecs = None
		self.directives = []
		self.title = ""
		if parse: # immediate parsing indicator
			self.parse_specs(chars)
		
		# Link items to the character list so that they can look up implicit
		# values. This creates references, not copies!
		for item in items:
			item.charlist = chars
	
	#----- Parse the specifications file
	def parse_specs(self, char_list):
		"""
		Parse the specifications from file. This only needs to be called externally
		if you specified parse=False when creating the object, or if you want to
		reload the specifications from file.
		"""
		#--- Open the items file
		self.fspecs = open(self.fname,"r")
		
		while True:
			cline = self.fspecs.readline()
			if not cline: break #End of file
			cline = cline.strip()
			if not cline: continue # Blank line
			
			if cline[0] == '*':
				#--- Reading a directive
				self.directives.append(cline)
				if cline.find(showDirective) != -1:
					self.title = cline.partition(showDirective)[-1].strip()
				elif cline.find(typeDirective) != -1:
					#--- Parse and read in the character types
					self.__parse_char_types(char_list, cline) 
				elif cline.find(impvalDirective) != -1:
					#-- Reading implicit values
					self.__parse_implicit_values(char_list, cline)
				##elif cline.find(depDirective) != -1:
					#--- Reading dependent characters (not yet implemented)
					##self.__parse_char_dependencies(char_list, cline)
		self.fspecs.close()
		return True
	
	#----- Set or change the specifications filename
	def set_filename(self, fname, parse=True):
		"""
		Change the file from which specifications are read. Specify parse=False to
		keep the existing specifications, otherwise it will load from the new file.
		"""
		if not self.fspecs.closed:
			self.fspecs.close()
		self.fname = fname
		self.fspecs = open(fname, "r")
		if parse:
			self.parse_specs()
	
	#----- Retrieves the number of dependent characters
	#----- for a given control character and state
##	def get_depchar_nb(self, ccnum, ccstate): 
##		pass
	
	#----- Retrieves a dependent character (in 'rank' position)
	#----- for a given control character and state 
##	def get_depchar(self, ccnum, ccstate, rank): 
##		pass
	
	#----- Test if a character is dependent from
	#----- a given control character and state
##	def is_dependent(self, dcnum, ccnum, ccstate): 
##		pass
	
	# Protected member functions

	#----- Parses "CHARACTER TYPES" directive
	def __parse_char_types(self, char_list, cline):	
		
		#--- If EOL reached, continue at next line
		next_line = self.fspecs.readline().strip()
		while next_line:
			cline += " " + next_line
			next_line = self.fspecs.readline().strip()
			
		ctypes = cline.partition(typeDirective)[-1].split()
		for ctype in ctypes: 
			laux = ctype.split(',')
			
			#--- Store character type
			if laux[0].find('-') != -1: 
				chars = expand_range(laux[0])
				for charnum in chars:
					char_list[charnum].char_type = CT[laux[1]]
			else:
				char_list[int(laux[0])].char_type = CT[laux[1]]
		return
	
	#----- Parses "IMPLICIT VALUES" directive
	def __parse_implicit_values(self, char_list, cline):
		next_line = self.fspecs.readline().strip()
		while next_line:
			cline += " " + next_line
			next_line = self.fspecs.readline().strip()
		
		cline = cline.partition("VALUES ")[2]
		impvals = extract_attributes(cline)
		for k, v in impvals.items():
			char_list[k].implicit = v
		return True
	
	#----- Parses "DEPENDENT CHARACTERS" directive
##	def __parse_char_dependencies(self, char_list, cline):
##		pass


#===== tDelta ============================================================
class tDelta(object):
	"""
	An entire DELTA database, consisting of a list of characters (pass as
	chars_fname), a list of items (typically species or other taxa; pass as
	items_fname), and two optional files: a set of specifications for the
	database (pass as specs_fname) and a list of notes for specific characters
	(pass as cnotes_fname).
	
	Once set up, the data is accessible in .items and .chars
	"""
	#----- Constructor
	def __init__(self, chars_fname, items_fname,\
			specs_fname = None, cnotes_fname=None, parse=True):
		self.chars = tDeltaCharList(chars_fname, cnotes_fname, parse)
		self.items = tDeltaItemList(items_fname, parse)
		if specs_fname:
			self.specs = tDeltaSpecs(specs_fname, self.chars, self.items)

#===== Miscellaneous =====================================================

#----- Remove comments (delimited by < >) from a string
def remove_comments(src):
	"Returns the part of a DELTA source line before any <comment>."
	left = src.find('<')
	return src[:left]

#----- Extracts comments from src string
def extract_comment(src):
	"Returns only the <comment> from a DELTA file source line."
	left = src.find('<')+1
	right = src.find('>')
	return src[left:right]

#----- Expands a character range and returs a list of character numbers
def expand_range(src):
	"Turns a range '4-7' into a list [4,5,6,7]; used in parsing DELTA files."
	nchar = []
	if len(src) > 0:
		pos = src.find('-')
		if pos != -1:
			first = int(src[:pos])
			last  = int(src[pos+1:])
		for j in range (first, last+1): 
			nchar.append(j)
		return nchar
		
def extract_attributes(attrlst):
	"""
	Processes a DELTA attribute list (for an item, or in the specs, e.g. for
	implicit values). Returns a dictionary of the attributes.
	"""	
	# We need to add a space so that it 'sees' the last value pair.
	attrlst += " "
	buf = ""
	attribs = {}
	inComment = 0
	i = 0
	for i in range(len(attrlst)):
		#--- Blank (separator) --> end of the current attribute
		if (attrlst[i] == ' ') and (not inComment):	# blanks in comment are ignored
			if not buf.strip(): # ignore blank lines
				continue
			
			temp = remove_comments(buf)
			if temp.count(',') == 1:
				aux, dummy, value = buf.partition(",")			
			else:
				aux = buf[:buf.find('<')]
				if aux:
					value = buf[buf.find('<'):]
			aux = aux.strip()
		
			#--- Store attribute
			if aux.find('-') != -1: 
				chars = expand_range(aux)
				for charnum in chars:
					attribs[charnum] = value
			else:
				attribs[int(aux)] = value
			buf = ""
											
		#--- Other characters (comments included) are copied into the buffer
		else:
			if attrlst[i] == '<':   # comment begin (nested comments do occur)
				inComment += 1
			elif attrlst[i] == '>' and inComment > 0:   # comment end
				inComment -= 1
		buf += attrlst[i]
	return attribs
	
#=== Test section (not run if imported as a module) ============================

if __name__ == '__main__':
	import os
	import os.path
	
	#--- Creates CharList, ItemList and Specs objects and parses the
	#    corresponding text files ----------------------------------------------
	#--- Defaults to Grass sample data -----------------------------------------
	Example = tDelta("grass/chars", "grass/items", "grass/specs")
	print Example.items.title
	print Example.chars.title
	print Example.specs.title
	print len(Example.items), "items, ", len(Example.chars), "characters"
	
	#--- Displays header -------------------------------------------------------
	print
	print "=================="
	print "Free Delta Project"
	print "=================="
	print "Test of PyDelta class"
	print
	stop = False
	while not stop:
		#--- Menu ----------------------------------------------------------------
		print "1. Character list"
		print "2. Retrieve a character"
		print "3. Item list"
		print "4. Retrieve an item"
		print "5. Specifications"
		print "6. Change dataset"
		print "9. Exit"
		choice = raw_input("Your choice : ")
		opt = int(choice)
		if opt == 1 : #----- Displays all characters features --------------------
			print "CHARACTERS LIST :" 
			for i, char in enumerate(Example.chars):
				print i+1, ": ", char.feature
			print "*** ", len(Example.chars), " characters ***"
			print
		elif opt == 2: #----- Displays information about one character ------------
			choice = raw_input("Enter character number to retrieve : ")
			opt = int(choice)
			if (opt < 1) or (opt > len(Example.chars)):
				print "Invalid character number"
			else:
				#--- Character type
				print "Type : ",
				if Example.chars[opt].char_type == CT['UM']:
					print "unordered multistate"
				elif Example.chars[opt].char_type == CT['OM']:
					print "ordered multistate"
				elif Example.chars[opt].char_type == CT['IN']:
					print "integer numeric"
				elif Example.chars[opt].char_type == CT['RN']:
					print "real numeric"
				elif Example.chars[opt].char_type == CT['TE']:
					print "text/comment"
				#--- Feature
				print "Feature : ", Example.chars[opt].feature
				#--- State list or unit
				if Example.chars[opt].char_type in (CT['UM'], CT['OM']):
					for j,state in enumerate(Example.chars[opt].states):
						print "State",j+1,": ",state
				else:
					if Example.chars[opt].char_type in (CT['IN'], CT['RN']):	
						print "Unit : ", Example.chars[opt].unit
			print
		elif opt == 3: #----- Displays all items names -------------------------
			print "ITEMS LIST :"
			for i, item in enumerate(Example.items):
				print i+1, ": ", item.name
			print "*** ", len(Example.items), " items ***"
			print
		elif opt == 4: #----- Displays information about an item ---------------
			choice = raw_input("Enter item number to retrieve : ")
			opt = int(choice)
			if (opt < 1) or (opt > len(Example.items)):
				print "Invalid item number"
			else:
				print "Item name : "
				print "  ", Example.items[opt].name
				print "Attributes : "
				for key in Example.items[opt].attributes:
					print "%s: %s" % (key, Example.items[opt].attributes[key])
			print
		elif opt == 5: #----- Displays specification file content --------------
			print Example.specs.directives
		elif opt == 6: #----- Change dataset -----------------------------------
			print
			dir = raw_input("Enter path name of the new dataset : ")
			if os.path.exists(dir):
				os.chdir(dir)
				Example = tDelta("chars", "items", "specs")
				print Example.items.title
				print Example.chars.title
				print Example.specs.title
				print len(Example.items), "items, ", len(Example.chars), "characters"
				print
			else:
				print "*** ERROR: Path", dir, "not found!"
		elif opt == 9: #----- Exit ---------------------------------------------
			print "-- done --"
			stop = True
