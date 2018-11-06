# coding=gbk
# Notification Originator Application (TRAP)
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import encoder
from pysnmp.proto import api
from pyasn1.type import univ, constraint
import datetime
import tkinter.messagebox
import PTUUtils.PTUCommon as common
import time
import threading
'''
def sendsnmp(udpconfig):
    snmptype = PSNMPConfig.getsnmptype()

    if snmptype == 1:  # snmp version 1
        pass
    elif snmptype == 2:  # snmp version 2c
        s = sendSNMPV2(udpconfig)
        s.send()
    else:  # snmp version 3
        pass
'''
'''
class PTUSNMPV2(object):
    def __init__(self, udpconfig):
        print(udpconfig)
        self.data = udpconfig.get_data()
        self.send_flag=True

        if self.data:
            self.udpconfig = udpconfig
        else:
            tkinter.messagebox.showerror("错误", "发送数据不能为空")
            self.send_flag=False

    def timeticks(self):
        #upday = self.udpconfig.getupday()
        upday=100
        tdy = datetime.datetime.now()

        return (((upday * 24 + tdy.hour) * 60 + tdy.minute) * 60 + tdy.second) * 100 + tdy.microsecond % 100

    def getobjid(self):
        return ((1, 3, 6, 1, 6, 3, 1, 1, 5, 1))

    def send(self):
        t = self.udpconfig.get_data()
        #print (len(t))
        for i in t:
            self._send(i)

    def _send(self,data):
        # Protocol version to use
        verID = api.protoVersion2c
        pMod = api.protoModules[verID]
        # Build PDU
        trapPDU = pMod.TrapPDU()
        pMod.apiTrapPDU.setDefaults(trapPDU)

        # Traps have quite different semantics among proto versions
        var = []

        oid = pMod.apiTrapPDU.sysUpTime
        val = pMod.TimeTicks(self.timeticks())
        var.append((oid, val))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

        oid = pMod.apiTrapPDU.snmpTrapOIDSNMP
        genTrap = univ.ObjectIdentifier(self.getobjid())
        var.append((oid, genTrap))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

        oid = (1, 3, 6, 1, 4, 1, 4, 2, 6)
        val = pMod.OctetString(data.encode('utf-8'))
        var.append((oid, val))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

        # Build message
        trapMsg = pMod.Message()
        pMod.apiMessage.setDefaults(trapMsg)
        pMod.apiMessage.setCommunity(trapMsg, 'public')
        pMod.apiMessage.setPDU(trapMsg, trapPDU)

        transportDispatcher = AsynsockDispatcher()
        transportDispatcher.registerTransport(
            udp.domainName, udp.UdpSocketTransport().openClientMode()
        )
        #print(self.udpconfig.get_ip(), self.udpconfig.get_port())
        transportDispatcher.sendMessage(
            encoder.encode(trapMsg), udp.domainName, (self.udpconfig.get_ip(), int(self.udpconfig.get_port()))
        )
        transportDispatcher.runDispatcher()
        transportDispatcher.closeDispatcher()
'''

upday = 397
tdy = datetime.datetime.now()

upintdy = (((upday*24+tdy.hour)*60 + tdy.minute)*60+tdy.second)*100+tdy.microsecond % 100
def snmp2(msg):
    # Protocol version to use
    verID = api.protoVersion2c
    pMod = api.protoModules[verID]

    # Build PDU
    trapPDU = pMod.TrapPDU()
    pMod.apiTrapPDU.setDefaults(trapPDU)

    # Traps have quite different semantics among proto versions
    if verID == api.protoVersion2c:
        var = []
        oid = pMod.apiTrapPDU.sysUpTime
        val = pMod.TimeTicks(upintdy)
        var.append((oid, val))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

        oid = pMod.apiTrapPDU.snmpTrapOID
        genTrap = univ.ObjectIdentifier((1, 3, 6, 1, 6, 3, 1, 1, 5, 1))
        var.append((oid, genTrap))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

        oid = (1, 3, 6, 1, 4, 1, 4, 2, 6)
        val = pMod.OctetString(msg.encode('utf-8'))
        var.append((oid, val))
        pMod.apiTrapPDU.setVarBinds(trapPDU, var)

    # Build message
    trapMsg = pMod.Message()
    pMod.apiMessage.setDefaults(trapMsg)
    pMod.apiMessage.setCommunity(trapMsg, 'public')
    pMod.apiMessage.setPDU(trapMsg, trapPDU)

    return trapMsg
