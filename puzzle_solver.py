import cv2
from sklearn.metrics.pairwise import pairwise_distances
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import structural_similarity as ssim
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import math
import pickle
from time import sleep

# Constants
PWDTH = 118
PHIGT = 118             # 289, 24 -- 236, 65
SPACE = 10
# Globals
pccords = []
mtrc = ""	
shwimg = None
#---------------------------
# Data definitions
#
class Slice:
	def __init__(self, start, end, whites):
		self.start = start
		self.end   = end
		self.wts   = whites
		self.size = end - start
		
	# Slice, Slice -> 0, 1, 2
	# produce 	0 -> if second slice is higher than first slice
	#			1 -> if second slice is at level with first slice
	#			2 -> if second slice is lower than first slice
	
	def pos_relation(self, sb):
		sdif = self.start - sb.start
		edif = self.end - sb.end
		
		if sdif > 5 or edif > 5:
			return 0
		if sdif < -5 or edif < -5:
			return 2
		else:
			return 1
	
	def pos_relation_mod(self, sb):
		sdif = self.start - sb.start
		edif = self.end - sb.end
		
		if self.start == 0 or self.end == 117:
			return 1
			
		if sdif > 12 or edif > 12:
			return 0
		if sdif < -12 or edif < -12:
			return 2
		else:
			return 1
			
			
	def fuzzy_match(self, sb):
		sdif = abs(self.start - sb.start)
		edif = abs(self.end - sb.end)
		
		#!!!
		return 1 + (10 /(sdif + edif + 1))
#
# Slice is Slice(Number, Number, Number)
# Interp. represent a part of a side of a puzzle piece where start and end are
#			where the slice starts and ends.
#			Number -> is the start index of the slice in a side
#			Number -> is the end   index of the slice in a side
#			Number -> is the number of white spaces in a slice
#
S1 = Slice(40, 100, 20)
#
"""
def fn-for-slice(s):
	...(s.start)
	...(s.end)
	...(s.size)			# Size is Number -> represent size of slice
	...(s.wts)
"""
# Template rules used :
# - Atomic non-distinct : Number
# - Atomic non-distinct : Number 
# - Atomic non-distinct : Number
# - Atomic non-distinct : Number
#
#---------------------------------------------------
#
class Piece:
	def __init__(self, id, left, top, right, bottom):
		self.id = id
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom
#
#
# Piece is Piece(Number, List of 118 Number, List of 118 Number, List of 118 Number, List of 118 Number)
# Interp. represents image piece in puzzle where :
#				Number 			   -> is the number of the piece in the grid
#				List of 118 Number -> is left side row with each number representing the B color grade of pixel
#				List of 118 Number -> is top side row with each number representing the B color grade of pixel
#				List of 118 Number -> is right side row with each number representing the B color grade of pixel
#				List of 118 Number -> is bottom side row with each number representing the B color grade of pixel
#
P1 = Piece(0, [], [], [], []) # examples can't fit due to large amount of numbers
"""
def fn_for_piece(p):
	...(p.id)
	for pixel in p.left:
		...(pixel)
	for pixel in p.top:
		...(pixel)
	for pixel in p.right:
		...(pixel)
	for pixel in p.bottom:
		...(pixel)
"""
# Template rules used :
# - Atomic non-distinct : Number
# - Each of -> 118 Atomic non-distinct : Number
# - Each of -> 118 Atomic non-distinct : Number
# - Each of -> 118 Atomic non-distinct : Number
# - Each of -> 118 Atomic non-distinct : Number
#
#
#-------------------------------------------------
def reduce(fn, lst):
	acm = lst[0]
	for a in lst[1:]:
		acm = fn(acm, a)
		
	return acm
