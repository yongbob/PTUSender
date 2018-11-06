# coding=utf-8

from tkinter import Frame, Entry, StringVar, Tk

import re
from tkinter.constants import *
import tkinter as tk


class IPV4():

    def __init__(self, master):
        self.master = master
        validatecmd = (self.master.register(self.checkInput), '%P')

        self.entry = Entry(self.master,
                           justify=CENTER, width=3, relief='flat',
                           validate='key', validatecommand=validatecmd
                           )
        self.entry.bind("<FocusOut>", self.analyze)

    def configure(self, **kwargs):
        self.entry.configure(**kwargs)

    def analyze(self, event=None):
        ''' set ip to "0" if the entry is blank '''
        content = self.entry.get()
        if content == "":
            self.setEntry("0")

    def setEntry(self, ip):
        self.entry.delete(0, END)
        self.entry.insert(0, ip)

    def checkInput(self, content):
        ''' callback for validating input ip. '''

        if content == '':  # allow empty for entry. will put "0" when focusout
            return True
        elif content[0] == '0' and len(content) > 1:
            print("\a")
            return False

        elif content.isdigit() == False:
            print("\a")
            return False

        elif int(content) > 255:
            print("\a")
            return False

        else:
            return True

    def get(self):
        # data checked when input.
        value = self.entry.get()
        return value

    def set(self, ip):
        if ip == None:
            self.setEntry("0")
            return

        elif ip.isdigit() == False:
            self.setEntry("0")
            return

        elif int(ip) >= 256:
            self.setEntry("255")
            return

        else:
            self.setEntry(ip)

    def grid(self, *args, **kwargs):
        self.entry.grid(*args, **kwargs)


class IPEntry(Frame):

    def __init__(self, master, **kwargs):

        Frame.__init__(self, master, **kwargs)
        self.frame = Frame(master)
        self.master = master

        dotcmd = (self.master.register(self.KeepDotNoChange), '%P')
        self.ipv4 = []
        self.ipdot = []
        self.dotvalue = []
        for i in range(4):
            self.ipv4.append(IPV4(self.frame))
            self.ipv4[i].grid(row=0, column=i * 2)
            if i < 3:
                self.dotvalue.append(StringVar())
                self.dotvalue[i].set('.')
                self.ipdot.append(Entry(self.frame, justify=CENTER, width=1, relief='flat'))
                self.ipdot[i].grid(row=0, column=i * 2 + 1)

                self.ipdot[i]['textvariable'] = self.dotvalue[i]
                self.ipdot[i]['validate'] = 'key'
                self.ipdot[i]['vcmd'] = dotcmd

    def ipState(self, st=NORMAL):
        for i in range(4):
            self.ipv4[i].configure(state=st)
        for i in range(3):
            self.ipdot[i]['state'] = st

    def getIP(self):

        value = ""

        for i in range(4):
            temp = self.ipv4[i].get()
            if temp is None:
                return None
            else:
                value = value + temp + "."
        value = value.strip('.')  # remove last "."

        return value

    def setIP(self, ip):

        if ip == None:
            for i in range(4):
                self.ipv4[i].set('0')

        validateIP = re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", ip)

        if validateIP:
            array = ip.split('.')

            for i in range(4):
                try:
                    self.ipv4[i].set(array[i])
                except:
                    pass
        else:
            print("\a")
            pass

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)
        return

    def configure(self, *args, **kwargs):
        for i in range(4):
            self.ipv4[i].configure(*args, **kwargs)
        for i in range(3):
            self.ipdot[i].configure(*args, **kwargs)

    def KeepDotNoChange(self, content):  # keep dot nochange
        return False


if __name__ == "__main__":
    root = Tk()

    root.title("IP Widget Example")


    def setIP():
        ip2.setIP(entry1.get())
        return


    def getIP():
        value = ip2.getIP()
        entry1.delete(0, END)
        entry1.insert(0, value)
        return


    def disableIP():
        ip2.ipState(DISABLED)


    def enableIP():
        ip2.ipState(NORMAL)


    label1 = tk.Label(root, text="Normal IP Address(192.168.100.1)")
    label1.grid(row=0, column=0, sticky=E)
    ip1 = IPEntry(root)
    ip1.setIP("192.168.100.1")
    ip1.grid(row=0, column=1, padx=5, pady=5)

    label2 = tk.Label(root, text="Invalid IP address(192.304.100.288):")
    label2.grid(row=1, column=0, sticky=E)
    ip2 = IPEntry(root)
    ip2.setIP("192.304.100.288")
    ip2.grid(row=1, column=1, padx=5, pady=5)

    label3 = tk.Label(root, text="IP set or get:")
    label3.grid(row=2, column=0, sticky=E)
    entry1 = Entry(root, width=20)
    entry1.grid(row=2, column=1, padx=5, pady=5)

    btnFrm = Frame(root)
    btnAdd = tk.Button(btnFrm, text="Set IP", command=setIP)
    btnGet = tk.Button(btnFrm, text="Get IP", command=getIP)
    btnDisable = tk.Button(btnFrm, text="Disable", command=disableIP)
    btnEnable = tk.Button(btnFrm, text="Enable", command=enableIP)
    btnAdd.grid(row=0, column=0, padx=5)
    btnGet.grid(row=0, column=1)
    btnDisable.grid(row=0, column=2, padx=5)
    btnEnable.grid(row=0, column=3)

    btnFrm.grid(row=3, column=0, padx=5, pady=5)

    root.mainloop()