def _send(*args,**kwargs):
    data = args[0]
    ip = args[1]
    port = int(args[2])
    transportDispatcher = args[3]
    #print(args)
    try:
        transportDispatcher.sendMessage(
            encoder.encode(data), udp.domainName, (ip, int(port))
        )
        transportDispatcher.runDispatcher()
    except Exception as e:
        common.g_printthread.submit(common.print_log, "socket error:" + e)

def send_para(*args):
    return ": Server= "+args[0]+" Port="+args[1]+" 发送方法="+args[2]+" 发送参数="+args[3]

def send_by_timer(*args,**kwargs):
    method_para = args[0]
    data = args[1]
    data_len = len(data)
    ip = args[2]
    port = args[3]
    t = common.g_snmp_timer.get_counter()*method_para % data_len
    #print(t)

    for i in range(method_para):
        #print(str(i)+data[(i+t) % data_len])
        if common.g_ex._work_queue.qsize() < common.g_total_tasks:
            try:
                if common.g_thread_running:

                    all_tasks = [common.g_ex.submit(_send, data[(i+t) % data_len], ip,port,common.g_snmp_transportDispatcher)]
            except Exception as e:
                common.g_printthread.submit(common.print_log, e)
                print(e)
    if common.g_ex._work_queue.qsize() < common.g_total_tasks:
        try:
            common.g_threadpool_result.submit(common.wait_for_done, all_tasks, "结束发送" + str(method_para) + "条 SNMP 记录")
        except Exception as e:
            common.g_printthread.submit(common.print_log, e)
            print(e)


def sendsnmp(udpconfig):
    # get SNMP message
    t_list = udpconfig.get_data()
    snmpdata = []
    for i in t_list:
       snmpdata.append(snmp2(i))

    #snmpdata = map(snmp2,t_list)
    method = udpconfig.get_method()
    method_para = int(udpconfig.get_method_para())
    ip = udpconfig.get_ip()
    port = udpconfig.get_port()

    data_len = len(snmpdata)

    if not snmpdata:
        tkinter.messagebox.showerror("错误", "发送数据不能为空")
        return False

    #if send_type == 按次发送
    #check for socket in common.g_snmp_pool
    #ip+port  is the key.
    #[socket,start_time] is the value
    #if the key is existed, for 按次发送 will do nothing
    #else create new socket.

    #else will replace the socket in dict.
    key = ip+":"+ str(port)
    if method == '按次发送':
        if key in common.g_snmp_pool:
            pass
        else:
            #create new socket
            common.g_socket_lock.acquire()
            try:
                transportDispatcher = AsynsockDispatcher()
                transportDispatcher.registerTransport(
                    udp.domainName, udp.UdpSocketTransport().openClientMode()
                )
                common.g_snmp_pool[key]=[transportDispatcher,ip,port,time.time()]
            finally:
                common.g_socket_lock.release()
        for i in range(0,method_para):
            try:
                if common.g_thread_running:
                    all_tasks=[common.g_ex.submit(_send,snmpdata[i % data_len],ip,port,common.g_snmp_pool[key][0])]
            except Exception as e:
                if common.g_thread_running:
                    common.g_printthread.submit(common.print_log, e)
                print(e)

        try:
            if common.g_thread_running:
                common.g_threadpool_result.submit(common.wait_for_done,all_tasks,"结束发送"+str(method_para)+"条 SNMP记录")
        except Exception as e:
            if common.g_thread_running:
                common.g_printthread.submit(common.print_log, e)
            print(e)
    else:
        common.g_snmp_timer.pause()
        #replace socket
        common.g_snmp_transportDispatcher.closeDispatcher()
        common.g_snmp_transportDispatcher=AsynsockDispatcher()
        common.g_snmp_transportDispatcher.registerTransport(
                    udp.domainName, udp.UdpSocketTransport().openClientMode()
                )

        common.g_snmp_timer.set_function(send_by_timer)
        common.g_snmp_timer.set_args(method_para, snmpdata, ip,port)
        common.g_snmp_timer.resume()

    #pring send log information
    t = send_para(ip,str(port),method,str(method_para))
    if common.g_thread_running:
        common.g_printthread.submit(common.print_log,"开始发送"+t+"SNMP 记录")
