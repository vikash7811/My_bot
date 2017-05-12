#!/usr/bin/python

import time
import mybot_serialport

import mybot_OpenCV

from colorama import init,Fore
init(autoreset=True)


Run = False

# Data Packet from robot
#
# Byte  Description
# 0	Center Sonar
# 1	Left Sonar
# 2	0
# 4	0




# Opencv threshold values

YELLOWOBJECTS = [10,100,90,30,255,255]
BLUEOBJECTS = [100,145,130,130,255,255]
PINKOBJECTS = [142,8,32,175,255,255]
GREENOBJECTS = [40,60,60,100,200,230]

#ThresholdArray = YELLOWOBJECTS

Symbol = "HOME" 

# Robot control variables

#Instructions
GETDATA = 0
ROBOTFORWARD = 1
ROBOTLEFT = 2
ROBOTRIGHT = 3
ROBOTREVERSE = 4

#to getdata from arduino
def GetData():
    mybot_serialport.sendserial([255, 255, GETDATA, 0,  0,0,0,0]) #send command to get sensor data from robot
    while True:
        a = mybot_serialport.getserial(6) #wait here until data is received to confirm command complete
        if a is not None:
            break    
    return a #return data packet


#to move robot , sends command to ardduino
def RobotMove(direction,time,center,left,speed):

    mybot_serialport.sendserial([255, 255, direction, time,center,left,speed,0]) #send command to move head
    while True:
        a = mybot_serialport.getserial(6) #wait here until data is received to confirm command complete
        if a is not None:
            break 
    return a #return data packet

#Testing Functions
def Turn180():
    RobotData = RobotMove(ROBOTLEFT,2,0,0,125) #no sonar or IR threshold so move always completes
    print RobotData

def Turn360():
    RobotData = RobotMove(ROBOTLEFT,4,0,0,125) #no sonar or IR threshold so move always completes
    print RobotData

def MoveForward():
    RobotData = RobotMove(ROBOTFORWARD,1,0,0,125) #no sonar or IR threshold so move always completes
    print RobotData

def MoveReverse():
    RobotData = RobotMove(ROBOTREVERSE,1,0,0,125) #no sonar or IR threshold so move always completes
    print RobotData

#check for target , current uses findobject from opencv
def CheckForTarget(Symbol ,tries):
    TargetData = [-1,-1,-1,-1,-1,-1]
    for x in range (0,tries):
        TargetData = mybot_OpenCV.FindObject(GREENOBJECTS)
        if TargetData[0] != -1:#Target present
             #if its the correct target type
                return TargetData #return straight away if correct symbol found


    return TargetData


#for moving to target after detection
def MoveToTarget(Symbol):

    time = 1
    RobotData = RobotMove(ROBOTFORWARD, time,20,8,255)
    print "Moved Foward towards Target"
    TargetData = CheckForTarget(Symbol,1)
    print TargetData ,"outside"
    a = TargetData[2]
    print "a  outside", a
    while a > 25:
        time = int (a)
        print "Target not yet Reached"
        RobotData = RobotMove(ROBOTFORWARD, 1,20,8,125)
        TargetData = CheckForTarget(Symbol,1)
        a = TargetData[2]
        

    if a <25 and a>0 :
            print a
            print "target reached"
            RobotData = Turn180()
            print "Target Reached"
            return 1

    else :
        print a , "Might be -1"

def AlignToRight(Symbol):

    TargetData = CheckForTarget(Symbol,1)
    a = TargetData[0]
    while  a > 400:
        print (Fore.BLUE + "Target is on the right ")
        RobotData = RobotMove(ROBOTRIGHT, 1,0,0,255)
        print "turning right for alignmnt"
        RobotData = RobotMove(ROBOTFORWARD, 1,0,0,255)
        print "moving foward while right aligning"
        RobotData = RobotMove(ROBOTLEFT, 1,0,0,255)
        print "turning left whiel right aligning"
        TargetData = CheckForTarget(Symbol,1)
        a = TargetData[0]
        if a!=-1:
            a = TargetData[0]
        else:
             TargetData = CheckForTarget(Symbol,1)
             a = TargetData[0]
             if a!=-1:
                continue
             else:
                return -1
        print a
       

    TargetData = CheckForTarget(Symbol,1)
    if (TargetData[0] > 200 and TargetData[0] < 400):
        print "Alignment Done"
        return 1
    else:
        return -1



