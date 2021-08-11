from pymodbus.version import version
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.datastore.database import SqlSlaveContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
import random
import time

# --------------------------------------------------------------------------- # 
# import the twisted libraries we need 
# --------------------------------------------------------------------------- # 
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- # 
# configure the service logging 
# --------------------------------------------------------------------------- # 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- # 
# define your callback process 
# --------------------------------------------------------------------------- # 

def updating_writer(a):
    
    log.debug("updating the context")
    context = a[0]
    register = 3
    slave_id = 0x00
    address = 0x10
    values = context[slave_id].getValues(register, address, count=5)
    values = [v + 1 for v in values]
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)

def run_dbstore_update_server():
    # ----------------------------------------------------------------------- # 
    # initialize your data store 
    # ----------------------------------------------------------------------- # 

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17]*100),
        co=ModbusSequentialDataBlock(0, [17]*100), 
        hr=ModbusSequentialDataBlock(0, [17]*100), 
        ir=ModbusSequentialDataBlock(0, [17]*100)) 
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- # 
    # initialize the server information 
    # ----------------------------------------------------------------------- # 
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = version.short()

    # ----------------------------------------------------------------------- # 
    # run the server you want 
    # ----------------------------------------------------------------------- # 
    time = 5  # 5 seconds delay 
    loop = LoopingCall(f=updating_writer, a=(context,))
    print("test")
    loop.start(time)# initially delay by time 
    
    
    StartTcpServer(context, identity=identity, address=("", 5020))
    

if __name__ == "__main__":
   
   while True:
    run_dbstore_update_server()
    time.sleep(5)
    
