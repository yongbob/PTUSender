# coding:gbk
# author: Marshall Bao

#from PTURun import PRun
#from PTUType import PType
from PTUUI import PTUMainFrm
import tkinter as tk

#PRun.run(PType.ProtocolType.Syslog)

#PRun.run(PType.ProtocolType.SNMP)
import PTUUtils.PTUCommon as common

class MainPTUTool(PTUMainFrm.MainFrame):
    '''
    main func class
    '''

    def __init__(self, master=None):
        super(MainPTUTool, self).__init__(master)
        self.root = master


if __name__ == '__main__':
    '''
    main loop
    '''

    common.init_para()

    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry()
    root.title("PTU Sender")
    def close():
        common.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    app = MainPTUTool(root)
    root.mainloop()
