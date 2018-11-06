# coding:gbk
# author: Marshall Bao
import PTUUtils.PTUConfigParser as cfg
import sys
import PTUUI.PyTkinter as pytk
import tkinter as tk
import tkinter.ttk as ttk
import PTUUI.PTUIPDialog as ipdialog
import PTUUtils.PTUPing as ping
import PTUUtils.PTUCommon as common
import PTUUtils.PTUType as ptype
from concurrent.futures import ThreadPoolExecutor
import threading


g_font = ('Monaco', 9)


class PTUConfigFrm(object):
    def __init__(self, master=None):
        self.root = master
        self.create_frame()
        #self.log = None
        self.logaction = True
        self.config_dict = None

    def create_frame(self):
        '''
        创建Config窗体
        root 为PTUFrm.frm_config
        '''

        self.frm_send_config = pytk.PyLabelFrame(self.root)  # 发送方式设置
        self.create_send_config()
        self.frm_send_config.grid(row=0, column=1)

    def create_send_config(self):
        self.radio_intvar = tk.IntVar()
        self.radio_log_intvar = tk.IntVar()
        self.send_num_entry_var = tk.IntVar()
        self.send_freq_entry_var = tk.IntVar()
        self.thread_num_entry_var = tk.IntVar()
        # read server info from config.ini
        # if no config.ini, create and set default server as 127.0.0.1 and port is 514
        self.dict_server = ()
        self.conf = cfg.PTUConfigParser()
        self.config_file_name = sys.path[0] + "\config.ini"
        try:
            self.conf.read(filenames=self.config_file_name)
        except:
            tk.messagebox.showerror('错误', '打开config.ini失败')

        if self.conf.has_section('server') == False:
            self.conf.add_section('server')
            self.conf.set('server', 'server_0', '127.0.0.1:514')
            self.save_config()
            # insert 127.0.0.1:514 as default one
            # self.dict_server.append(('server_0','127.0.0.1:514'))
        if self.conf.has_section('config') == False:
            self.conf.add_section('config')
            self.conf.set('config', '线程数量', '20')
            self.save_config()
            self.thread_num = 20
        else:
            self.thread_num = self.conf.getint('config', '线程数量')

        common.g_ex = ThreadPoolExecutor(self.thread_num)

        self.frm_send_type = pytk.PyLabelFrame(self.frm_send_config, text='发送设置')
        pytk.PyLabel(self.frm_send_type, text='方式：', font=g_font).grid(row=0, column=0)

        self.radio_send_number = pytk.PyRadiobutton(self.frm_send_type, text="按次数发送",
                                                    variable=self.radio_intvar, value=0, command=self.RadioNum,
                                                    font=g_font)
        self.radio_send_number.grid(row=0, column=1, sticky=tk.W)
        self.radio_send_freq = pytk.PyRadiobutton(self.frm_send_type, text="按速度发送",
                                                  variable=self.radio_intvar, value=1, command=self.RadioFreq,
                                                  font=g_font)
        self.radio_send_freq.grid(row=0, column=2, sticky=tk.W)

        self.entry_send_num = pytk.PyEntry(self.frm_send_type, width=10,
                                           textvariable=self.send_num_entry_var,
                                           relief="sunken", state='normal',
                                           font=g_font)
        self.entry_send_freq = pytk.PyEntry(self.frm_send_type, width=10,
                                            textvariable=self.send_freq_entry_var,
                                            relief="sunken", state='disabled',
                                            font=g_font)

        self.send_num_entry_var.set('1')
        self.send_freq_entry_var.set('100')
        pytk.PyLabel(self.frm_send_type, text='次/秒', font=g_font).grid(row=1, column=3, sticky=tk.W, pady=3)
        self.radio_intvar.set(0)
        self.entry_send_num.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.entry_send_freq.grid(row=1, column=2, padx=5, sticky=tk.W)
        ''' send configuration end '''
        self.frm_send_type.grid(row=0, column=0, sticky=tk.W, ipadx=5, ipady=5, padx=3, pady=3)

        ''' 
        for log print setting
        '''
        self.frm_send_log = pytk.PyLabelFrame(self.frm_send_config, text='日志选择')
        self.radio_send_log_on = pytk.PyRadiobutton(self.frm_send_log, text="打印日志",
                                                    variable=self.radio_log_intvar, value=0, command=self.print_log,
                                                    font=g_font)
        self.radio_send_log_on.grid(row=0, column=0, sticky=tk.W)
        self.radio_send_log_off = pytk.PyRadiobutton(self.frm_send_log, text="不打印日志",
                                                     variable=self.radio_log_intvar, value=1, command=self.no_log,
                                                     font=g_font)
        self.radio_send_log_off.grid(row=1, column=0, sticky=tk.W)
        self.radio_log_intvar.set(0)
        self.frm_send_log.grid(row=0, column=1, sticky=tk.W, ipadx=5, ipady=5, padx=3, pady=3)

        validatecmd = (self.frm_send_config.register(self.check_thread_num), '%P')
        self.frm_thread_num = pytk.PyLabelFrame(self.frm_send_config, text='系统设置')
        pytk.PyLabel(self.frm_thread_num, text='线程数量:', font=g_font).grid(row=0, column=0, pady=5, sticky=tk.W)
        pytk.PyButton(self.frm_thread_num,text='保存',font=g_font,
                      command=self.save_thread_num,width=10).grid(row=0,column=1)
        self.entry_thread_num = pytk.PyEntry(self.frm_thread_num, width=15,
                                             textvariable=self.thread_num_entry_var,
                                             validate='key', vcmd=validatecmd,
                                             relief="sunken", font=g_font)
        self.thread_num_entry_var.set(self.thread_num)

        self.entry_thread_num.grid(row=1, column=0, columnspan=2,sticky=tk.W + tk.E)
        self.frm_thread_num.grid(row=0, column=2, sticky=tk.W, ipadx=5, ipady=5, padx=3, pady=3)

        self.frm_server = pytk.PyLabelFrame(self.frm_send_config, text='服务器和端口设置')
        self.tree_ip_port = ttk.Treeview(self.frm_server,
                                         show="headings", height=8, columns=("a", "b", "c"))
        self.tree_ip_port.column("a", width=20, anchor="center")
        self.tree_ip_port.column("b", width=200, anchor="center")
        self.tree_ip_port.column("c", width=200, anchor="center")
        self.tree_ip_port.heading("a", text="#")
        self.tree_ip_port.heading("b", text="目标IP地址")
        self.tree_ip_port.heading("c", text="目标端口")
        # self.tree_ip_port.insert("", 0, values=("0", "127.0.0.1", "162"))
        t_dict = self.conf.items('server')
        for (item, value) in t_dict:
            t_index = item.split('_')[1]
            t_ip, t_port = value.split(':')
            self.tree_ip_port.insert('', 'end', values=(t_index, t_ip, t_port))

        self.tree_ip_port.grid(row=0, rowspan=4, column=0)
        self.tv_vbar = ttk.Scrollbar(self.frm_server, orient=tk.VERTICAL, command=self.tree_ip_port.yview)
        self.tree_ip_port.configure(yscrollcommand=self.tv_vbar.set)
        self.tv_vbar.grid(row=0, rowspan=4, column=1, sticky=tk.N + tk.S)

        self.btn_ping_ip = pytk.PyButton(self.frm_server, text="Ping", width=10, font=g_font, command=self.PingIP)
        self.btn_ping_ip.grid(row=0, column=2, padx=(15, 5))

        self.btn_add_ip_port = pytk.PyButton(self.frm_server, text="添加", width=10, font=g_font, command=self.AddIP)
        self.btn_add_ip_port.grid(row=1, column=2, padx=(15, 5))

        self.btn_edit_ip_port = pytk.PyButton(self.frm_server, text="编辑", width=10, font=g_font, command=self.EditIP)
        self.btn_edit_ip_port.grid(row=2, column=2, padx=(15, 5))

        self.btn_del_ip_port = pytk.PyButton(self.frm_server, text="删除", width=10, font=g_font, command=self.DelIP)
        self.btn_del_ip_port.grid(row=3, column=2, padx=(15, 5))

        self.tree_ip_port.selection_set(('I001',))
        '''server frame end'''
        self.frm_server.grid(row=1, column=0, columnspan=3)

    def check_thread_num(self, content):
        # just input digit
        if content.isdigit() or content == "":
            return True
        else:
            return False

    def save_thread_num(self):

        self.conf.set('config', '线程数量', str(self.thread_num_entry_var.get()))
        self.save_config()

    def save_config(self):
        try:
            with open(self.config_file_name, 'w+') as fw:
                self.conf.write(fw)
        except:
            tk.messagebox.showerror('错误', '写入config.ini失败')

    def RadioNum(self):
        self.radio_intvar.set(0)
        self.entry_send_num['state'] = 'normal'
        self.entry_send_freq['state'] = 'disabled'

    def RadioFreq(self):
        self.radio_intvar.set(1)
        self.entry_send_num['state'] = 'disabled'
        self.entry_send_freq['state'] = 'normal'

    def AddIP(self):
        self.dialog = ipdialog.PTUIPDialog()
        self.root.wait_window(self.dialog)
        if self.dialog.ipinfo == None:
            pass
        else:
            lastitem = len(self.tree_ip_port.get_children())
            t_ip = self.dialog.ipinfo[0]
            t_port = self.dialog.ipinfo[1]
            self.tree_ip_port.insert("", 'end', values=(lastitem, t_ip, t_port))
            # edit config.ini
            # self.dict_server.append(('server_'+str(lastitem),t_ip+':'+t_port))
            self.conf.set('server', 'server_' + str(lastitem), t_ip + ':' + t_port)
            self.save_config()
    def do_ping(self,ph):
        ph.ping()

    def PingIP(self):
        item = self.tree_ip_port.selection()
        # print(item)
        if item:
            values = self.tree_ip_port.item(item, "values")
            p = ping.CheckServer(values[1], self.logaction )

            common.g_ex.submit(self.do_ping,p)
            #t = threading.Thread(target=p.ping())
            #t.start()
            '''
            if result > 0:
                common.g_printthread.submit(common.print_log,self.log, values[1] + " status: OK")
            else:
                common.g_printthread.submit(common.print_log,self.log, values[1] + " status: no response")
            '''
        else:
            # alter for no selection
            tk.messagebox.showerror('错误', '请选择一个IP地址')

    def EditIP(self):
        item = self.tree_ip_port.selection()
        if item:
            values = self.tree_ip_port.item(item, "values")
            self.dialog = ipdialog.PTUIPDialog(values[1], values[2])
            self.root.wait_window(self.dialog)
            if self.dialog.ipinfo == None:
                pass
            else:
                t_ip = self.dialog.ipinfo[0]
                t_port = self.dialog.ipinfo[1]

                self.tree_ip_port.item(item, values=(values[0], t_ip, t_port))
                # self.dict_server.append(('server_' + values[0], t_ip + ':' + t_port))
                self.conf.set('server', 'server_' + values[0], t_ip + ':' + t_port)
                self.save_config()
        else:
            # alter for no selection
            tk.messagebox.showerror('错误', '请选择一个IP地址和端口')

    def DelIP(self):
        item = self.tree_ip_port.selection()
        if item:

            self.tree_ip_port.delete(item)
            all_items = self.tree_ip_port.get_children()
            index = 0
            # clear section server
            self.conf.remove_section('server')
            self.conf.add_section('server')

            for item in all_items:
                values = self.tree_ip_port.item(item, "values")
                # values[0]=index
                self.tree_ip_port.set(item, column=0, value=index)
                self.conf.set('server', 'server_' + str(index), values[1] + ':' + values[2])
                index = index + 1
            self.save_config()

        else:
            tk.messagebox.showerror('错误', '请选择一个IP地址和端口')

    #def setloghandler(self, loghandler):
    #    self.log = loghandler

    #def get_loghandler(self):
    #    return self.log

    def logon(self, logaction):
        self.logaction = logaction

    def print_log(self):
        self.logaction = True

    def no_log(self):
        self.logaction = False

    def config_para(self):
        item = self.tree_ip_port.selection()[0]
        values = self.tree_ip_port.item(item, "values")
        method = ('按次发送', '按速度发送')
        method_para = (self.send_num_entry_var.get(), self.send_freq_entry_var.get())
        n = self.radio_intvar.get()
        log = ('打印日志', '不打印日志')
        m = self.radio_log_intvar.get()
        self.config_dict = ptype.ConfigDict(ip=values[1], port=values[2], method=method[n],
                                            method_para=method_para[n], log=log[m])
        return self.config_dict
