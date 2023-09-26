from time import sleep
import configparser
from os.path import isfile
import tkinter as tk
from tkinter import ttk, font, PhotoImage

PREF_PATH = "pref.ini"
if not isfile(PREF_PATH):
	HEAL_PREF = {
	"State" : "disabled",
	"Percent" : "60"
	}
else:
	config = configparser.ConfigParser()
	config.read(PREF_PATH)
	HEAL_PREF = config['HEAL']
	
prcvarToPercent = {
	0 : "20",
	1 : "40",
	2 : "60",
	3 : "80"
}
percentToPrcvar = {
	"20" : 0,
	"40" : 1,
	"60" : 2,
	"80" : 3
}
hlvarToHlstate = {
	0 : "disabled",
	1 : "enabled"
}
hlstateToHlvar = {
	"disabled" : 0,
	"enabled" : 1
}

class MainGui:
	
	def __init__(self, controls):
		cgui = tk.Tk()
		#-------------------------------------------------------
		# CONSTANTS
		DEFAULT_FONT = font.Font(family="Corbel",size=12)
		WIDTH = 270
		HEIGHT = 325
		
		NPCS = []
		if isfile('mobs.txt'):
			with open('mobs.txt') as f:
				for line in f.readlines():
					line = line.replace('\n', '')
					if line != '':
						NPCS.append(line)
					
		for mob in ["Granite Golem", "Dugrkharg", "Zombie", 
				"Maverick Gungl", "GunglVO", "Stone Golem", "Sharker Legionnaire", 
				"GunglXO", "Gargoyle", "Large Scorpion" ,"GunglXO Inspector", "Grim Gargoyle",
				"King Scorpion" ,"Fire Kroffdor", "Eldive Warrior", "Female Eldive Warrior", 
				"Fierce Kroffdor", "Eldive Mage", "Dark Kroffdor"]:
			NPCS.append(mob)
		#-------------------------------------------------------
		# TABS
		tabcontrol = ttk.Notebook(cgui)
		auto_fight = ttk.Frame(tabcontrol)
		auto_collect = ttk.Frame(tabcontrol)
		tabcontrol.add(auto_fight, text="Auto-Fighter")
		tabcontrol.add(auto_collect, text="Auto-Collector")
		tabcontrol.pack(expand = 1, fill ="both")
		#-------------------------------------------------------
		# AUTO-FIGHTER CONTROLS
		tk.Label(auto_fight, text="Choose mob to kill:", font=DEFAULT_FONT).grid(column = 0, 
															  row    = 0,
															  padx = 5,
															  pady = 5,
															  sticky = tk.W)
		# SELECT NPC COMBOBOX 
		select_npc = tk.StringVar()
		select_npc.set(NPCS[0])
		npc_cb = ttk.Combobox(auto_fight, textvariable=select_npc, width=WIDTH//10, font=DEFAULT_FONT)
		npc_cb['values'] = NPCS
		#npc_cb['state'] = 'readonly'
		npc_cb.grid(row = 1, column = 0, padx = 12)
		# PREFERENCE OPTIONS
		#	AUTO-HEAL FRAME
		ah_frame = tk.LabelFrame(auto_fight, text="Auto-Heal")
		ah_frame.grid(row=2, column=0, padx = 8, pady= 10, sticky = tk.W)
		hlVar = tk.IntVar()
		hlVar.set(hlstateToHlvar[HEAL_PREF['State']])
		tk.Radiobutton(ah_frame, text="Disabled			", variable=hlVar, value=0).grid(row=0, column=0, sticky = tk.W)
		tk.Radiobutton(ah_frame, text="Enabled	", variable=hlVar, value=1).grid(row=0, column=1, sticky = tk.E)
		
		tk.Label(ah_frame, text="Health percent to use heal at :", font=DEFAULT_FONT).grid(row=1,column=0,columnspan=2,sticky=tk.W)
		hlprcVar = tk.IntVar()
		hlprcVar.set(percentToPrcvar[HEAL_PREF['Percent']])
		tk.Radiobutton(ah_frame, text="20%", variable=hlprcVar, value=0).grid(row=2, column=0, sticky = tk.W)
		tk.Radiobutton(ah_frame, text="40%", variable=hlprcVar, value=1).grid(row=2, column=0)
		tk.Radiobutton(ah_frame, text="60%", variable=hlprcVar, value=2).grid(row=2, column=0, sticky = tk.E)
		tk.Radiobutton(ah_frame, text="80%", variable=hlprcVar, value=3).grid(row=2, column=1)
		# 	GIANT POTION FIRST
		gp_frame = tk.LabelFrame(auto_fight, text="Auto-Giant")
		gp_frame.grid(row=3, column=0, padx = 8, sticky = tk.W)
		self.gpVar = tk.IntVar()
		self.gpVar.set(0)
		tk.Radiobutton(gp_frame, text="Disabled			", variable=self.gpVar, value=0).grid(row=0, column=0, sticky=tk.W)
		tk.Radiobutton(gp_frame, text="Enabled	", variable=self.gpVar, value=1).grid(row=0, column=0, sticky = tk.E)
		#----------------------
		# CONTROL BUTTONS
		self.stop_btn = tk.Button(auto_fight, text = "STOP", width = round(WIDTH / 34), font=DEFAULT_FONT, command = lambda : self.stop(controls['STOP']))
		self.stop_btn.grid(row = 4, column = 0, padx = 5, pady = 10, sticky = tk.W)
		self.stop_btn['state'] = 'disabled'
		
		self.status_lbl = tk.Label(auto_fight, text="Status", font=DEFAULT_FONT)
		
		self.run_btn = tk.Button(auto_fight, text="RUN", width = round(WIDTH / 15),font=DEFAULT_FONT, command = lambda : self.run(controls['START'], select_npc.get(),lambda : self.updatePref(hlVar.get(), hlprcVar.get())))
		self.run_btn.grid(row = 4, column = 0, padx = 5, pady = 10, sticky = tk.E)
		# STATUS LABEL
		self.status_lbl.grid(row = 5, column = 0, padx = 10, sticky = tk.NW)
		#-----------------------------------------------------------------------------------------------------
		# Auto-Collector Controls
		PLANTS = []
		if isfile('plants.txt'):
			with open('plants.txt') as f:
				for line in f.readlines():
					line = line.replace('\n', '')
					if line != '':
						PLANTS.append(line)
						
		PLANTS.append("Aquamarine")
			
		tk.Label(auto_collect, text="Choose object to collect:", font=DEFAULT_FONT).grid(column = 0, 
															  row    = 0,
															  padx = 5,
															  pady = 5,
															  sticky = tk.W)
		# SELECT PLANT COMBOBOX 
		select_plant = tk.StringVar()
		select_plant.set(PLANTS[0])
		plant_cb = ttk.Combobox(auto_collect, textvariable=select_plant, width=WIDTH//10, font=DEFAULT_FONT)
		plant_cb['values'] = PLANTS
		plant_cb['state'] = 'readonly'
		plant_cb.grid(row = 1, column = 0, padx = 12)
		
		# SELECT TOOL OPTIONS
		TOOLS = []
		if isfile('tools.txt'):
			with open('tools.txt') as f:
				for line in f.readlines():
					line = line.replace('\n', '')
					if line != '':
						TOOLS.append(line)
						
		
		TOOLS.append("Pickaxe")
			
		tk.Label(auto_collect, text="Choose tool to use:", font=DEFAULT_FONT).grid(column = 0, 
															  row    = 2,
															  padx = 5,
															  pady = 5,
															  sticky = tk.W)
		# SELECT TOOL COMBOBOX 
		select_tool = tk.StringVar()
		select_tool.set(TOOLS[0])
		tools_cb = ttk.Combobox(auto_collect, textvariable=select_tool, width=WIDTH//10, font=DEFAULT_FONT)
		tools_cb['values'] = TOOLS
		tools_cb['state'] = 'readonly'
		tools_cb.grid(row = 3, column = 0, padx = 12)
		
		
		self.frm_str_btn = tk.Button(auto_collect, text="RUN", width=round(WIDTH / 16), font=DEFAULT_FONT, command= lambda : self.frm_run(controls['FRMSTART'], select_plant.get(), select_tool.get()))
		self.frm_stp_btn = tk.Button(auto_collect, text="STOP", width=round(WIDTH / 34), font=DEFAULT_FONT, command= lambda : self.frm_stop(controls['STOP']))
		
		self.frm_str_btn.grid(row = 4, column = 0, pady = 115, padx = 5, sticky = tk.E)
		self.frm_stp_btn.grid(row = 4, column = 0, pady = 115, padx = 5, sticky = tk.W)
		self.frm_stp_btn['state'] = 'disabled'
		
		self.frm_status_lbl = tk.Label(auto_collect, text='Status', font=DEFAULT_FONT)
		self.frm_status_lbl.grid(row = 4, column = 0, pady = 85, padx = 6, sticky = tk.SW)
		#-----------------------------------------------------------------------------------------------------
		cgui.title("Hisham Moe's Bot")
		cgui.iconphoto(False, tk.PhotoImage(file='icon.png'))
		cgui.geometry(str(WIDTH) + 'x' + str(HEIGHT) + '+50+50')
		cgui.resizable(False, False)
		cgui.mainloop()
	
	def run(self, start, mob, saveCb):
		saveCb()
		start(mob, self.status_lbl, HEAL_PREF['State'], HEAL_PREF['Percent'], self.gpVar.get())
		self.run_btn['state'] = 'disabled'
		self.stop_btn['state'] = 'normal'
		
		self.frm_str_btn['state'] = 'disabled'
		self.frm_status_lbl['text'] = 'Auto-Fighter Running...'
			
	def stop(self, stopf):
		stopf()
		self.run_btn['state'] = 'normal'
		self.stop_btn['state'] = 'disabled'
		
		self.frm_str_btn['state'] = 'normal'
		self.frm_status_lbl['text'] = 'Ready'
	
	def frm_run(self, start, plnt, tool):
		start(plnt, tool, self.frm_status_lbl)
		self.run_btn['state'] = 'disabled'
		self.status_lbl['text'] = 'Auto-Collector Running...'
		
		self.frm_str_btn['state'] = 'disabled'
		self.frm_stp_btn['state'] = 'normal'
		
	def frm_stop(self, stopf):
		stopf()
		self.run_btn['state'] = 'normal'
		self.status_lbl['text'] = 'Ready'
		
		self.frm_str_btn['state'] = 'normal'
		self.frm_stp_btn['state'] = 'disabled'
	
	def updatePref(self, hlvr, prcvr):
		state = hlvarToHlstate[hlvr]
		percent = prcvarToPercent[prcvr]
		
		config = configparser.ConfigParser()
		config['HEAL'] = {
			'State' : state,
			'Percent' : percent
		}
		
		global HEAL_PREF
		if config['HEAL'] != HEAL_PREF:
			with open(PREF_PATH, 'w') as configfile:
				config.write(configfile)
			HEAL_PREF = config['HEAL']
	
	
if __name__ == '__main__':
	MainGui(None)
	