# Function definitions
#
# BGR image -> List of 6 Pieces
# given a screenshot find puzzle pieces and form each into a Piece
#
def puzzle_to_piece(img):
	# BGR img -> (Number, Number)
	# find the location of "Skill Check" text label in image
	#
	def find_puzzle_cords(img):
		method = cv2.TM_SQDIFF_NORMED
		
		title = cv2.imread('title.png')
		result = cv2.matchTemplate(title, img, method)
		# We want the minimum squared difference
		mn,_,mnLoc,_ = cv2.minMaxLoc(result)
		# Extract the coordinates of our best match
		MPx,MPy = mnLoc
		
		return (MPx - 53, MPy + 41)
		
	
	# List of 6 (Number, Number), BGR image -> List of 6 List of 4 List of 118 Number
	# read all the Blue pixel color in given image which belongs to each side of piece
	# 	with the help of each piece cordinations and return each side Blue pixel color.
	def get_pixels(lopcrd, img):
		lololons = []
		for p in lopcrd:
			left = img[p[1]:p[1]+118, p[0]:p[0]+1].reshape(1, -1)
			top = img[p[1]:p[1]+1, p[0]:p[0]+118].reshape(1, -1)
			right = img[p[1]:p[1]+118, p[0]+117:p[0]+118].reshape(1, -1)
			bottom = img[p[1]+117:p[1]+118, p[0]:p[0]+118].reshape(1, -1)
			
			
			lololons.append((left, top, right, bottom))
		
			
		return lololons
	
	# List of 6 List of 4 List of 118 Number -> List of 6 Piece
	#  make each pixel color info list into it's own Piece object
	def pixel_to_piece(lololons):
		pieces = []
		for i in range(0, 6):
			pieces.append(Piece(i, lololons[i][0], lololons[i][1], lololons[i][2], lololons[i][3]))
		
		return pieces
		
		
	(x, y) = find_puzzle_cords(img)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# first row
	p0 = (x                    , y)
	p1 = (x + PWDTH + SPACE    , y)
	p2 = (p1[0] + PWDTH + SPACE, y)
	# second row
	p3 = (x    , y + PHIGT + SPACE)
	p4 = (p1[0], p3[1])
	p5 = (p2[0], p3[1])
	
	
	pcs_crds = [p0, p1, p2, p3, p4, p5]
	global pccords
	pccords = pcs_crds
	
	
	#timg1 = img[p0[1]:p0[1]+117, p0[0]:p0[0]+117]
	#timg2 = img[p1[1]:p1[1]+117, p1[0]:p1[0]+117]
	#timg3 = img[p2[1]:p2[1]+117, p2[0]:p2[0]+117]
	#timg4 = img[p3[1]:p3[1]+117, p3[0]:p3[0]+117]
	#timg5 = img[p4[1]:p4[1]+117, p4[0]:p4[0]+117]
	#timg6 = img[p5[1]:p5[1]+117, p5[0]:p5[0]+117]
	#row1 = np.hstack((timg1, timg2, timg3))
	#row2 = np.hstack((timg4, timg5, timg6))
	#full = np.vstack((row1, row2))
	#cv2.imshow("puzzle", full)
	#cv2.waitKey(0)


	pieces = pixel_to_piece(get_pixels(pcs_crds, img))
	
	return pieces
	

	
