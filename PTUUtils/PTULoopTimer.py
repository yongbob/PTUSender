# coding=utf-8
# author: Marshall Bao
# Date: 2018-11-3

# timer with pause() and resume
# each protocls has a timer

import threading
import PTUUtils.PTUCommon as common

class LoopTimer(threading.Timer):
    '''Call a function after a specified number of seconds:
            t = LoopTimer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
    '''

    def __init__(self, interval, function, *args, **kwargs):
        threading.Timer.__init__(self, interval, function, args, kwargs)
        self.__resume = threading.Event()
        self.__resume.clear()
        self.counter = 0
    def pause(self):
        self.counter = 0
        self.__resume.clear()

    def pause_counter(self):
        self.__resume.clear()

    def resume(self):
        self.__resume.set()

    def stop(self):
        self.__resume.set()
        super().cancel()
    def status(self):
        return self.__resume.is_set()

    def get_counter(self):
        return self.counter

    def set_counter(self,counter):
        self.counter = counter

    def set_function(self, function):
        self.function = function

    def set_args(self,*args):
        self.args = args

    def set_kwargs(self,**kwargs):
        self.kwargs = kwargs

    def run(self):
        while True:
            if not self.__resume.is_set():
                self.__resume.wait()
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)
            self.counter = self.counter + 1
            #common.g_syslog_timer_count = common.g_syslog_timer_count+1

if __name__ == '__main__':
    import time

    para_1 = []
    for i in range(10):
        para_1.append(str(i))

    para_2 = []
    for i in range(12):
        para_2.append(str(i))

    def func_1(*args,**kwargs):
        print("function 1:",args[0])

    def func_2(*args,**kwargs):
        print("function 2:",args[0])

    t = LoopTimer(1,func_1,para_1)
    t.start()
    t.pause()
    for i in range(7):
        print("main",t.get_counter())
        if i == 2:
            t.resume()
        time.sleep(1)
    t.pause()
    t.set_function(func_2)
    t.set_args(para_2)
    time.sleep(1)
    t.resume()
    for i in range(5):
        print("main", t.get_counter())
        time.sleep(1)

    t.stop()
    print("end")
