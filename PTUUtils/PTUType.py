from enum import Enum


class ProtocolType(Enum):
    Syslog = 1
    SNMP = 2

class ConfigDict(object):
    def __init__(self,ip=None,port=None,method=None,method_para=None,log=None):
        self.ip=ip
        self.port = port
        self.method=method
        self.method_para =method_para
        self.log = log

    def set(self,ip=None,port=None,method=None,method_para=None,log=None):
        if ip :
            self.ip = ip
        elif port :
            self.port = port
        elif method :
            self.method = method
        elif method_para :
            self.method_para = method_para
        elif log :
            self.log = log

    def info(self):
        if self.method == "按次发送":
            t_return = "IP: "+str(self.ip)+" Port: "+str(self.port) + "     发送方式:"+str(self.method) + \
                       "("+str(self.method_para)+"次）  "+str(self.log)
        else:
            t_return = "IP: " + str(self.ip) + " Port: " + str(self.port) + "     发送方式:" + str(self.method) + \
                       "(" + str(self.method_para) + "次/秒）  " + str(self.log)
        return t_return
    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_method(self):
        return self.method

    def get_method_para(self):
        return self.method_para

    def get_log(self):
        return self.log

if __name__ == '__main__':
    cd = ConfigDict()
    cd.set(ip='127.0.0.1')
    cd.set(method="按次发送")

    print(cd.info())
    cd.set(method = "按速度发送")
    print(cd.info())

    print(cd.get_ip())
    print(cd.__getattribute__('ip'))