# List of 6 Piece -> String
# find the best orientation for given pieces
def best_match(pcs, shwornt=""):
	best_score = -100000000
	orientation = shwornt
	
	lopcscr = match(pcs)
	lopcscr.sort(key=lambda ps: ps[1], reverse=True)
	n = 0
	scores = {}
	for i in range(0, 200):
		lopcscr[i][1] = [lopcscr[i][1]]
		#print(i, tuple(map(lambda x: x.id, lopcscr[i][0])), lopcscr[i][1])
		#if shwornt != "" and tuple(map(lambda x: x.id, lopcscr[i][0])) == tuple(map(int, shwornt.split(","))): print("---------------------------------------")
		lopcscr[i][1].append(normalize(lopcscr[i][0]))
		#"2,5,4,0,1,3"
		
	del lopcscr[200:]
	#lopcscr.sort(key=lambda ps: ps[1][2] + ps[1][3], reverse=True)
	
	lopcscr.sort(key=lambda ps: ps[1][1], reverse=True)
	top = lopcscr[0][1][1]
	for i in range(0, 200):
		lopcscr[i][1].append(hand_pick(lopcscr[i][0]))
		if lopcscr[i][1][1] < (top - 50) or i == 120:
			del lopcscr[i:]
			break
	
	#lopcscr.sort(key=lambda ps: ps[1][2], reverse=True)
	#del lopcscr[35:]
	#lopcscr.sort(key=lambda ps: ps[1][0] + (ps[1][2] * 8), reverse=True)
	#del lopcscr[40:]
	#lopcscr.sort(key=lambda ps: ps[1][2], reverse=True)
	#del lopcscr[-1]
	#lopcscr.sort(key=lambda ps: ps[1][0] + (ps[1][2] * 60), reverse=True)
	#del lopcscr[-1]
	
	
	for pcscr in lopcscr:
		#pcscr[1][0] = mean_metric(pcscr[0])
		#pcscr[1][1] = anti_match(pcscr[0]) * 60
		del pcscr[1][2]
	#	
	#lopcscr.sort(key=lambda ps: ps[1][0] + ps[1][1], reverse=True)
	#del lopcscr[90:]
	### #
	for pcscr in lopcscr:
		pcscr[1][0] = pcscr[1][0]
		pcscr[1][1] = calc_score(pcscr[0], "correlation") * 100
		pcscr[1].append(pcscr[1][1] / 100)
		pcscr[1].append(hand_pick(pcscr[0]))
		pcscr[1].append(normalize(pcscr[0]) * 5)
		pcscr[1].append(calc_score(pcscr[0], "cosine") * 100)
		pcscr[1].append(exprmnt101(pcscr[0]))
	#
	#lopcscr.sort(key=lambda ps: ps[1][5], reverse=True)
	#lopcscr.sort(key=lambda ps: ps[1][0] + ps[1][2] + ps[1][4], reverse=True)
	
	#del lopcscr[35:]
	lopcscr.sort(key=lambda ps: ps[1][0] + (ps[1][3] * 7) + (ps[1][6] * 2) + (ps[1][5] * 500), reverse=True)
	#del lopcscr[60:]
	#del lopcscr[10:]
	# diff = abs(abs(lopcscr[0][1][1]) - abs(lopcscr[1][1][1]))
	# hpdif = abs(lopcscr[0][1][2] - lopcscr[1][1][2])
	# nmdif = abs(abs(lopcscr[0][1][3]) - abs(lopcscr[1][1][3]))
	# exdif = abs(lopcscr[0][1][5] - lopcscr[1][1][5])
	
	# if diff < 5 and (hpdif < 6 and hpdif > 1):
		# print("in 1")
		# lopcscr.sort(key=lambda ps: ps[1][1], reverse=True)
	# elif (diff < 22 and hpdif < 20 and nmdif < 6) or \
		 # (diff < 1 and hpdif < 1 and nmdif < 26):
		# print("in 2")
		# lopcscr.sort(key=lambda ps: ps[1][4], reverse=True)
		# lopcscr[0][1][4] -= 0.3
		# lopcscr.sort(key=lambda ps: ps[1][4], reverse=True)
	# else:
		# lopcscr.sort(key=lambda ps: ps[1][1], reverse=True)
		# top1 = lopcscr[0]
		# lopcscr.sort(key=lambda ps: ps[1][2], reverse=True)
		# top2 = lopcscr[0]
		# lopcscr.sort(key=lambda ps: ps[1][3], reverse=True)
		# top3 = lopcscr[0]
		# lopcscr.sort(key=lambda ps: ps[1][4], reverse=True)
		# top4 = lopcscr[0]
		# lopcscr.sort(key=lambda ps: ps[1][0], reverse=True)
		# top5 = lopcscr[0]
		# if (top1 == top2 == top3 == top4) and hpdif < 15 and exdif < 1000:
			# print("in 3a")
			# lopcscr.sort(key=lambda ps: ps[1][0], reverse=True)
		# elif (top1 == top2 == top3 == top4 == top5) and nmdif > 115:
			# print("in 3fuckthisshit")
			# lopcscr.sort(key=lambda ps: ps[1][5], reverse=True)
		# else:	
			# print("in 3b")
			# lopcscr.sort(key=lambda ps: ps[1][1] + ps[1][2] + ps[1][3], reverse=True)
			
	#del lopcscr[-1]
	
	# top = lopcscr[0][1][2]
	# for pcscr in lopcscr:
		# if pcscr[1][2] < (int(top) - 25) or lopcscr.index(pcscr) > 9:
			# del lopcscr[lopcscr.index(pcscr):]
			# break
	#
	#lopcscr.sort(key=lambda ps: ps[1][0], reverse=True)
	#del lopcscr[2:]
	#lopcscr.sort(key=lambda ps: ps[1][2], reverse=True)
	pack = np.empty((len(lopcscr), 83544))
	i = 0
	for pcscr in lopcscr:
		pack[i] = getData(pcs_to_ornt(pcscr[0]))
		i += 1
		#print(i - 1, tuple(map(lambda x: x.id, pcscr[0])), pcscr[1])
		#showResult(pcs_to_ornt(lopcscr[i][0]))
		if shwornt != "" and tuple(map(lambda x: x.id, pcscr[0])) == tuple(map(int, shwornt.split(","))): 
			print("---------------------------------------")
	
	result = knn.predict(pack)
	#print(result)
	n = np.where(result == "Correct")[0][0]
	#print(n)
	orientation = pcs_to_ornt(lopcscr[n][0])
	
		
	return orientation
	"""
	for (ornt, score) in match(pcs):
		if score > best_score:
			best_score = score
			orientation = ornt
			print(ornt, "->", score)
		#if ornt == '345012':
			#print("***", ornt, "->", score)
	"""
	
	return orientation
	

