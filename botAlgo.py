import time
import threading
import puzzle_solver as ps
import numpy as np
from desktopmagic.screengrab_win32 import getScreenAsImage
import win32gui as wapi
from random import choice

class Bot:

	def __init__(self, webwin, gui):
		self.isRunning = False
		self.KEYCODES = {
			"1" : "49",
			"2" : "50",
			"3" : "51",
			"4" : "52",
			"5" : "53",
			"6" : "54",
			"7" : "55",
			"8" : "56",
			"q" : "81",
			"w" : "87",
			"e" : "69"
		}
		self.SEQ = {
			"0" : "w",
			"1" : "q",
			"2" : "w",
			"3" : "e"
		}
		self.MAPPING = {
		"Waiting for user to log in..." : self.longstall,
		"Looking for a mob..." : self.attackMob,
		"Opening hunt map" : self.openHunt,
		"Resurrecting..." : self.resurrect,
		"Fighting..." : self.fight,							# canvas.app.leftMenu.model.items[1]["image"]
		"Waiting for page to load..." : self.stall,			# "maxhp3-purp.gif" elixir image
		"Waiting for hunt to load..." : self.stall,
		"Waiting for top menu to load..." : self.stall,
		"Eating..." : self.eat,
		"Checking food..." : self.openEffects,
		"No food detected, regenerating..." : self.longstall,
		"Looking for a plant..." : self.collect,
		"Checking equipments..." : self.openBackpack,
		"Splinter! Asking for help" : self.callHelp,
		"Wearing sickle for collecting..." : self.wearSickle,
		"Solving captcha..." : self.solveCaptcha,
		"Waiting for procurement..." : self.longstall
		}
		self.CONTROLS = {
			"START" : self.start,
			"STOP" : self.stop,
			"FRMSTART" : self.frm_start,
		}
	
		self.gamewin = webwin
		for i in range(1, 21):
			if wapi.FindWindow(None, "BotClient" + str(i)) == 0:
				self.gamewin.set_title("BotClient" + str(i))
				self.winname = "BotClient" + str(i)
				break
			
		self.mob = ""
		self.plant = ""
		self.tool = ""
		self.sickleEquipped = False
		self.isFTR = True
		self.state_lbl = None
		self.isGPF = False
		self.pwr_on = True
		self.hl_on = True
		self.drankGP = False
		self.hl_percent = 80
		self.nextPot = 3
		self.seq = ""
		self.curHit = 0
		self.waitCounter = 0
		
		threading.Thread(target=gui, args=(self.CONTROLS,)).start()
		
		
	def next(self):
		self.state_lbl['text'] = state = self.getState()
		self.MAPPING[state]()
			
		
	def stall(self):
		time.sleep(1)
	
	def longstall(self):
		time.sleep(5)
		
	def getState(self):
		if not self.isPageReady():
			return "Waiting for page to load..."
		elif self.gamewin.get_current_url() != "https://warofdragons.com/main.php":
			return "Waiting for user to log in..."
		else:
			main = self.getMain()
			if self.isDead():
				return "Resurrecting..."
			elif main.find("blank") != -1:
				return "Waiting for page to load..."
			elif main.find("hunt") != -1:
				if self.huntReady():
					if self.hl_on and self.needToEat():
						if self.effectsReady():
							if self.haveFood():
								return "Eating..."
							else:
								return "No food detected, regenerating..."
						else:
							return "Checking food..."
					elif self.isFTR:
						return "Looking for a mob..."
					elif self.sickleOn():
						if self.isFree():
							self.waitCounter = 0
							return "Looking for a plant..."
						elif (self.waitCounter > 2) and (self.captchaOn()):
							return "Solving captcha..."
						elif self.waitCounter > 12:
							return "Opening hunt map"
						else:
							self.waitCounter += 1
							return "Waiting for procurement..."
					elif self.splintered():
						return "Splinter! Asking for help"
					elif self.backpackReady():
						return "Wearing sickle for collecting..."
					else:
						return "Checking equipments..."
				else:
					return "Waiting for hunt to load..."
			elif main.find("fight") != -1:
				if self.oponentDied():
					self.reset()
					return "Opening hunt map"
				else:
					return "Fighting..."
			elif self.canOpenHunt():
				return "Opening hunt map"
			else:
				return "Waiting for top menu to load..."
	
	def eat(self):
		self.gamewin.evaluate_js("main_frame.backpack.effectsSetUse(main_frame.backpack.document.getElementsByClassName('butt1 btn-use pointer')[0].getElementsByTagName('input')[0], parseInt(main_frame.backpack.document.getElementsByClassName('butt1 btn-use pointer')[0].getElementsByTagName('input')[0].onclick.toString().match(/\d+/)[0]))")
		self.stall()
	
	def haveFood(self):
		return self.gamewin.evaluate_js("main_frame.backpack.document.getElementsByClassName('butt1 btn-use pointer')[0].getElementsByTagName('input')[0].disabled == false")
	
	def reset(self):
		self.nextPot = 3
		self.curHit = 0
		
	def needToEat(self):
		return (self.getHpPrc() < 80)
	
	def effectsReady(self):
		return self.gamewin.evaluate_js("main_frame.backpack.document.URL == 'https://warofdragons.com/user.php?mode=effects_set'")
	
	def openEffects(self):
		self.gamewin.evaluate_js("main_frame.backpack.window.location.href = 'https://warofdragons.com/user.php?mode=effects_set'")
		self.stall()
		
	def resurrect(self):
		self.gamewin.evaluate_js("resurrect(1)")
		self.longstall()
		
	def isDead(self):
		return self.gamewin.evaluate_js("main_frame.canvas.app.avatar.model.ghost")
		
	def oponentDied(self):
		return self.gamewin.evaluate_js("main_frame.main.canvas.app.battle.model.oppStatus == 2") #&& (main_frame.main.canvas.app.battle.model.oppId == 0))
	
	def canOpenHunt(self):
		return self.gamewin.evaluate_js("main_frame.canvas.app.topMenu.model != undefined")
		
	def captchaOn(self):
		return self.gamewin.evaluate_js("main_frame.main.canvas.app.hunt.model.captchaFinishTime > 0")
		
	def huntReady(self):
		return self.gamewin.evaluate_js("main_frame.main.canvas.app.hunt.model != undefined")
	
	def isPageReady(self):
		return self.gamewin.evaluate_js(r"document.readyState == 'complete'")
		
	def getMain(self):
		return self.gamewin.evaluate_js("main_frame.main.document.URL")
		
	def start(self, mob, state_lbl, state="enabled", percent="80", gpf=0):
		self.mob = mob
		self.state_lbl = state_lbl
		self.hl_on = (state != "disabled")
		self.hl_percent = int(percent)
		self.isGPF = (gpf == 1)
		self.isRunning = True
		self.isFTR = True
		self.reset()
		
		threading.Thread(target=self.main_loop, args=()).start()
	
	def main_loop(self):
		while (self.isRunning):
			self.stall()
			self.next()
		self.state_lbl['text'] = 'Stopped'
		
	def stop(self):
		self.isRunning = False
	
	def openHunt(self):
		self.gamewin.evaluate_js("main_frame.canvas.app.topMenu.Main.prototype.processMenu(main_frame.canvas.app.topMenu.model.itemsById[3])")
		self.stall()
		self.stall()
		
	def attackMob(self):
		self.stall()
		self.gamewin.evaluate_js(r"""
			keys = Object.keys(main_frame.main.canvas.app.hunt.model.Objects)
			
			for (i=0; i < keys.length; i++) {
				if (main_frame.main.canvas.app.hunt.model.Objects[keys[i]].name == '""" + self.mob + """') {
					if (main_frame.main.canvas.app.hunt.model.Objects[keys[i]].fight_id == '0') {
						huntAttack(main_frame.main.canvas.app.hunt.model.Objects[keys[i]].id, false)
						break
					}
				}   
			}
		""")
		if self.isGPF : 
			self.drankGP = False
		
	def fight(self):
		if self.fightReady():
			if (self.attackReady()):
				if self.isGPF and not self.drankGP:
					self.drinkGP()
					self.drankGP = True
				else:
					self.attack(self.nextSeq())
			elif self.hl_on and (self.getHpPrc() <= self.hl_percent):
				if self.potReady():
					self.heal()
				else:
					self.nextPotSlot()
	
	def drinkGP(self):
		self.gamewin.evaluate_js("document.dispatchEvent(canvas.InputManager.processKey(new KeyboardEvent('keydown', {'key' : '" + "1" + "', 'keyCode' : " + self.KEYCODES["1"] + "})))")
		self.stall()
		
	def potReady(self):
		return self.gamewin.evaluate_js("main_frame.canvas.app.leftMenu.model.items['" + str(self.nextPot) + "'].cdLeft == 0")
	
	def getHpPrc(self):
		return round(100 * (self.gamewin.evaluate_js("main_frame.canvas.app.avatar.model.hpCur") / self.gamewin.evaluate_js("main_frame.canvas.app.avatar.model.hpMax")))
		
	def fightReady(self):
		return self.gamewin.evaluate_js("main_frame.main.canvas.app.battle.model != undefined")
	
	def nextSeq(self):
		self.seq = self.gamewin.evaluate_js(r"""
			for (i=0; i < main_frame.main.canvas.app.battle.model.combos.length;i++) {
				if (main_frame.main.canvas.app.battle.model.activeComboId == main_frame.main.canvas.app.battle.model.combos[i].id) {
					main_frame.main.canvas.app.battle.model.combos[i].seq
					break
				}
			}
		""")
		k = self.SEQ[self.seq[self.curHit]]
		self.curHit = (self.curHit + 1) if self.curHit < (len(self.seq) - 1) else 0
		
		if self.pwr_on and self.curHit == 0:	#Drink power potion before last hit
			self.drinkPower()

		return k
		
	def attack(self, k):
		self.gamewin.evaluate_js("document.dispatchEvent(canvas.InputManager.processKey(new KeyboardEvent('keydown', {'key' : '" + k + "', 'keyCode' : " + self.KEYCODES[k] + "})))")
		time.sleep(0.25)
		
	def drinkPower(self):
		self.gamewin.evaluate_js("document.dispatchEvent(canvas.InputManager.processKey(new KeyboardEvent('keydown', {'key' : '" + "2" + "', 'keyCode' : " + self.KEYCODES["2"] + "})))")
		time.sleep(0.25)
	
	def nextPotSlot(self):
		self.nextPot = (self.nextPot + 1) if self.nextPot < 9 else 3
		
	def heal(self):
		k = str(self.nextPot)
		self.gamewin.evaluate_js("document.dispatchEvent(canvas.InputManager.processKey(new KeyboardEvent('keydown', {'key' : '" + k + "', 'keyCode' : " + self.KEYCODES[k] + "})))")
		self.nextPotSlot()
		self.stall()
	
	def attackReady(self):
		return self.gamewin.evaluate_js("main_frame.main.canvas.app.battle.model.centerVisible")
		
	#----------------------------------------------------------------------------
	# Farm Functions
	def frm_start(self, plant, tool, lbl):
		self.gamewin.on_top = True
		self.isRunning = True
		self.plant = plant
		self.tool = tool
		self.isFTR = False
		self.hl_on = True
		self.state_lbl = lbl
		self.sickleEquipped = False
		
		threading.Thread(target=self.main_loop, args=()).start()
			
	def wearSickle(self):
		self.gamewin.evaluate_js("main_frame.backpack.user_iframe_2.artifactAct(main_frame.backpack.user_iframe_2.document.getElementsByClassName('artifact-slot')[1], 'equip')")	
		self.sickleEquipped = True
		self.stall()
	
	def splintered(self):
		return (self.sickleEquipped and (self.sickleOn() == False))
		
	def callHelp(self):
		MESSAGES = ["Help splinter", "I need help I got a splinter", "Can someone help me with this splinter?", "anyone here? can you remove this splinter?", "I don't have healings and I'm splintered someone help"]
		SLEEP = [180, 360, 600]
		self.gamewin.evaluate_js("""
		chat.gebi('message').value = ""
		for (i=0; i < chat.chat_user.document.getElementsByClassName("chat_user_item").length; i++) {
			if (chat.chat_user.document.getElementsByClassName("chat_user_item")[i].getAttribute("data-nick") != main_frame.canvas.app.avatar.model.login.toLowerCase()) {
				chat.gebi('message').value += 'prv[' + chat.chat_user.document.getElementsByClassName("chat_user_item")[i].getAttribute("data-nick") + '] '
			}
		}
		chat.gebi('message').value += '""" + choice(MESSAGES) + """'
		""")
		self.stall()
		self.gamewin.evaluate_js("chat.chatSend()")
		time.sleep(choice(SLEEP))
		self.wearSickle()
		if self.sickleOn():
			self.gamewin.evaluate_js("""
			msgs = chat.chat_text.document.getElementsByClassName("msgtxt")
			for (i=msgs.length - 1; i >= 0; i--) {
				if (msgs[i].innerText.endsWith("Your splinter has been removed.")) {
					e = msgs[i+1].innerText.indexOf("[")
					s = msgs[i+1].innerText.indexOf(",") + 1
					remover = msgs[i+1].innerText.slice(s, e).trim().toLowerCase()
					chat.gebi('message').value = "prv[" + remover + "] " + "ty"
				}
			}
			""")
			self.stall()
			self.gamewin.evaluate_js("chat.chatSend()")
		
	def sickleOn(self):
		return self.gamewin.evaluate_js("main_frame.backpack.user_iframe_2.document.getElementById('item_list').getElementsByClassName('item')[1].getAttribute('data-title') != '" + self.tool + "'")
		
	def backpackReady(self):
		return self.gamewin.evaluate_js("main_frame.backpack.user_iframe_2.document.URL != 'about:blank'")
	
	def openBackpack(self):	
		self.gamewin.evaluate_js("main_frame.canvas.app.topMenu.Main.prototype.processMenu(main_frame.canvas.app.topMenu.model.itemsById[1])")
		self.stall()
		self.stall()
		self.gamewin.evaluate_js("main_frame.backpack.swUserIframes('user_iframe_2', 'user_iframe.php?group=2')")
		self.stall()
		self.openHunt()
	
	def isFree(self):
		return self.gamewin.evaluate_js("((main_frame.main.canvas.app.hunt.model.farm.checking == undefined) || (main_frame.main.canvas.app.hunt.model.farm.checking))")
		
	def collect(self):
		self.gamewin.evaluate_js(r"""
			keys = Object.keys(main_frame.main.canvas.app.hunt.model.Objects)
			
			for (i=0; i < keys.length; i++) {
				if (main_frame.main.canvas.app.hunt.model.Objects[keys[i]].name == '""" + self.plant + """') {
					if (main_frame.main.canvas.app.hunt.model.Objects[keys[i]].farming == '0') {
						main_frame.main.canvas.app.hunt.model.farm.begin_farming(main_frame.main.canvas.app.hunt.model.Objects[keys[i]].num, 1, 1)
						break
					}
				}   
			}
		""")
		
#-------------------------------------------------------------------------------------
	def solveCaptcha(self):
		self.openHunt()
		time.sleep(1)
		self.collect()
		time.sleep(2)
		self.sendOrn(ps.solve(self.captureWin()))
		
	def captureWin(self):
		hndl = wapi.FindWindow(None, self.winname)
		wapi.SetForegroundWindow(hndl)
		wapi.SetActiveWindow(hndl)
		time.sleep(1)
		img = getScreenAsImage()
		return img
		
	def sendOrn(self, ornt):
		url = "hunt_conf.php?mode=farm&action=minigame_check&sequence=" + ornt
		self.gamewin.evaluate_js(r"""
			ldr = new canvas.utils.URLRequest
			ldr.load('""" + url + """')
		""")
		time.sleep(5)
		self.gamewin.evaluate_js("main_frame.main.canvas.app.hunt.model.captchaFinishTime = 0")
			
			
			