import matplotlib.pyplot as plt
import numpy as np
import math
import serial
import time
from scipy import optimize
from scipy import interpolate
from PyLTSpice import AscEditor
from PyLTSpice import RawRead
from PyLTSpice import SimRunner

def model_sat(x):
    
    BF = BFmin+(BFmax - BFmin)*math.sin(x[0])**2

    netlist.set_parameter('BF',BF)

    task = LTC.run(netlist)

    raw_file = task.wait_results()[0]
#    print(raw_file)
    LTR = RawRead(raw_file)

    Vout = LTR.get_trace('V(out)')
    Vout_s = np.array([2.33]) 
    Vout_s[0]=Vout_sat
    LTC.file_cleanup()
    print(Vout[0], Vout_s[0])
    print((Vout_s[0] - Vout[0])**2)
    return (Vout_s[0] - Vout[0])**2

LTC = SimRunner()
# Выбор файла с моделью схемы
simFile = "ampl_op.asc"

netlist = AscEditor(simFile)
print(netlist.get_components())

ser = serial.Serial('COM4', 9600)

try:
        Vcc = ser.readline()
        Vout_sat = ser.readline()
        Vcc = Vcc.decode('utf-8').strip()
        Vout_sat = Vout_sat.decode('utf-8').strip()
        print("\nVcc=", Vcc)
        print("\nVout_sat=", Vout_sat)

        netlist.set_parameter('VCC',Vcc)

        BFmin=200
        BFmax=400
        x0 = np.array([1])
        # COBYLA
        res = optimize.minimize(model_sat, x0, method='COBYLA',tol=1e-3)

        print(res.message) 
        #print(res.x)
        print(model_sat(res.x))
        BF = BFmin+(BFmax - BFmin)*math.sin(res.x[0])**2
        print("BF=",BF)

        netlist.set_parameter('BF',BF)

        i=0
        Vout_sat = [0]*50
        Vout_cal = [0]*50
        time_sat = [0]*50
        for i in range(50) :
            time_sat[i] = i
            Vcc = ser.readline()
            Vc = ser.readline()
            Vcc = Vcc.decode('utf-8').strip()
            Vout_sat[i] = Vc.decode('utf-8').strip()
#            print("\nVCC=", Vcc)
            print("\nVout=", Vout_sat[i])
            netlist.set_parameter('VCC',Vcc)
            
            task = LTC.run(netlist)

            raw_file = task.wait_results()[0]
            LTR = RawRead(raw_file)
            Vout = LTR.get_trace('V(out)')
            print("\nVmod=", Vout[0])
            Vout_cal[i] = Vout[0]

            LTC.file_cleanup()
#            time.sleep(0.05)
except Exception:
       ser.close()
spline_sat = interpolate.UnivariateSpline(time_sat,Vout_sat)
spline_cal = interpolate.UnivariateSpline(time_sat,Vout_cal)
plt.plot(time_sat, spline_sat(time_sat),'b',label='макет')
plt.plot(time_sat, spline_cal(time_sat),'r',label='модель')
plt.ylim(2.0,2.3)
plt.legend()
plt.grid()
plt.show()
LTC.file_cleanup()
