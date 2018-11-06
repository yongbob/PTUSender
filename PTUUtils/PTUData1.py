# coding=utf-8
# author Marshall Bao

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import PTUUtils.PTUConfigParser as cfg
import PTUUI.PyTkinter as pytk
import sys
import tkinter.filedialog
import random

class PTUData1(object):
    '''
    create how to send message widgets:by times or by numbers
    create multiple-lines entry for data

    '''
    def __init__(self, master=None,send_config=None):
        self.send_config = send_config
        #print(send_config.config_para().info())

        self.master = master
        self.type_item = []
        self.type_value = []
        self.type_dict = []
        self.type_content={}
        self.root = pytk.PyLabelFrame(self.master,text='消息设置',padx=2)
        self.root.grid(row=0,column=0)
        self.frm_send_para = pytk.PyLabelFrame(self.master, text= '发送参数')
        self.frm_send_para.grid(row=1, column=0, sticky=tk.W)
        self.conf = cfg.PTUConfigParser()
        self.current_path = sys.path[0]
        self.config_file_name = self.current_path + "\config.ini"
        try:
            self.conf.read(filenames=self.config_file_name)
        except:
            tk.messagebox.showerror('错误', '打开config.ini失败')

        if self.conf.has_section('logtext') == False:
            self.add_logtext()
            self.conf.read(filenames=self.config_file_name)


        self.type_dict = self.conf.items('logtext')

        self.create_data_frm()

    def create_data_frm(self):

        self.data_source_label = pytk.PyLabel(self.root,text='消息来源')
        self.data_source_label.grid(row=0,column=0,ipadx=2,pady=10)

        self.send_file_type = tk.IntVar()
        self.send_file_name = tk.StringVar()

        self.data_filename_entry = pytk.PyEntry(self.root, width=63,textvariable=self.send_file_name,state='readonly')
        self.data_filename_entry.grid(row=1,column=0,columnspan=4,pady=5)

        self.data_filename_btn = pytk.PyButton(self.root,text='...',width=10, command=self.data_openfile)
        self.data_filename_btn['state']='disabled'
        self.data_filename_btn.grid(row=1,column=4,padx=10)

        self.radio_send_order=pytk.PyRadiobutton(self.root, text="按顺序读",
                                                 variable=self.send_file_type,
                                                 value=0,command=self.radio_order,
                                                 state='disabled')
        self.radio_send_order.grid(row=2,column=3,sticky=tk.E)
        self.radio_send_random=pytk.PyRadiobutton(self.root, text="随机读",
                                                  variable=self.send_file_type,
                                                  value=1,command=self.radio_random,
                                                  state='disabled')
        self.radio_send_random.grid(row=2,column=4,sticky=tk.W)
        self.send_file_type.set(0)

        self.data_source = ttk.Combobox(self.root) #, textvariable=self.data_source_name)
        self.data_source["values"] = ('从文本框', '从文件')
        self.data_source.current(0)
        self.data_source.bind("<<ComboboxSelected>>", self.data_source_change)
        #self.data_source.focus()
        self.data_source["state"] = "readonly"
        self.data_source.grid(row=0,column=1)
        self.data_type_label = pytk.PyLabel(self.root,text='选择日志样本：')
        self.data_type_label.grid(row=0,column=2)

        self.data_type=ttk.Combobox(self.root)
        self.add_data_type()
        self.data_type.grid(row=0,column=3)
        self.data_type.bind("<<ComboboxSelected>>", self.data_type_change)

        self.data_clear = pytk.PyButton(self.root,text="清空",width=10,command=self.clear_data)
        self.data_clear.grid(row=0,column=4)

        self.frm_text = pytk.PyFrame(self.root)
        self.frm_text.grid(row=3,column=0,columnspan=5)
        self.data_type_text = pytk.PyText(self.frm_text,width=80,height=8,wrap=tk.NONE)
        self.data_type_text.grid(row=0,column=0,ipadx=5,pady=10,sticky=tk.E)

        self.data_type_vbar = tk.Scrollbar(self.frm_text)
        self.data_type_vbar.grid(row=0,column=1,sticky=tk.N+tk.S+tk.W,pady=10)
        self.data_type_vbar.configure(command=self.data_type_text.yview)
        self.data_type_hbar = tk.Scrollbar(self.frm_text, orient=tk.HORIZONTAL)
        self.data_type_hbar.grid(row=1, column=0, columnspan=2, sticky=tk.E + tk.W)
        self.data_type_hbar.configure(command=self.data_type_text.xview)

        self.data_type_text.delete(1.0, tk.END)
        self.data_type_text.insert(tk.END, self.type_content[self.data_type.get()])


        self.label_send_para = pytk.PyLabel(self.frm_send_para,text=self.send_config.config_para().info())
        self.label_send_para.grid(row=0,column=0,sticky=tk.W)


    def add_data_type(self):
        self.read_log_file()
        self.data_type['values'] = self.type_item
        self.data_type['state']='readonly'

        self.data_type.current(2)

    def data_type_change(self,*args):
        self.data_type_text.delete(1.0, tk.END)
        self.data_type_text.insert(tk.END, self.type_content[self.data_type.get()])
        #print(*args)

    def data_source_change(self,*args):
        item = self.data_source.get()
        if item == '从文本框':
            self.data_filename_btn['state']='disabled'
            self.data_filename_entry['state']='disabled'
            self.radio_send_random['state']='disabled'
            self.radio_send_order['state']='disabled'

            self.data_type['state']='normal'
            #self.data_type_text['state']='normal'
            self.data_clear['state']='normal'

        elif item == '从文件':
            self.data_filename_btn['state']='normal'
            self.data_filename_entry['state']='normal'
            self.radio_send_random['state'] = 'normal'
            self.radio_send_order['state'] = 'normal'

            self.data_type['state'] = 'disabled'
            #self.data_type_text['state'] = 'disabled'
            self.data_clear['state']='disabled'

    def read_log_file(self):
        self.type_item = []
        self.type_value = []
        self.type_content = {}
        for item,value in self.type_dict:
            self.type_item.append(item)
            self.type_value.append(value)
            # read .txt files
            self.type_content[item]=self.read_txt(item,value,False)
            #print(self.type_content)
    # read log message from file
    # support multiple lines
    def data_openfile(self):
        self.send_file_name.set( tk.filedialog.askopenfilename())
        self.from_file()
        #print (self.send_file_name)

    def radio_order(self):
        print(self.send_file_type.get())

    def radio_random(self):
        print(self.send_file_type.get())
        pass

    def read_txt(self,item,filename,action):
        # check for filename in pre-define list
        t_type = ""
        if action == False:
            # check for filename exists
            try:
                fh = open(self.current_path+"\\"+filename)
                for eachline in fh:
                    t_type = t_type+eachline
                fh.close()
                return t_type
            except FileNotFoundError:
                #tk.messagebox.showerror('错误','No '+filename+". Will create it")
                action = True

        if item == 'Fortinet-1':
            t_type = 'date=2005-07-25,time=09:25:26,device_id=APS3012801012028,' \
                     'log_id=0001000002,type=traffic,subtype=session,pri=notice,' \
                     'SN=7590956,duration=180,policyid=1,proto=17,service=53/udp,' \
                     'status=accept,src=192.168.3.123,srcname=192.168.3.123,dst=202.106.0.20,' \
                     'dstname=202.106.0.20,src_int=internal,dst_int=external,sent=60,rcvd=181,' \
                     'sent_pkt=1,rcvd_pkt=1,src_port=4664,dst_port=53,vpn=n/a,' \
                     'tran_ip=211.167.237.137,tran_port=39540,'
        elif item =='Fortinet-2':
            t_type='date=2005-07-25,time=09:25:26,device_id=APS3012801012028,log_id=0400000000,' \
                   'type=ids,subtype=detection,pri=alert,attack_id=287113220,,src=192.168.25.1,dst=192.168.25.3,' \
                   'src_port=43323,dst_port=161,src_int=n/a,dst_int=n/a,status=detected,proto=17,' \
                   'service=161/udp,msg="SNMP public access udp[Reference: http://www.fortinet.com/ids/ID287113220]"'
        elif item== "Huawei":
            t_type="<189>Jun 7 05:22:03 2003 Quidway IFNET/6/UPDOWN:Line protocol on " \
                   "interface Ethernet0/0/0, changed state to UP"
        elif item=='Kill':
            t_type='发现DOShunt病毒在 C:\SHARE\ATOZVIRUS.病毒包\DOSHUNTE\DOSHUNTE.COM. ' \
                   '机器: TESTFORKILL, 用户: 系统. 文件状态: 已感染'
        elif item == "Linux":
            t_type="xinetd[3469]: START: cvspserver pid=16386 from=192.168.17.188"
        elif item == 'NetscrrenAdm':
            t_type='ns204: NetScreen device_id=ns204 [No Name] (2005-12-20 192.168.3.22) alert-00027 ' \
                   'login failures occurred for user root from IP address 192.168.24.110:8080'
        elif item=='NetscreenTraff':
            t_type='ns204: NetScreen device_id=ns204  [No Name]system-notification-00257(traffic): ' \
                   'start_time="2005-11-15 16:27:55" duration=4 policy_id=5 service=tcp/port:501 ' \
                   'proto=6 src zone=V1-Untrust dst zone=V1-Trust action=Permit sent=198 rcvd=192 ' \
                   'src=192.168.24.165 dst=192.168.24.233 src_port=1573 ' \
                   'dst_port=501 src-xlated ip=192.168.24.165 port=1573'
        elif item == 'PIX':
            t_type = '%PIX-7-710005: UDP request discarded from 192.168.24.181/137 to inside:192.168.24.255/netbios-ns'
        elif item=='Snort':
            t_type='snort: [122:19:0] (portscan) UDP Portsweep {PROTO255} 192.168.17.253 -> 192.168.17.50'
        elif item=='Solaris':
            t_type='sshd[23538]: Received disconnect from ::ffff:192.168.17.50: 11: Disconnect requested by Windows SSH Client.'

        elif item=='Topsec4000':
            t_type='id=firewall time="2005-07-29 10:57:16" fw=TOPSEC pri=3 recorder=kernel ' \
                   'type=ids proto=TCP rule=deny src=192.168.25.1 sport=59393 ' \
                   'dst=192.168.25.2 dport=80 smac=00:10:f3:04:77:db'
        elif item=='Topsec4000Adm':
            t_type='May 30 18:38:06 fw_proxy:id=firewall time="2005-5-30 18:38:6" fw=192.168.1.116 ' \
                   'pri=4 type=mgmt recorder=fw_proxy  msg=ShellCmd(): fork() ERROR'
        elif item=='VenusAuditP':
            t_type='Jan 9 10:26:04 192.168.4.185 VENUS_AUDIT: type=audit time=2006-01-09 10:24:32 ' \
                   'engine_ip=192.168.4.125 src_ip=192.168.4.123 dst_ip=192.168.3.166 src_port=1785 ' \
                   'dst_port=23 src_mac=00:0e:0c:5e:7b:f1 dst_mac=00:02:b3:3e:e9:ed  user_id=10 ' \
                   'user_type=0 service_role_id=99 proto_id=10 action_mode=1 alarm_mode=1 log_level=1 ' \
                   'param_len=14 param=Telnet输入=ls;'
        elif item=='VenusAuditS':
            t_type='Jan 9 10:04:53 192.168.4.185 VENUS_AUDIT: type=sign time=2006-01-09 10:12:43 ' \
                   'engine_ip=192.168.4.125 src_ip=192.168.3.166 dst_ip=192.168.4.123 src_port=23 ' \
                   'dst_port=1052 src_mac=00:02:b3:3e:e9:ed dst_mac=00:0e:0c:5e:7b:f1 trans_' \
                   'proto_id=5 rule_id=187 proto_id=10 start_time=0 end_time=0 user_id=10 user_type=0 ' \
                   'policy_id=93 service_role_id=99 evt_set_id=100 action_mode=1 alarm_mode=1 ' \
                   'log_level=1 param_len=44 param=Telnet=root enginaix hello slowaction exit;'
        elif item=='VenusIDS':
            t_type='sub:TDS_MS-SQL_口令弱;se:30;sr:192.168.3.144;sport:0;dest:192.168.3.44;' \
                   'dport:0;proto:null;param:用户名称=sa;用户口令=123456;;time:2005-4-19_11:46:35'
        elif item == "绿盟NIPS1":
            #print('sfsdfsd')
            t_type = "NIDS 中联绿盟信息技术(北京)有限公司 冰之眼入侵检测系统V3 " \
                     "131073 192.168.1.201 192.168.1.107 00:11:25:83:93:5C 00:07:E9:10:7A:BE " \
                     "FTP服务anonymous匿名用户认证 失败 失败 " \
                     "VENQLkZUUG5TZjBDdXNDblNmMEN1c1VTRVI9YW5vbnltb3Vz " \
                     "网络监控类功能 事件监控 低 高 FTP"
        elif item=='绿盟NIPS2':
            t_type='NIDS 中联绿盟信息技术(北京)有限公司 冰之眼入侵检测系统V3 131073 192.168.1.201 ' \
                   '192.168.1.107 00:11:25:83:93:5C 00:07:E9:10:7A:BE Windows ' \
                   'SMB枚举系统用户帐号列表操作 未知 QW55blNmMEN1c0M= 信息收集类攻击 事件监控 中 高 Samba'
        else:
            tk.messagebox.showerror("错误",'无法打开文件'+filename)
            return ''
        #for new files
        try:
            with open(self.current_path+"\\"+filename,'w') as fh:
                fh.write(t_type)
            fh.close()
        except :
            tk.messagebox.showerror("错误", '无法写入文件' + filename)

        return t_type

    def clear_data(self):
        self.data_type_text.delete(1.0,tk.END)
        self.data_type_text.see(tk.END)
        self.data_type_text.update()
    def add_logtext(self):
        #add log text and files
        self.conf.add_section('logtext')
        t_logname=('Fortinet-1','Fortinet-2','Huawei','Kill','Linux','NetscrrenAdm',
                   'NetscreenTraff','PIX','Snort','Solaris','Topsec4000','Topsec4000Adm',
                   'VenusAuditP','VenusAuditS','VenusIDS','绿盟NIPS1','绿盟NIPS2')
        for item in t_logname:
            self.conf.set('logtext',item,item+'.txt')
            self.type_content[item]=self.read_txt(item,item+".txt",True)
        self.save_config()

    def save_config(self):
        try:
            with open(self.config_file_name, 'w+') as fw:
                self.conf.write(fw)
            fw.close()
        except:
            tk.messagebox.showerror('错误', '写入config.ini失败')

    def update_send_para(self):
        self.label_send_para.configure(text=self.send_config.config_para().info())

    def get_ip(self):
        return self.send_config.config_para().get_ip()

    def get_port(self):
        return self.send_config.config_para().get_port()

    def get_method(self):
        return self.send_config.config_para().get_method()
    def get_method_para(self):
        return self.send_config.config_para().get_method_para()

    def get_data(self):
        #t = []
        t = self.data_type_text.get(1.0,tk.END).split('\n')
        while '' in t:
            t.remove('')
        return t

        '''
        print("=======",l)
        if isinstance(l, list):
            for m in l:
                m = m.strip()
                if m:
                    t.append(m)
        elif isinstance(l, str):
            m = l.strip()
            if m:
                t.append(l.strip())
        else:
            pass
        print("------",t)
        return t
        '''
    def from_file(self):
        t=[]
        self.clear_data()
        file_name = self.send_file_name.get()
        if file_name == "":
            tk.messagebox.showerror("错误", "文件名不能为空")
        try:
            fh = open(file_name, "r")
            lines = fh.readlines()
            for l in lines:
                l = l.strip()
                if l:
                    t.append(l.rstrip())
            fh.close()
        except:
            tk.messagebox.showerror("错误", "不能打开文件：" + file_name)
        if self.send_file_type.get() == 1:
            random.shuffle(t)
        for each in t:
            self.data_type_text.insert(tk.END,each+"\n")


if __name__ == '__main__':
    '''
    main loop
    '''
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry()
    root.title("PTU Sender")

    PTUData1(root)

    root.mainloop()
