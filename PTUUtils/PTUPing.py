# coding=utf-8
__author__ = 'Rosefinch'
__date__ = '2018/5/31 22:27'

import time
import struct
import socket
import select
import tkinter as tk
import PTUUtils.PTUCommon as common

# import sys

class CheckServer(object):
    def __init__(self, host=None, logoutput=None):
        if host == None:
            self.host = '127.0.0.1'
        else:
            self.host = host
            self.logoutput = logoutput


    def chesksum(self, data):

        n = len(data)
        m = n % 2
        sum = 0
        for i in range(0, n - m, 2):
            sum += (data[i]) + ((data[i + 1]) << 8)  # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
        if m:
            sum += (data[-1])
        # 将高于16位与低16位相加
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)  # 如果还有高于16位，将继续与低16位相加
        answer = ~sum & 0xffff
        # 主机字节序转网络字节序列（参考小端序转大端序）
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    '''
    连接套接字,并将数据发送到套接字
    '''

    def raw_socket(self, dst_addr, imcp_packet):
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        send_request_ping_time = time.time()
        # send data to the socket
        rawsocket.sendto(imcp_packet, (dst_addr, 80))
        return send_request_ping_time, rawsocket, dst_addr

    '''
    request ping
    '''

    def request_ping(self, data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
        # 把字节打包成二进制数据
        imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, data_checksum, data_ID, data_Sequence,
                                  payload_body)
        icmp_chesksum = self.chesksum(imcp_packet)  # 获取校验和
        imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_ID, data_Sequence,
                                  payload_body)
        return imcp_packet

    '''
    reply ping
    '''

    def reply_ping(self, send_request_ping_time, rawsocket, data_Sequence, timeout=2):
        while True:
            started_select = time.time()
            what_ready = select.select([rawsocket], [], [], timeout)
            wait_for_time = (time.time() - started_select)
            if what_ready[0] == []:  # Timeout
                return -2
            time_received = time.time()
            received_packet, addr = rawsocket.recvfrom(1024)
            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(
                ">BBHHH", icmpHeader
            )
            if type == 0 and sequence == data_Sequence:
                return time_received - send_request_ping_time
            timeout = timeout - wait_for_time
            if timeout <= 0:
                return -1

    def ping(self):
        data_type = 8  # ICMP Echo Request
        data_code = 0  # must be zero
        data_checksum = 0  # "...with value 0 substituted for this field..."
        data_ID = 0  # Identifier
        data_Sequence = 1  # Sequence number
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'  # data
        try:
            dst_addr = socket.gethostbyname(self.host)
        except socket.gaierror as e:
            common.g_printthread.submit(common.print_log,format(e))
            return

        if self.logoutput :
            common.g_printthread.submit(common.print_log,"正在 Ping {0} [{1}] 具有 32 字节的数据:".format(self.host, dst_addr))
        result = 0
        for i in range(0, 4):
            icmp_packet = self.request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence + i,
                                            payload_body)
            send_request_ping_time, rawsocket, addr = self.raw_socket(dst_addr, icmp_packet)
            times = self.reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
            if times >= 0:
                if self.logoutput:
                    common.g_printthread.submit(common.print_log," {0} 的回复: 字节=32 时间={1}ms".format(addr, int(times * 1000)))
                result = result + 1
                time.sleep(0.7)
            elif times == -1:
                if self.logoutput == True and result > 0:
                    common.g_printthread.submit(common.print_log,self.host+' 系统问题')
                    result = result + 1
            else:
                if self.logoutput :
                    common.g_printthread.submit(common.print_log,self.host+" 请求超时。")
        if result > 0:
            common.g_printthread.submit(common.print_log,self.host + " status: OK")
        else:
            common.g_printthread.submit(common.print_log,self.host + " status: No Response")
        return result


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #    sys.exit('Usage: ping.py <host>')

    def myping():
        result=CheckServer(t.get(), l).ping()
        if (result>1):
            l.insert(tk.END,t.get()+' OK')
            l.insert(tk.END,'\n')
        else:
            l.insert(tk.END,t.get()+' no response')
            l.insert(tk.END,'\n')
        l.see(tk.END)

    root = tk.Tk()
    l=tk.Text(root,width=100,height=4)
    l.pack()
    t=tk.Entry(root,width=30)
    t.pack()
    b=tk.Button(root,text="Ping",command=myping)
    b.pack()

    root.mainloop()