def exprmnt101(lop):
	def hisham_metric(la, lb):
		score = 0
		def isdark(p):
			return p <= 160
		def islight(p):
			return p > 160
		
		
		
		started = False
		closing = False
		counter = 0
		for i in range(0, 118):
			for n in range(0, 6):
				if isdark(la[0][i]) and ((((i+n) < 118) and (isdark(lb[0][i+n]))) or \
									(((i-n) >   0) and (isdark(lb[0][i-n])))):
					if started and closing:
						closing = False
						score += counter * 8		# (100 / counter) * 10 or 12.8
						counter = 0
					else:
						started = True
					
				elif islight(la[0][i]) and islight(lb[0][i]):
				#((((i+n) < 118) and (islight(lb[0][i+n]))) or \						old logic
				#					    (((i-n) >   0) and (islight(lb[0][i-n]))))
					if started:
						closing = True
						if counter == 65:			# 65 or 75
							counter = 0
							closing = False
							score -= 65
						else:
							counter += 1
		

		return score
	
	score = 0
	score += hisham_metric(lop[0].right , lop[1].left)
	score += hisham_metric(lop[0].bottom, lop[3].top)
	score += hisham_metric(lop[1].bottom, lop[4].top)
	score += hisham_metric(lop[1].right , lop[2].left)
	score += hisham_metric(lop[2].bottom, lop[5].top)
	score += hisham_metric(lop[3].right , lop[4].left)
	score += hisham_metric(lop[4].right , lop[5].left)
		
	return score


def isdark(p):
	return p <= 160
def islight(p):
	return p > 160

def mean_metric(lop, opt=0):
	def aux(la, lb):
		if opt == 0:
			return -mse(la, lb)
		elif opt == 1:
			return ssim(la[0], lb[0])
		else:
			print("UNKNOWN OPTION RETURNED 0 RESULT")
			return 0



	score = 0

	score += aux(lop[0].right , lop[1].left)
	score += aux(lop[0].bottom, lop[3].top)
	score += aux(lop[1].bottom, lop[4].top)
	score += aux(lop[1].right , lop[2].left)
	score += aux(lop[2].bottom, lop[5].top)
	score += aux(lop[3].right , lop[4].left)
	score += aux(lop[4].right , lop[5].left)
	
	return score
			
def get_slices(sidea, sideb):
	def next_slice(side, index, start=-1, wts=0, end=-1, extwts=0):
		if index == 117:
			if start != -1 and end == -1:
				if wts > 24:
					return (None, 117)
				else:
					return (Slice(start, 117, wts), 117)
			elif start != -1 and end != -1:
				if extwts == 0:
					return (Slice(start, 117, wts), 117)
				else:
					return (Slice(start, end, wts), end)
			else:
				return (None, 117)
		else:
			if start != -1 and end == -1:
				if isdark(side[index]):
					if wts == 0:
						return next_slice(side, index + 1, start)
					else:
						return next_slice(side, index + 1, start, wts, index, 0)
				else:
					if wts > 23:
						return (None, index)
					else:
						return next_slice(side, index + 1, start, wts + 1)
			elif start != -1 and end != -1:
				if extwts > 24:
					return (Slice(start, index - extwts - 1, wts), index)
				else:
					if isdark(side[index]):
						if extwts != 0:
							return (Slice(start, end, wts), end)
						else:
							return next_slice(side, index + 1, start, wts, end, extwts)
					else:
						return next_slice(side, index + 1, start, wts, end, extwts + 1)
			elif start == -1 and end == -1:
				if isdark(side[index]):
					return next_slice(side, index + 1, index, 0)
				else:
					return next_slice(side, index + 1, start, 0)
			else:
				print("ERROR! slice ended before it starts")
				return (None, index)
				
		
		
	aindex = 0
	bindex = 0
	aslices = []
	bslices = []
	while aindex != 117 or bindex != 117:
		aslice, aindex = next_slice(sidea, aindex)
		bslice, bindex = next_slice(sideb, bindex)
		
		
		if aslice is not None: aslices.append(aslice)
		if bslice is not None: bslices.append(bslice)
	
	#if test != 0:
	#	for s in aslices:
	#		print("[", s.start, "->", s.end, "|","whites :", s.wts, "]")
	#		None
			
	return (aslices, bslices)
			
