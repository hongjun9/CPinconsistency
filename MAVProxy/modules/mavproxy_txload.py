#!/usr/bin/env python
'''
load a tx firmware using DATA96
'''

import sys, os, time, struct
from MAVProxy.modules.lib import mp_module

class TxLoad(mp_module.MPModule):
    def __init__(self, mpstate):
        super(TxLoad, self).__init__(mpstate, "txload", "txload module")
        self.add_command('txload', self.cmd_txload, "load a TX firmware")
        self.data = None
        self.data_type = 42

    def cmd_txload(self, args):
        '''load a tx firmware'''
        if len(args) < 1:
            print("txload <FILE>")
            return
        self.data = open(args[0]).read()
        self.acked_to = 0
        self.last_send = time.time()
        self.send_start = time.time()
        print("Loaded %u bytes" % len(self.data))


    def send_block(self):
        '''send one block'''
        block = self.data[self.acked_to:self.acked_to+92]
        header = struct.pack("<I", self.acked_to)
        packet = header + block
        data = [ord(x) for x in packet]
        dlen = len(data)
        data.extend([0]*(96-dlen))
        print("Sending block of length %u at %u" % (dlen-4, self.acked_to))
        mav = self.master.mav
        mav.data96_send(self.data_type, dlen, data)
        self.last_send = time.time()
        

    def idle_task(self):
        '''run periodic upload check'''
        if self.data is None:
            return
        now = time.time()
        if now - self.last_send > 2:
            self.send_block()
        
    def mavlink_packet(self, m):
        '''handle an incoming mavlink packet'''
        if self.data is None:
            return
        if m.get_type() == 'DATA16' and m.type == self.data_type and m.len == 4:
            s = str(m.data[:4])
            data = m.data[:m.len]
            s = ''.join([chr(x) for x in data])
            (ack,) = struct.unpack("<I", s)
            self.acked_to = max(self.acked_to, ack)
            if self.acked_to >= len(self.data):
                print("Finished upload of txdata of length %u in %u seconds" % (
                    len(self.data), time.time() - self.send_start))
                self.data = None
            else:
                self.send_block()

def init(mpstate):
    '''initialise module'''
    return TxLoad(mpstate)
