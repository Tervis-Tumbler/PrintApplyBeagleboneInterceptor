from periphery import SPI # for SPI functions
import time # for timestamp and sleep functions.
from bbio import * # for BeagleBone Black pin functions.

# External connections
boxSensorPin = GPIO2_12 # pin P8.39
applicatorHomePositionSensor = GPIO2_13 # pin P8.40
randomStrokeDelayOutputPin = GPIO2_10 # pin P8.41
redLED = GPIO2_11 # pin P8.42
yellowLED = GPIO2_8 # pin P8.43

# Variables
accelerometerCurveArea = 0
accelerometerSampleDelay = 5
cycleDelay = 2000
randomStrokeDelay = 150
minVelocityToCalculate = 1000
maxVelocityToCalculate = 37500
maxRandomStrokeDelayTime = 145
minRandomStrokeDelayTime = 50

# Pin Setup
pinMode(applicatorHomePositionSensor,INPUT,1)
pinMode(boxSensorPin,INPUT,1)
pinMode(randomStrokeDelayOutputPin,OUTPUT)
pinMode(redLED,OUTPUT)
pinMode(yellowLED,OUTPUT)

def calculateRandomStrokeDelay(velocity):
    if (velocity < minVelocityToCalculate):
        return maxRandomStrokeDelayTime
    elif (velocity > minVelocityToCalculate) and (velocity < maxVelocityToCalculate):
        return (velocity - minVelocityToCalculate) * (minRandomStrokeDelayTime - maxRandomStrokeDelayTime) / (maxVelocityToCalculate - minVelocityToCalculate) + maxRandomStrokeDelayTime 
    else:
        return minRandomStrokeDelayTime

def printStatus(randomStrokeDelay, accelerometerCurveArea):
    print "JSON STUFF"
    
def isApplicatorMoving():
    if(digitalRead(applicatorHomePositionSensor)):
        digitalWrite(yellowLED,HIGH)
        return True
    else:
        return False

def boxDetected():
    if (digitalRead(boxSensorPin)):
        return False
    else:
        return True
        
def sendRandomStrokeDelaySignal():
    digitalWrite(redLED,HIGH)
    delay(randomStrokeDelay)
    digitalWrite(randomStrokeDelayOutputPin,HIGH)
    delay(cycleDelay)
    digitalWrite(yellowLED,LOW)
    digitalWrite(redLED,LOW)
    digitalWrite(randomStrokeDelayOutputPin,LOW)
    
def printSettings():
    print ("\nMinimum Velocity: " + str(minVelocityToCalculate)) 
    print ("\nMaximum Velocity: " + str(maxVelocityToCalculate))
    print ("\nMinimum Delay Time: " + str(minRandomStrokeDelayTime))
    print ("\nMaximum Delay Time: " + str(maxRandomStrokeDelayTime) + "\n")

# Initialize SPI communication with the ADXL345.
def initiateADXL345():
    
    # Creates SPI object with the following parameters:
        # - SPI device as "/dev/spidev1.0"
        # - Clock mode 3 (i.e., sets clock polarity 1, clock phase 1)
        # - Clock frequency set to 400KHz
    spi = SPI("/dev/spidev1.0",3,400000)
    
    # Address 0x31 OR'd with 0x40 MB bit.
    # Set to 0x08: 16g Full (13-bit) Resolution - 4mg/LSB.
    setDataFormat = [0x71,0x0F]
    
    # Address 0x2D OR'd with 0x40 MB bit.
    # Set to 0x08: Measurement mode.
    setPowerCtl = [0x6D,0x08]
    
    # Address 0x2C OR'd with 0x40 MB bit.
    # Set to 0x0D: 800 Hz Output Data Rate    
    setDataRate = [0x6C,0x0D]
    
    # Transfer settings to ADXL345.
    spi.transfer(setDataFormat)
    spi.transfer(setPowerCtl)
    spi.transfer(setDataRate)
    
    return spi
    
# Parse data from accelerometer.
def combineBytes (lsb, msb, bits, offset):
    
    # Shift MSB to the left.
    MSB = msb << 8
    
    # Combine MSB and LSB.
    combo = MSB | lsb
    
    # Remove trailing bits.
    combo = combo >> 3
    
    # Perform Two's Complement, with offset if needed.
    sign_bit = 1 << (bits - 1)
    return (combo & (sign_bit - 1)) - (combo & sign_bit) + offset


# Define value indices for a given axis.
def axisVariable(axis):
    if axis == 'x':
        j = 1
        k = 2
        return j,k
    elif axis == 'y':
        j = 3
        k = 4
        return j,k
    elif axis == 'z':
        j = 5
        k = 6
        return j,k
    else:
        print ("Invalid axis.")
        return


# Gets data from accelerometer. Returns array with values.
def getData(adxl):
    
    # Get values from accelerometer.
    value = adxl.transfer(dataX0)
    
    # Initialize array with timestamp.
    axisValues = [{"time":time.time()}]
    
    for a in ['x','y','z']:
        # Value index associated with axis measured.
        j,k = axisVariable(a)
        
        # Combine data and perform Two's Complement.
        combinedValue = combineBytes(value[j],value[k],13,6)
        
        # Add values to the array.
        iter(axisValues).next()[a] = combinedValue
    
    # Contains data array [{"time":timestamp,"x":xValue,"y":yValue,"z":zValue}]
    return axisValues
    

# This is the DATAX0 register (0x32) OR'd with Read bit (0x80)
# and Multiple Bytes bit (0x40). It is followed by 6 0x00 values
# to read 6 bytes starting from DATAX0. When transferred, this 
# returns 7 bytes: NULL (0x00), DATAX0 (0x32), DATAX1 (0x33), 
# DATAY0 (0x34), DATAY1 (0x35), DATAZ0 (0x36), and DATAZ1 (0x37).
dataX0 = [0xF2,0x00,0x00,0x00,0x00,0x00,0x00]

# Initialize SPI object.
spi = initiateADXL345()


def setup() :# Set up pin values and properties.
    


def loop():
    digitalWrite(yellowLED,HIGH)
    print(getData(spi)[0]['z'])
    delay(5)
    digitalWrite(yellowLED,LOW)
    
    
    
run(setup,loop)