#aligns towaards left, tries to bring target to centre of frame
def AlignToLeft(Symbol):
    TargetData = CheckForTarget(Symbol,1)
    a = TargetData[0]
    while (a < 200 and a > 0):
        print (Fore.BLUE + "Target is on the left ")
        RobotData = RobotMove(ROBOTLEFT, 1,0,0,255)
        print "turning left for aligning"
        RobotData = RobotMove(ROBOTFORWARD, 1,0,0,255)
        print "moving foward while aligning"
        RobotData = RobotMove(ROBOTRIGHT, 1,0,0,255)
        print "turning right for alignment"
        TargetData = CheckForTarget(Symbol,1)
        a = TargetData[0]
        if a!=-1:
            a = TargetData[0]
        else:
             TargetData = CheckForTarget(Symbol,1)
             a = TargetData[0]
             if a!=-1:
                continue
             else:
                return -1
        print a

    TargetData = CheckForTarget(Symbol,1)
    if (TargetData[0] >200 and TargetData[0] < 400):
        print "Alignment Done"
        return 1
    else:
        return -1







def ScanForTarget(Symbol):

    print (Fore.BLUE + "Scanning for target")
    #Scan area in front of robot looking for an image target
    TargetData = CheckForTarget(Symbol,1)#Capture image and check for symbol
    print "doubt 1 target data",TargetData
    if TargetData[0] == -1:
        print (Fore.BLUE + "No Target In Image")
        print TargetData
    else: #If the target has been found
        TargetData = CheckForTarget(Symbol,1) #Check 1 time to see if target is still there
        if TargetData[0] == -1:
            print (Fore.BLUE + "Target Lost")
            print TargetData
        else: #Robot is looking at target, check again that target is still there
            print TargetData
            print "Target still in sight , aligning mode on" , TargetData
            if (TargetData[0] < 200 and TargetData[0] >0):
                print "aligning to the left"
                correction = AlignToLeft(Symbol);
                if correction == 1:
                    print (Fore.BLUE + "Target Ahead")
                    return 1
                else :
                    return -1

            elif (TargetData[0] > 200 and TargetData[0] < 400):
                print (Fore.BLUE + "Target Ahead NO NEED fOR aLIGNMET")
                return 1

            else:#for greater than 400
                print "Aligning To right"
                Correction = AlignToRight(Symbol);
                if Correction == 1:
                    print (Fore.BLUE + "Target Ahead")
                    return 1
                else :
                    return -1
  
    return -1



def AlignObjectR(ThresholdArray):
        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        print 'aligning right with object'
        x = ObjectData[0]
        while  x < 200:
                RobotData = RobotMove(ROBOTRIGHT,1,0,0,255)
                RobotData = RobotMove(ROBOTFORWARD,1,0,0,255)
                RobotData = RobotMove(ROBOTLEFT,1,0,0,255)
                TargetData = CheckForTarget(Symbol,1)
                if TargetData[0] != -1:
                        print "target found while checking object"
                        return 2

                ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
                x = ObjectData[0]

        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        if (ObjectData[0] >200 and ObjectData[0] < 400):
                print "Object Alignment Done"
                return 1



def AlignObjectL(ThresholdArray):
    ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
    x = ObjectData[0]
    print "aligning  left with object"
    while  x < 200:
                print "object is 200 cm left with frame"
                RobotData = RobotMove(ROBOTLEFT,1,0,0,255)
                print "robot turn left to align with object"
                RobotData = RobotMove(ROBOTFORWARD,1,0,0,255)
                print "robot turn forward to align with object"
                RobotData = RobotMove(ROBOTRIGHT,1,0,0,255)
                print "robot turn right to align ..."
                TargetData = CheckForTarget(Symbol,1,0,0,255)
                print "target re-achecked"
                if TargetData[0] != -1:
                        print "target found while aligning"
                        return 2

                ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
                x = ObjectData[0]

    ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
    if (ObjectData[0] >200 and ObjectData[0] < 400):
           print "Object Alignment Done"
           return 1



def CheckObject(ThresholdArray, Onum):
     if Onum == 1:
        ObjectData = mybot_OpenCV.FindObject(PINKOBJECTS)
        return  1
     elif Onum == 2:
        ObjectData = mybot_OpenCV.FindObject(YELLOWOBJECTS)
        return -1






