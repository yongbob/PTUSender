# coding=gbk

import tkinter as tk
import PTUUtils.IPEntry as ipe
import tkinter.ttk as ttk
import re

class PTUMessage(tk.Toplevel):
    def __init__(self, title,message):
        super().__init__()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.title(title)
        tk.Label(self, text=message).grid(row=0)

        btnOK = tk.Button(self, text="确定", command=self.ok)
        btnOK.grid(row=1)
        tk.Label(self).grid(row=2)
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        height = 100
        width = 200
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2 - 100)
        print(size)
        self.geometry(size)

    def ok(self):
        self.destroy()

class PTUIPDialog(tk.Toplevel):

    def __init__(self, ip=None,port=None):
        super().__init__()
        self.top = self.winfo_toplevel()
        self.port = tk.StringVar()
        if ip == None:
            self.ip = '127.0.0.1'
        else:
            self.ip = ip
        if port==None:
            self.port.set("514")
        else:
            self.port.set(port)

        self.title("IP地址以及端口")

        tk.Label(self, text="IP地址：").grid(row=0,column=0,pady=5)
        self.ipv4=ipe.IPEntry(self)
        self.ipv4.setIP(self.ip)
        self.ipv4.grid(row=0,column=1,pady=5)

        tk.Label(self,text="").grid(row=0,column=2,padx=3)
        tk.Label(self,text="端口：").grid(row=0,column=3)
        self.portEntry=tk.Entry(self,width=6,textvariable=self.port)
        self.portEntry.grid(row=0,column=4,padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        btnOK = tk.Button(self, text="确定", command=self.ok)
        btnOK.grid(row=1,column=0,columnspan=2,pady=5)

        btnCancel = tk.Button(self,text="取消",command=self.cancel)
        btnCancel.grid(row=1,column=2,columnspan=2)

        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        height = 80
        width = 300
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        print(size)
        self.geometry(size)

    def checkPort(self,p):
        if p == '':
            return False
        elif p == None:
            return False
        elif p.isdigit() == False:
            return False
        else:
            return True

    def checkIP(self,i):
        validateIP = re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", i)
        if validateIP:
            return True
        else:
            return False


    def ok(self, *args):

        print(self.ipv4.getIP(),':',self.port.get())
        self.ipinfo=[self.ipv4.getIP(),self.port.get()]
        if self.checkPort(self.ipinfo[1]) == False:
            PTUMessage('错误', '端口输入错误')
            return
        if self.checkIP(self.ipinfo[0]) == False:
            #tk.messagebox.showerror('错误', 'IP地址输入错误')
            PTUMessage('错误', 'IP地址输入错误')
            return

        self.destroy()


    def cancel(self,*args):
        self.ipinfo=None
        self.destroy()



if __name__ == '__main__':
    root = tk.Tk()
    def ipdialog():
        d = PTUIPDialog('1.1.1.1','23')
        root.wait_window(d.top)
        print(d.ipinfo)

        #print(d)

    # frame=tk.Frame(root)
    btn = tk.Button(root, text="dialog", command=ipdialog)
    btn.pack()



    root.mainloop()
