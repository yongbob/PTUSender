# coding=utf-8
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor,as_completed
import PTUUtils.PTULoopTimer as lptimer
import threading
import socket
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
import inspect
import ctypes
import time
'''
common functions
'''



'''

define global variable:
logprint thread: g_pringthread
threadpool:g_ex

'''
global g_printthread
global g_ex
global g_sysloghandler
global g_loghandler
global g_threadpool_result
global g_syslog_timer
global g_socket_lock
global g_socket_pool
global g_snmp_pool
global g_snmp_transportDispatcher
global g_snmp_timer
global g_clean_log_timer
global g_thread_running
global g_total_tasks

def clean_log(*args,**kwargs):
    if g_loghandler:
        g_loghandler.delete(1.0,tk.END)
        g_loghandler.see(tk.END)
        g_loghandler.update()

def print_log(*args,**kwargs):

    message = args[0]
    if g_loghandler:
        g_loghandler.insert(tk.END, '\n')
        g_loghandler.insert(tk.END, message)

        g_loghandler.see(tk.END)
        g_loghandler.update()
    else:
        print('没有日志窗口，无法打印消息：'+ message)
def wait_for_done(*args,**kwargs):

    for futures in as_completed(args[0]):
        pass
    print_log("\n"+args[1])

#degine empty function for LoopTimer
#will be replaced as required

def timer_function_null(*args,**kwargs):
    pass

def init_para():
    global g_total_tasks
    g_total_tasks = 50000

    global g_thread_running
    g_thread_running = True
    global g_printthread
    g_printthread = ThreadPoolExecutor(1)

    global g_ex
    g_ex = None

    global g_sysloghandler
    #init the socket. the address will be changed.
    #g_sysloghandler = plog.MySysLogHandler(("127.0.0.1", 514))
    g_sysloghandler = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #snmp timer handler.
    global g_snmp_transportDispatcher

    g_snmp_transportDispatcher = AsynsockDispatcher()
    g_snmp_transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openClientMode()
    )

    global g_loghandler
    g_loghandler = None

    global g_threadpool_result
    g_threadpool_result = ThreadPoolExecutor(5)

    global g_syslog_timer
    g_syslog_timer = lptimer.LoopTimer(1,timer_function_null,())
    g_syslog_timer.setDaemon(True)
    g_syslog_timer.start()
    g_syslog_timer.pause()

    global g_snmp_timer
    g_snmp_timer = lptimer.LoopTimer(1, timer_function_null, ())
    g_snmp_timer.setDaemon(True)
    g_snmp_timer.start()
    g_snmp_timer.pause()

    global g_clean_log_timer
    g_clean_log_timer = lptimer.LoopTimer(120,clean_log , ())
    g_clean_log_timer.setDaemon(True)
    g_clean_log_timer.start()
    g_clean_log_timer.resume()

    global g_socket_lock
    g_socket_lock = threading.Lock()

    global g_socket_pool
    g_socket_pool = {}

    global g_snmp_pool
    g_snmp_pool = {}


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
    #print(thread)

def close():
    global g_printthread
    global g_ex
    global g_threadpool_result
    global g_socket_pool
    global g_syslog_timer
    global g_snmp_transportDispatcher
    global g_snmp_pool
    global g_snmp_timer
    global g_socket_lock
    global g_thread_running
    g_thread_running = False

    print_log("正在关闭程序，需要结束排队中任务")
    g_syslog_timer.stop()
    g_snmp_timer.stop()
    g_clean_log_timer.stop()

    time.sleep(2)
    while g_ex._work_queue.qsize() > 0:
        print_log("还有%s个任务需要完成" % (g_ex._work_queue.qsize()))
        #print (g_ex._work_queue.qsize())
        time.sleep(2)
    #g_ex.shutdown()

    while g_printthread._work_queue.qsize() > 0:
        print_log("还有%s个任务需要完成" % (g_printthread._work_queue.qsize()))
        #print (g_ex._work_queue.qsize())
        time.sleep(1)
    #g_printthread.shutdown()

    while g_threadpool_result._work_queue.qsize() > 0:
        print_log("还有%s个任务需要完成" % (g_threadpool_result._work_queue.qsize()))
        #print (g_ex._work_queue.qsize())
        time.sleep(1)
    #g_threadpool_result.shutdown()


    for k, v in g_socket_pool.items():
        v[0].close()
        ##close socket

    g_sysloghandler.close()

    # close snmp handlers
    # global timer g_snmp_transportDispatcher
    g_snmp_transportDispatcher.closeDispatcher()
    for k, v in g_snmp_pool.items():
        v[0].closeDispatcher()
''''
def close():
    global g_printthread
    global g_ex
    global g_threadpool_result
    global g_socket_pool
    global g_syslog_timer
    global g_snmp_transportDispatcher
    global g_snmp_pool
    global g_snmp_timer
    global g_socket_lock
    global g_thread_running
    g_thread_running = False

    #close timer
    
    g_syslog_timer.pause()
    g_syslog_timer.stop()
    g_snmp_timer.pause()
    g_snmp_timer.stop()
    g_snmp_timer.pause()
    g_clean_log_timer.stop()
    
    
    g_socket_lock.acquire()
    try:
        g_ex.shutdown(wait=True)
        time.sleep(2)
        g_printthread.shutdown(wait=True)
        g_threadpool_result.shutdown(wait=True)
        #if not g_ex:
    finally:
        g_socket_lock.release()
    
    #close syslog handlers
    #print("please wait for shutdown....")
    #time.sleep(5)

    #g_ex.shutdown(wait=True)
    for t in g_ex._threads:
        stop_thread(t)
    for t in g_printthread._threads:
        stop_thread(t)
    for t in g_threadpool_result._threads:
        stop_thread(t)

    for k,v in g_socket_pool.items():
        print(v[0])
        v[0].close()
        ##close socket

    g_sysloghandler.close()

    #close snmp handlers
    #global timer g_snmp_transportDispatcher
    g_snmp_transportDispatcher.closeDispatcher()
    for k,v in g_snmp_pool.items():
        print(v[0])
        v[0].closeDispatcher()
'''