def AvoidObstacle(ThresholdArray):

    ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
    print "avoiding obstacle "
    if ObjectData[0] == -1:
        print "object lost while avoiding "
        return -1
    else:
        print "object is in range, entring avoing"
        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        b = (ObjectData[2])
        time = int(b/5)
        print "object is turning right to avoid obstacle"
        RobotData = RobotMove(ROBOTFORWARD,time,0,0,255)
        print "robot is turning forward to align"
        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        print "further rechecked object"
        b = int (ObjectData[2])
        if (b < 20 and b > 0 ):
            RobotData = RobotMove(ROBOTRIGHT, 1,0,0,255)
            RobotData = RobotMove(ROBOTFORWARD, 2,0,0,255)
            RobotData = RobotMove(ROBOTLEFT, 1,0,0,255)
            RobotData = RobotMove(ROBOTFORWARD, 4,0,0,255)
            ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
            if ObjectData == [-1,-1,-1,-1,-1,-1]:
                result = 1
            else:
                print "a obstacle maybe ahead"
                result = -1
        else :
            while b > 25:
                RobotData = RobotMove(ROBOTFORWARD, time,0,0,255)
                ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
                print "further rechecked object 222"
                b = int(ObjectData[2])

            RobotData = RobotMove(ROBOTRIGHT, 1,0,0,255)
            RobotData = RobotMove(ROBOTFORWARD, 2,0,0,255)
            RobotData = RobotMove(ROBOTLEFT, 1,0,0,255)
            RobotData = RobotMove(ROBOTFORWARD, 4,5,0,255)

            if ObjectData == [-1, -1, -1, -1, -1, -1]:
                 result = 1
            else:
                 result = -1


    return result

def GoToTarget(Symbol):
    if TargetAquired is True:
            result = MoveToTarget("HOME")
            if result == 1:
                 return 1
                 print "Target Reached Mission Accomlished"
            else:
                 print "No target in view  decide next"
                     #Move to a different location and scan again here
                 return  -1



#Scans  for Obstacle Ahead
def Scan4Object(ThresholdArray, tries):

    for i in range (0,tries):

        for x in range(0, 8):
            ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
            if ObjectData[0] == -1:
                print "No object found from scan"
   		#RobotData = RobotMove(ROBOTRIGHT,1,0,0,255)
		print "turning to left in search of object"
            else:
                print "Object Found"
                return  1



    return -1


def keyboard_control():
    while 1:
      a=CheckForTarget(Symbol ,tries)
      print a
      key=raw_input("enter the keyboard command ")
      if (key==F or key ==f):
          RobotMove(ROBOTFORWARD, 1,0,0,255)            
      elif (key ===L or key ==l):
          RobotMove(ROBOTLEFT, 1,0,0,255)
      elif (key ===R or key ==r):
          RobotMove(ROBOTLEFT, 1,0,0,255)
      elif(key ===B or key ==b):
          RobotMove(ROBOTREVERSE, 1,0,0,255)
      else:
           print("robot needs to be stoped")
           break
          

#Scans 360 for Target
def Scan4Target(Symbol,tries):

    Result = -1
    for i in range (0,tries):
        for x in range(0, 8):
            Result = ScanForTarget("HOME")
            if Result == -1:
                print "No Target found from scan"
                # turn 90 degrees to the left
                RobotData = RobotMove(ROBOTLEFT, 1, 0, 0,255)  # no sonar  so move always completes
                print "Turning to Left in search of target"
            else:
                print "Target Aquired"


    if Result == 1:
        return 1
    else:
        return -1




#####MAIN PYTHON FILE


Run = True



#while 1:
 
 #  RobotMove(ROBOTRIGHT,2,0,0,255)
  #RobotMove(ROBOTFORWARD,10,5,5,255)        