def anti_match(lop, test=0):
	def antimtch_metric(la, lb):
		score = 0	
				
		def closely_match(sa, los):
			matched = False
			mscore = 0
			cs = None
			if sa.size > 18:
				return 0
			for sb in los:
				cs = sb
				pr = sa.pos_relation_mod(sb)
				
				if   pr == 0:
					continue
				elif pr == 1:
					del los[0:los.index(sb)+1]
					matched = True
					mscore = 0
					if test != 0: print("[", sa.start, "->", sa.end, "]", "Matched with", "[", sb.start, "->", sb.end, "]")
					break
				elif pr == 2:
					break
					
			if not matched:
				if test != 0: print("[", sa.start, "->", sa.end, "]", "didn't match any slice")
				if cs is None:
					if test != 0: print("no close slice found")
					mscore = sa.wts
				else:
					if test != 0: print("closest was", "[", cs.start, "->", cs.end, "]")
					ci = los.index(cs)
					laste  = (los[(los.index(cs) - 1)].end if ci > 0 else sa.start)
					firsts = cs.start
					mscore = (laste - sa.start if (laste - sa.start) > (sa.end - firsts) else sa.end - firsts)
			
			return (mscore if matched else -mscore)
			

		losa, losb = get_slices(la[0], lb[0])
		closa, closb = losa.copy(), losb.copy()
			
		for sa in losa:
			score += closely_match(sa, closb)
			
		if test != 0: print("----------------Side B------------------")
		
		for sb in losb:
			score += closely_match(sb, closa)
		
		
		return score
	
	
	score = 0
	if   test == 17:
		score += antimtch_metric(lop[0].right , lop[1].left)
	elif test == 18:
		score += antimtch_metric(lop[0].bottom, lop[3].top)
	elif test == 19:
		score += antimtch_metric(lop[1].bottom, lop[4].top)
	elif test == 20:
		score += antimtch_metric(lop[1].right , lop[2].left)
	elif test == 21:
		score += antimtch_metric(lop[2].bottom, lop[5].top)
	elif test == 22:
		score += antimtch_metric(lop[3].right , lop[4].left)
	elif test == 23:
		score += antimtch_metric(lop[4].right , lop[5].left)
	else:
		score += antimtch_metric(lop[0].right , lop[1].left)
		score += antimtch_metric(lop[0].bottom, lop[3].top)
		score += antimtch_metric(lop[1].bottom, lop[4].top)
		score += antimtch_metric(lop[1].right , lop[2].left)
		score += antimtch_metric(lop[2].bottom, lop[5].top)
		score += antimtch_metric(lop[3].right , lop[4].left)
		score += antimtch_metric(lop[4].right , lop[5].left)
	
	return score


def hand_pick(lop, test=0):
	def match_metric(la, lb):
		score = 0	
				
		def closely_match(sa, los):
			mscore = 0
			for sb in los:
				pr = sa.pos_relation(sb)
				
				if   pr == 0:
					continue
				elif pr == 1:
					del los[0:los.index(sb)+1]
					mscore += sa.fuzzy_match(sb)
					if test != 0: print("[", sa.start, "->", sa.end, "]", "Matched with", "[", sb.start, "->", sb.end, "]")
					break
				elif pr == 2:
					break
			
			return mscore				#0 - 100, how closely it matches
			
			
		losa, losb = get_slices(la[0], lb[0])
		closa, closb = losa.copy(), losb.copy()
		
		for s in losa:
			score += closely_match(s, closb)
			
		if test != 0: print("----------------Side B------------------")
		
		for s in losb:
			score += closely_match(s, closa)
		
		
		return score
		
	
	
	
	score = 0
	if   test ==  9:
		score += match_metric(lop[0].right , lop[1].left)
	elif test == 10:
		score += match_metric(lop[0].bottom, lop[3].top)
	elif test == 11:
		score += match_metric(lop[1].bottom, lop[4].top)
	elif test == 12:
		score += match_metric(lop[1].right , lop[2].left)
	elif test == 13:
		score += match_metric(lop[2].bottom, lop[5].top)
	elif test == 14:
		score += match_metric(lop[3].right , lop[4].left)
	elif test == 15:
		score += match_metric(lop[4].right , lop[5].left)
	else:
		score += match_metric(lop[0].right , lop[1].left)
		score += match_metric(lop[0].bottom, lop[3].top)
		score += match_metric(lop[1].bottom, lop[4].top)
		score += match_metric(lop[1].right , lop[2].left)
		score += match_metric(lop[2].bottom, lop[5].top)
		score += match_metric(lop[3].right , lop[4].left)
		score += match_metric(lop[4].right , lop[5].left)
		
		
	return score

	
	
