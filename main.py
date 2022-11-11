#!/usr/bin/env python3
"""
Pymodbus Asynchronous Server Example
--------------------------------------------------------------------------

The asynchronous server is a high performance implementation using the
twisted library as its backend.  This allows it to scale to many thousands
of nodes which can be helpful for testing monitoring software.
"""
import time

from pymodbus.constants import Endian
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import threading as th
from pymodbus.payload import BinaryPayloadBuilder

class ModbusServer:
    def __init__(self, max_address=100, port=5020):
        self._co_datablock = ModbusSequentialDataBlock(0, [1] * (max_address + 4))
        self._hr_datablock = ModbusSequentialDataBlock(0, [2] * (max_address + 4))
        self._ir_datablock = ModbusSequentialDataBlock(0, [3] * (max_address + 4))
        self._di_datablock = ModbusSequentialDataBlock(0, [4] * (max_address + 4))

        self._store = ModbusSlaveContext(
            co=self._co_datablock, hr=self._hr_datablock, ir=self._ir_datablock, di=self._di_datablock)

        self._context = ModbusServerContext(slaves=self._store, single=True)
        self._port = port
        self._i = 0.0

    def start(self):
        t = th.Thread(target=self.update)
        t.start()

    def update(self):
        while True:
            time.sleep(1)
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
            builder.add_32bit_float(self._i)
            builder.add_32bit_float(-self._i)
            self._i += 1.0
            self._i %= 100.0
            self._store.setValues(16, 4, builder.to_registers())
            print('Updating values to ' + str(self._i))

    def run_server(self):
        # ----------------------------------------------------------------------- #
        # run the server
        # ----------------------------------------------------------------------- #
        print("Modbus server started!")
        StartTcpServer(self._context, address=("localhost", self._port))


if __name__ == "__main__":
    s = ModbusServer()
    s.start()
    s.run_server()