while Run is True:
     Onum = -1
     ALIGNED = False
     TargetAquired = False
     ObjectAquired = False
     ObstacleAvoided = False

     ScanT = Scan4Target("HOME",1)
     if (ScanT == -1):
         print "target not found inside main"

     elif(ScanT == 1):
         print "Target found from scan"
         
	 result = MoveToTarget("HOME")
         z = mybot_OpenCV.FindObject(GREENOBJECTS)
	 if z < 200 and z > 0:
		p = AlignToLeft("HOME")
		if p == 1:
			MoveToTarget("HOME")
		
	 		TargetAquired = True
         		Run = False
		else :
			TargetAquired = False
	 elif z>400 and z<200:
		print "no alignment to target require"
		MoveToTarget("HOME")
		TargetAquired("HOME")
		Run = False
	 else:
		q = AlignToRight("HOME")
		if q == 1:
			MoveToTarget("HOME")
			TargetAquired = True 
			Run = False
		else :
			TargetAquired = False	     
     else:
         print "Check Here!"




     ScanP = Scan4Object(PINKOBJECTS,1)
     if ScanP == 1 :
         print 'Pink Object  Found'
         ObjectAquired = True
         Onum = 1
     else:
         print 'no pink object  found in path'

     ScanY = Scan4Object(YELLOWOBJECTS, 1)
     if ScanY == 1:
         print "yellow object detected"
         ObjectAquired = True
         Onum = 2
     else:
         print 'no yellow object found inn path'

     if ScanP == -1 and ScanY == -1:
	RobotData = RobotMove(ROBOTFORWARD, 3, 0, 0,255)
	print "moving to anoher locaion"

     if ObjectAquired is True:
            print "entering object loop"
            
            if Onum == 1:
                print "aliging to  pink objects"
                foralign = CheckObject(PINKOBJECTS, 1 )
                if foralign == -1:
                    'pink objects lost'
                else:
                    AlignData = mybot_OpenCV.FindObject(PINKOBJECTS)
                    if AlignData[0] < 200 and AlignData[0] > 0:
                        y = AlignObjectL(PINKOBJECTS)
                        if y == 1 :
                            ALIGNED = True
                        else:
                            TargetAquired = True
                            print 'add here'
                            MoveToTarget("HOME")
                    elif AlignData[0] > 200 and AlignData[0] < 400:
                        print 'No Alignement error'
                        ALIGNED = True
                    else:

                        y = AlignObjectR(PINKOBJECTS)
                        if y == 1:
                            ALIGNED = True
                        else:
                            TargetAquired = True
                            print 'add here'
                            MoveToTarget("HOME")
                

            elif Onum == 2:
                print "aliging to  yellow objects"
                foralign = CheckObject(YELLOWOBJECTS,2)
                if foralign == -1:
                    'yellow objects lost'
                else:
                    AlignData = mybot_OpenCV.FindObject(YELLOWOBJECTS)
                    if AlignData[0] < 200 and AlignData[0] > 0:
                        y = AlignObjectL(YELLOWOBJECTS)
                        if y == 1:
                            ALIGNED = True
                        else:
                            TargetAquired = True
                            print 'add here'
                            TargetData = mybot_OpenCV.FindObject(GREENOBJECTS)
                            if TargetData is not -1:
                                a = TargetData[0]
                                if a < 200 and a > 0 :
                                    rt= AlignToLeft(GREENOBJECTS)
                                    if rt == -1:
                                        print "chech iiii"
                                    else:
                                        mt = MoveToTarget('HOME')
                                        if mt == 1:
                                            TargetReached = True
                                            Run = False
                                        else:
                                            TargetAquired = False
                                elif TargetData[0] > 200 and TargetData[0] < 400:
                                    print "lucky case"
                                    mt = MoveToTarget()
                                    if mt == 1:
                                        TargetReached = True
                                        Run = False
                                    else:
                                        TargetAquired  = False
                                else:
                                    AlignToRight(GREENOBJECTS)
                                    mt = MoveToTarget()
                                    if mt == 1:
                                        TargetReached = True
                                        Run = False
                                    else:
                                        TargetAquired = False
                            else :
                                TargetAquired = False
                                print '? False Case'



                    elif AlignData[0] > 200 and AlignData[0] < 400:
                            print 'No Alignement error'
                            ALIGNED = True
                    else:

                        y = AlignObjectR(YELLOWOBJECTS)
                        if y == 1:
                            ALIGNED = True
                        else:
                            TargetAquired = True
                            TargetData = mybot_OpenCV.FindObject(GREENOBJECTS)
                            if TargetData is not -1:
                                a = TargetData[0]
                                if a < 200 and a > 0:
                                    rt = AlignToLeft(GREENOBJECTS)
                                    if rt == -1:
                                        print "chech iiii"
                                    else:
                                        mt = MoveToTarget('HOME')
                                        if mt == 1:
                                            TargetReached = True
                                            Run = False
                                        else:
                                            TargetAquired = False
                                elif TargetData[0] > 200 and TargetData[0] < 400:
                                    print "lucky case"
                                    mt = MoveToTarget()
                                    if mt == 1:
                                        TargetReached = True
                                        Run = False
                                    else :
                                        TargetAquired = False
                                else:
                                    AlignToRight(GREENOBJECTS)
                                    mt = MoveToTarget()
                                    if mt == 1:
                                        TargetReached = True
                                        Run = False
                                    else:
                                        TargetAquired = False

                            else:
                                TargetAquired = False
                                print '? False Case'
		   
                   


     if Onum == 1:
            resi = AvoidObstacle(PINKOBJECTS)
            if resi == 1:
                   ObstacleAvoided = True
                   print 'avoided yellow objects'
            else:
                   print 'hkj'
     if Onum == 2:
            resi = AvoidObstacle(YELLOWOBJECTS)
            if resi == 1:
                   ObstacleAvoided = True
                   print 'avoided yellow objects'
            else:
                   print 'hkj' 
     if ObstacleAvoided is True:

        print "Seraching For Target beyond obstacle"
        Run = True





mybot_serialport.closeserial()













