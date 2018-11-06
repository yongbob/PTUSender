# coding:gbk
# author: Marshall Bao
import os, sys

import PTUUI.PyTkinter as pytk
import PTUUI.PTUConfigFrm as ptcfg
import PTUUtils.PTUData1 as pd1
import PTUUtils.PTUType as ptype
import tkinter.messagebox
import PTUSNMP.PSNMP as psnmp
#import PTUSyslog.PSyslog as plog
import PTUSyslog.PSyslog as plog
import PTUUtils.PTUCommon as common

g_font = ('Monaco', 9)

if sys.version_info[0] == 2:
    from tkinter import *
    from tkFont import Font
    from ttk import *
    # Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    # Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    # import tkFileDialog
    # import tkSimpleDialog
else:  # Python 3.x
    import tkinter as tk
    from tkinter.font import Font
    from tkinter import ttk
    from tkinter.messagebox import *
    from tkinter.scrolledtext import ScrolledText

    # import tkinter.filedialog as tkFileDialog
    # import tkinter.simpledialog as tkSimpleDialog    #askstring()


class PTUFrame(object):


    def __init__(self, master=None):
        '''
        初始化
        '''

        self.root = master
        self.frm_middle_send_btn=None
        self.nb = None
        self.create_frame()

    def create_frame(self):
        self.frm = self.root

        self.frm_top = pytk.PyLabelFrame(self.frm)
        self.frm_middle = pytk.PyLabelFrame(self.frm,bd=0)
        self.frm_status = pytk.PyLabelFrame(self.frm,bd=0)

        self.create_frm_top()
        self.create_frm_middle()
        self.create_frm_status()

        self.frm_top.grid(row=0,column=0,sticky=tk.W)
        self.frm_middle.grid(row=1,column=0,pady=(5,10),sticky=tk.W)
        self.frm_status.grid(row=2,column=0,sticky=tk.W)

    def create_frm_top(self):
        self.nb = ttk.Notebook(self.root)
        self.frm_syslog = pytk.PyTTKFrame(self.nb,bd=0)
        self.frm_snmp = pytk.PyTTKFrame(self.nb,bd=0)
        self.frm_config = pytk.PyTTKFrame(self.nb,bd=0)

        self.send_config = ptcfg.PTUConfigFrm(self.frm_config)
        self.syslog_pd1 = pd1.PTUData1(self.frm_syslog,self.send_config)
        self.snmp_pd1 = pd1.PTUData1(self.frm_snmp,self.send_config)

        self.nb.add(self.frm_config, text="系统配置")
        self.nb.add(self.frm_syslog, text="Syslog")
        self.nb.add(self.frm_snmp, text="SNMP")
        self.nb_frame=(self.syslog_pd1,self.snmp_pd1)

        self.nb.grid(row=0,column=0)
        self.nb.bind('<<NotebookTabChanged>>',self.notebook_change)
        self.dict_nb = self.nb.tabs()
    def create_frm_middle(self):

        self.frm_middle_clearlog_btn = pytk.PyButton(self.frm_middle,
                                                  text="清空日志",
                                                  width=10,
                                                  font=g_font,
                                                  command=self.ClearLog)
        self.frm_middle_send_btn = pytk.PyButton(self.frm_middle,
                                                 text="发送",
                                                 width=10,
                                                 font=g_font,
                                                 command=self.Send)
        self.frm_middle_pause_resume_btn = pytk.PyButton(self.frm_middle,
                                                 text="Timer暂停",
                                                 width=15,
                                                 font=g_font,
                                                 command=self.Pause_Resume)

        self.btn_send_status('disabled') #in config tab page, no send command
        self.threshold_str = tk.StringVar()

        self.frm_middle_clearlog_btn.grid(row=0,column=0,sticky=tk.W,padx=(10,5))
        self.frm_middle_send_btn.grid(row=0,column=1,sticky=tk.W)
        self.frm_middle_pause_resume_btn.grid(row=0,column=2,sticky=tk.W,padx=(5,5))

    def create_frm_status(self):

        self.frm_status_vbar=tk.Scrollbar(self.frm_status)
        self.frm_status_vbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        self.frm_status_hbar = tk.Scrollbar(self.frm_status, orient=tk.HORIZONTAL)
        self.frm_status_hbar.grid(row=1,column=0,columnspan=2,sticky=tk.E+tk.W)


        self.frm_status_text = pytk.PyText(self.frm_status,
                                           #font=g_font,
                                           width=75, height=10,
                                           yscrollcommand=self.frm_status_vbar.set,
                                           xscrollcommand=self.frm_status_hbar.set,
                                           wrap='none')
        self.frm_status_text.grid(row=0,column=0,sticky=tk.W)

        self.frm_status_vbar.config(command=self.frm_status_text.yview)
        self.frm_status_hbar.config(command=self.frm_status_text.xview)
        #self.send_config.setloghandler(self.frm_status_text)
        common.g_loghandler = self.frm_status_text

    def ClearLog(self):
        self.frm_status_text.delete(1.0,tk.END)
        self.frm_status_text.see(tk.END)
        self.frm_status_text.update()

    def Send(self):
        i = self.notebook_tabid()
        if i == ptype.ProtocolType.Syslog.value:
            plog.sendsyslog(self.nb_frame[i-1])
        elif i == ptype.ProtocolType.SNMP.value:
            psnmp.sendsnmp(self.nb_frame[i-1])

        else:
            tkinter.messagebox.showerror('错误', '错误的协议类型')

    def Pause_Resume(self):
        # pause/resume of global_syslog_timer and global_snmp_timer
        if common.g_syslog_timer.status(): #resume->pause
            common.g_syslog_timer.pause_counter()

            self.frm_middle_pause_resume_btn['text'] = 'Timer暂停'
        else: #pause->resume
            common.g_syslog_timer.resume()
            self.frm_middle_pause_resume_btn['text']='Timer运行'
        #print(common.g_syslog_timer.get_counter())
    def btn_send_status(self,status):
        self.frm_middle_send_btn['state'] = status

    def notebook_tabid(self):
        nb_name = self.nb.select()

        i = 0
        for eachtab in self.dict_nb:
            if eachtab == nb_name:
                break
            i = i + 1
        return i
    def notebook_change(self,*args):
        i = self.notebook_tabid()
        if i > 0:
            status = 'normal'
        else:
            status = 'disabled'

        self.nb_frame[i-1].update_send_para()
        self.btn_send_status(status)
    