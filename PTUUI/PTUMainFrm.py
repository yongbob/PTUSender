# coding:gbk
# author: Marshall Bao
# import tkFont
import tkinter as tk
import datetime
import threading

import PTUUI.PyTkinter as pytk
from PTUUI.PTUFrm import PTUFrame

g_font = ("Monaco", 16)


class MainFrame(object):
    '''
    main frame
    '''

    def __init__(self, master=None):
        '''
        constructor
        '''
        self.root = master
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        width=630
        height=550
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)
        self.create_frame()

        self.state = True
        # self.root.attributes("-fullscreen", self.state)

    def create_frame(self):
        self.frm_main = pytk.PyLabelFrame(self.root)
        self.frm_main.grid(row=0,column=0)

        self.create_frm_main()

    def create_frm_main(self):
        self.PTU_frm = PTUFrame(self.frm_main)
        self.PTU_frm.frm.grid(row=0,column=0)






