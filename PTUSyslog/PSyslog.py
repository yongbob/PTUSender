# coding=utf-8

import socket
import tkinter.messagebox
import PTUUtils.PTUCommon as common
import time

FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}
LEVEL = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}
SEND_TYPE = {
    'normal':0,
    'row':1
}

'''
def MySyslog(message, level=LEVEL['notice'], facility=FACILITY['daemon'],
           host='localhost', port=514,type=SEND_TYPE['normal']):

    host = '10.1.23.2'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility * 8, message)

    sock.sendto(data.encode("utf-8"), (host, port))
    sock.close()

def create_socket(host='localhost',ip=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock
'''
#syslog("message", level=LEVEL['warning'], facility=FACILITY['auth'])

def _send(*args,**kwargs):
    data = args[0]
    ip = args[1]
    port = int(args[2])
    sock = args[3]
    #print(args)
    try:
        sock.sendto(data.encode("utf-8"), (ip, port))
    except socket.error as e:
        common.g_printthread.submit(common.print_log, "socket error:" + e)
'''
def _send_timer(*args,**kwargs):
    data = args[0]
    ip = args[1]
    port = args[2]
    try:
        common.g_sysloghandler.sendto(data.encode("utf-8"), (ip, port))
    except socket.error as e:
        common.g_printthread.submit(common.print_log, "socket error:" + e)
'''
def send_para(*args):
    return "Syslog: Server= "+args[0]+" Port="+args[1]+" 发送方法="+args[2]+" 发送参数="+args[3]

def send_by_timer(*args,**kwargs):
    method_para = args[0]
    data = args[1]
    data_len = len(data)
    ip = args[2]
    port = args[3]
    t = common.g_syslog_timer.get_counter()*method_para % data_len
    #print(t)

    for i in range(method_para):
        #print(str(i)+data[(i+t) % data_len])
        try:
            all_tasks = [common.g_ex.submit(_send, data[(i+t) % data_len], ip,port,common.g_sysloghandler)]
        except Exception as e:
            common.g_printthread.submit(common.print_log, e)
            print(e)
    try:
        common.g_threadpool_result.submit(common.wait_for_done, all_tasks, "结束发送" + str(method_para) + "条 Syslog 日志")
    except Exception as e:
        common.g_printthread.submit(common.print_log, e)
        print(e)


def sendsyslog(udpconfig):
    # get Syslog message
    syslogdata = udpconfig.get_data()
    method = udpconfig.get_method()
    method_para = int(udpconfig.get_method_para())
    ip = udpconfig.get_ip()
    port = udpconfig.get_port()

    data_len = len(syslogdata)

    if not syslogdata:
        tkinter.messagebox.showerror("错误", "发送数据不能为空")
        return False

    #syslogger = logging.getLogger()

    #sysloghandler = MySysLogHandler((udpconfig.get_ip(), int(udpconfig.get_port())))
    #if send_type == 按次发送
    #check for socket in common.g_socket_pool
    #ip+port  is the key.
    #[socket,start_time] is the value
    #if the key is existed, for 按次发送 will do nothing
    #else create new socket.

    #else will replace the socket in dict.
    key = ip+":"+ str(port)
    if method == '按次发送':
        if key in common.g_socket_pool:
            pass
        else:
            #create new socket
            common.g_socket_lock.acquire()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                common.g_socket_pool[key]=[sock,ip,port,time.time()]
            finally:
                common.g_socket_lock.release()
        for i in range(0,method_para):
            try:
                all_tasks=[common.g_ex.submit(_send,syslogdata[i % data_len],ip,port,common.g_socket_pool[key][0])]
            except Exception as e:
                common.g_printthread.submit(common.print_log, e)
                print(e)
            #all_tasks = [common.g_ex.submit(_send, str(i), syslogger)]
        try:
            common.g_threadpool_result.submit(common.wait_for_done,all_tasks,"结束发送"+str(method_para)+"条 Syslog 日志")
        except Exception as e:
            common.g_printthread.submit(common.print_log, e)
            print(e)
    else:
        common.g_syslog_timer.pause()
        #replace socket
        common.g_sysloghandler.close()
        common.g_sysloghandler=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        common.g_syslog_timer.set_function(send_by_timer)
        common.g_syslog_timer.set_args(method_para, syslogdata, ip,port)
        common.g_syslog_timer.resume()
    #syslogger.addHandler(common.g_sysloghandler)

    #pring send log information
    t = send_para(ip,str(port),method,str(method_para))
    common.g_printthread.submit(common.print_log,"开始发送"+t)

            #_send(syslogdata,syslogger)
    #syslogger.warning(syslogdata)
    #sysloghandler.close()