def normalize(lop, test=0):
	def white_metric(la, lb):
		score = 0
		def isdark(p):
			return p <= 160
		def islight(p):
			return p > 160
		
		wtspots = {}
		series = False
		lastwt = 0
		for i in range(0, 118):
			if islight(la[0][i]):
				if series == False:
					wtspots[i] = 1
					lastwt = i
					series = True
				else:
					wtspots[lastwt] += 1
				
			else:
				series = False
		
		keys = tuple(wtspots.keys())
		if len(keys) != 0:
			bscr = 0
			for k in keys:
				blk  = 0
				acrs = 0
				if test != 0: print("[ ", k, "->", wtspots[k], " ]")
				for i in range(k, wtspots[k]):
					if isdark(lb[0][i]):
						blk += 1
						if acrs > 0:
							blk += (acrs if acrs < 25 else 0)
							acrs = 0
					elif blk > 0:
						acrs += 1
						
				if blk > 3:
					bscr += blk
					
				if test != 0: print(blk)
				
			score -= bscr

		return score
	
	score = []
	if test == 1:
		score.append(white_metric(lop[0].right , lop[1].left))
	elif test == 2:
		score.append(white_metric(lop[0].bottom, lop[3].top))
	elif test == 3:
		score.append(white_metric(lop[1].bottom, lop[4].top))
	elif test == 4:
		score.append(white_metric(lop[1].right , lop[2].left))
	elif test == 5:
		score.append(white_metric(lop[2].bottom, lop[5].top))
	elif test == 6:
		score.append(white_metric(lop[3].right , lop[4].left))
	elif test == 7:
		score.append(white_metric(lop[4].right , lop[5].left))
	else:
		score.append(white_metric(lop[0].right , lop[1].left))
		score.append(white_metric(lop[0].bottom, lop[3].top))
		score.append(white_metric(lop[1].bottom, lop[4].top))
		score.append(white_metric(lop[1].right , lop[2].left))
		score.append(white_metric(lop[2].bottom, lop[5].top))
		score.append(white_metric(lop[3].right , lop[4].left))
		score.append(white_metric(lop[4].right , lop[5].left))
		
		score.sort(reverse=True)
		
		score = reduce(lambda a,b: a + b, score[0:-2])
		
	return score
	
# List of Piece -> String
# turn Piece list into orientation String
def pcs_to_ornt(lop):
	ornt = ""
	for pc in lop:
		ornt += ("" if ornt == "" else ",") + str(pc.id)
	return ornt
	
	
# List of Piece -> Number
# calculate the score of given lop
def calc_score(lop, motroc=""):
	score = 0
	# List of 118 Number, List of 118 Number -> Number
	# compares 2 puzzle piece sides and adds to the score
	# if the pixel is dark enough on both sides
	def prwdiff(la, lb):
		if motroc == "avg":
			avga = 0
			avgb = 0
			for i in range(0, 118):
				avga += la[0][i]
				avgb += lb[0][i]
			
			avga = avga / 118
			avgb = avgb / 118
			
			return -abs(avga - avgb) * 2
			
		# return -(abs(avga - avgb) * 10)
		# 1st. correlation					
		# 2nd. euclidean
		# 2nd. minkowski
		if motroc == "":
			pwd = pairwise_distances(la, lb, metric="correlation")[0][0] * 1000
			pwd += pairwise_distances(la, lb, metric="euclidean")[0][0] * 3
		else:
			pwd = pairwise_distances(la, lb, metric=motroc)[0][0]
		return -pwd
	
	
	score += prwdiff(lop[0].right , lop[1].left)
	score += prwdiff(lop[0].bottom, lop[3].top)
	score += prwdiff(lop[1].bottom, lop[4].top)
	score += prwdiff(lop[1].right , lop[2].left)
	score += prwdiff(lop[2].bottom, lop[5].top)
	score += prwdiff(lop[3].right , lop[4].left)
	score += prwdiff(lop[4].right , lop[5].left)
				
	return score
		
		
# List of 6 Piece -> List of 720 (String, Number)
# Matches all possible orientations and calculates each orientation score
#		String -> orientation of the pieces
#		Number -> score that tells how good a match is
def match(pcs):
	ornt_scr_list = []
	def aux(visited=[]):
		if len(visited) == 6:
			ornt_scr_list.append([visited, calc_score(visited)])
		else:
			for pc in pcs:
				if pc not in visited:
					new_vstd = visited.copy()
					new_vstd.append(pc)
					aux(new_vstd)
			
		
	aux()
	return ornt_scr_list


"""
def manually_solve(ornt):
	print(ornt)
	crnt = [0, 1, 2, 3, 4, 5]
	pag.mouseDown(cp[0][0], cp[0][1] - 80)
	pag.mouseUp
	sleep(1)
	target = list(map(int, ornt.split(",")))
	for i in range(0, 5):
		if crnt[i] != target[i]:
			dpc = crnt.index(target[i])
			pag.moveTo(cp[dpc][0], cp[dpc][1])
			sleep(0.5)
			pag.dragTo(cp[i][0], cp[i][1], duration=1)
			sleep(0.5)
			temp = crnt[i]
			crnt[i] = crnt[dpc]
			crnt[dpc] = temp
	
	pag.mouseDown(cp[3][0] - 150, cp[3][1] - 45)
	pag.mouseUp()
"""	
def human_match(lop, test=0):
	def humanize(la, lb, n):
		score = 0
		
		
		
		return score



	score = 0
	if   test ==  9:
		score += humanize(lop[0].right , lop[1].left, 0)
	elif test == 10:
		score += humanize(lop[0].bottom, lop[3].top,  1)
	elif test == 11:
		score += humanize(lop[1].bottom, lop[4].top,  2)
	elif test == 12:
		score += humanize(lop[1].right , lop[2].left, 3)
	elif test == 13:
		score += humanize(lop[2].bottom, lop[5].top,  4)
	elif test == 14:
		score += humanize(lop[3].right , lop[4].left, 5)
	elif test == 15:
		score += humanize(lop[4].right , lop[5].left, 6)
	else:
		score += humanize(lop[0].right , lop[1].left, 0)
		score += humanize(lop[0].bottom, lop[3].top,  1)
		score += humanize(lop[1].bottom, lop[4].top,  2)
		score += humanize(lop[1].right , lop[2].left, 3)
		score += humanize(lop[2].bottom, lop[5].top,  4)
		score += humanize(lop[3].right , lop[4].left, 5)
		score += humanize(lop[4].right , lop[5].left, 6)
		
		
	return score


def getData(ornt):
	ornttpl = tuple(map(int, ornt.split(",")))
	p0 = pccords[ornttpl[0]]
	p1 = pccords[ornttpl[1]]
	p2 = pccords[ornttpl[2]]
	p3 = pccords[ornttpl[3]]
	p4 = pccords[ornttpl[4]]
	p5 = pccords[ornttpl[5]]
	timg1 = shwimg[p0[1]:p0[1]+118, p0[0]:p0[0]+118]
	timg2 = shwimg[p1[1]:p1[1]+118, p1[0]:p1[0]+118]
	timg3 = shwimg[p2[1]:p2[1]+118, p2[0]:p2[0]+118]
	timg4 = shwimg[p3[1]:p3[1]+118, p3[0]:p3[0]+118]
	timg5 = shwimg[p4[1]:p4[1]+118, p4[0]:p4[0]+118]
	timg6 = shwimg[p5[1]:p5[1]+118, p5[0]:p5[0]+118]
	row1 = np.hstack((timg1, timg2, timg3))
	row2 = np.hstack((timg4, timg5, timg6))
	full = np.vstack((row1, row2))
	cv2.imwrite("solution.png", full)
	
	return cv2.imread("solution.png", 0).flatten()

def showResult(ornt):
	ornttpl = tuple(map(int, ornt.split(",")))
	p0 = pccords[ornttpl[0]]
	p1 = pccords[ornttpl[1]]
	p2 = pccords[ornttpl[2]]
	p3 = pccords[ornttpl[3]]
	p4 = pccords[ornttpl[4]]
	p5 = pccords[ornttpl[5]]
	timg1 = shwimg[p0[1]:p0[1]+118, p0[0]:p0[0]+118]
	timg2 = shwimg[p1[1]:p1[1]+118, p1[0]:p1[0]+118]
	timg3 = shwimg[p2[1]:p2[1]+118, p2[0]:p2[0]+118]
	timg4 = shwimg[p3[1]:p3[1]+118, p3[0]:p3[0]+118]
	timg5 = shwimg[p4[1]:p4[1]+118, p4[0]:p4[0]+118]
	timg6 = shwimg[p5[1]:p5[1]+118, p5[0]:p5[0]+118]
	row1 = np.hstack((timg1, timg2, timg3))
	row2 = np.hstack((timg4, timg5, timg6))
	full = np.vstack((row1, row2))
	cv2.imwrite("solution " + ornt + " .png", full)
	#cv2.waitKey(0)
	
# RGB Image -> String
# The main puzzle solver function
#	the puzzle solver has to take a screenshot of a puzzle in the game war of dragons
#	it analyses this image and find the best configuration of the puzzle pieces which
#	solves the puzzle, this orientation is return as String -> "013524" each number
#	represents the id of the pieces in view and their should be position
def solve(img, metric="", test=0, shwornt=""):
	#img = cv2.imread(img)
	#pieces = puzzle_to_piece(img)
	# ------------------------
	global mtrc
	mtrc = metric
	if type(img) == str:
		img = cv2.imread(img)
	else:
		img = np.array(img)
		img = rgb_to_bgr(img)
	cv2.imwrite("puzzle.png", img)
	pieces = puzzle_to_piece(img)
	
	global shwimg
	shwimg = img
	
	if test == 0:
		orientation = best_match(pieces, shwornt)
		if shwornt != "":
			orientation = shwornt
		showResult(orientation)
		return orientation
	else:
		return test_suite(pieces, test)
	
	
	

# RGB Image -> BGR Image
# turn Pillow images into OpenCV compatible image
def rgb_to_bgr(rgbimg): 
	# Convert RGB to BGR 
	bgrimg = rgbimg[:, :, ::-1].copy()
	return bgrimg


def test_suite(lop, num=1):
	if num < 9:
		print(normalize(lop, num))
	elif num < 17:
		print(hand_pick(lop, num))
	elif num < 25:
		print(anti_match(lop, num))
	elif num < 33:
		print(human_match(lop, num))
# Image cropping
#crop_img = large_image[MPy + 41:MPy + 41 + PHIGT, MPx - 53:MPx - 53 + PWDTH].copy()
#cv2.imshow("cropped", crop_img)
#---------------------------
# TESTS
def pos_relation_test():
	sa = Slice(50, 80)
	
	sb1 = Slice(0, 30)		# completely above a
	sb2 = Slice(0, 50)		# above a but touching a's upper border
	sb3 = Slice(0, 65)		# above a but part of it is inside a
	#--------------------
	sb4  = Slice(45, 75) 	# a little above and inside a
	sb5  = Slice(50, 80)	# mirror of a
	sb6  = Slice(55, 85)	# a little lower and inside a
	sb61 = Slice(55, 75)	# completely inside a with relatively close borders
	#--------------------
	sb7 = Slice(65, 95)		# lower than a but part of it is inside a
	sb8 = Slice(80, 100)	# lower than a but touches a's lower border
	sb9 = Slice(90, 118)	# completely lower than a
	#--------------------
	# Cases where slice b is above slice a
	print(sa.pos_relation(sb1) == 0)
	print(sa.pos_relation(sb2) == 0)
	print(sa.pos_relation(sb3) == 0)
	# Cases where slice b is level with slice a
	print(sa.pos_relation(sb4) == 1)
	print(sa.pos_relation(sb5) == 1)
	print(sa.pos_relation(sb6) == 1)
	print(sa.pos_relation(sb61) == 1)
	# Cases where slice b is lower than slice a
	print(sa.pos_relation(sb7) == 2)
	print(sa.pos_relation(sb8) == 2)
	print(sa.pos_relation(sb9) == 2)
	


# INITIALIZING THE PREDICITON MACHINE LEARNING METHODS
#knn = KNeighborsClassifier(n_neighbors=1)
#puzzle = {}
#puzzle['data'] = np.empty((1360, 83544))
#
#list = []
#for i in range(0, 1360):
#	puzzle['data'][i] = cv2.imread('df/' + str(i) + '.png', 0).flatten()
#	if (i % 40) == 0:
#		list.append("Correct")
#	else:
#		list.append("Wrong")
#		
#puzzle['target'] = np.array(list)
#
#X = puzzle['data']
#y = puzzle['target']
#
#knn.fit(X, y)

#knn = pickle.load(open('model.sav', 'rb'))

#print(knn.score(X, y))

#print(knn.predict(np.array([cv2.imread('df/0.png', 0).flatten()])))