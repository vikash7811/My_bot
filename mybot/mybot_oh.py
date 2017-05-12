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

YELLOWOBJECTS = [20,43,57,25,255,255]
GREENOBJECTS = [56,46,64,110,255,255]
PINKOBJECTS = [5,187,36,27,255,255]
BLUEOBJECTS = [40,152,67,179,200,230]

#ThresholdArray = YELLOWOBJECTS







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
def CheckForTarget( ThresholdArray,tries):
    TargetData = [-1,-1,-1,-1,-1,-1]
    for x in range (0,tries):
        TargetData = mybot_OpenCV.FindObject(ThresholdArray)
        if TargetData[0] != -1:#Target present
            return TargetData #return straight away if correct symbol found


    return TargetData


#for moving to target after detection
def MoveToTarget(ThresholdArray):

    print "First Step  towards Target"
    TargetData = CheckForTarget(ThresholdArray,1)
    a = TargetData[2]
    while ( a != -1 and a > 25 ):
        time = int (a/16)
        print "Target not yet Reached"
        RobotData = RobotMove(ROBOTFORWARD, time,20,10,125)
        if RobotData[0] < 20 :
            print "sonar readig shows target reached or obstacle may be ahead "
            break;
        else:

            TargetData = CheckForTarget(ThresholdArray, 1)
            a = TargetData[2]

    TargetData = CheckForTarget(ThresholdArray,1)
    a = TargetData[2]
    if ( a < 25 and a > 0 ):
            print "target reached , Finally distance to target : " , a
            RobotData = Turn180()
            print "Target Reached"
            return 1

    else :
        print "no idea during movement to target",



def AlignToTarget(ThresholdArray):
    TargetData = CheckForTarget(ThresholdArray,1)
    x = TargetData[0]
    if x < 200 and x > 0:

        while x < 200 and x > 0:
            print (Fore.BLUE + "Target is on the left ")
            RobotData = RobotMove(ROBOTLEFT, 1, 0, 0, 255)
            print "turning left for alignmnt"
            RobotData = RobotMove(ROBOTFORWARD, 1, 0, 0, 255)
            print "moving foward while Left aligning"
            RobotData = RobotMove(ROBOTRIGHT, 1, 0, 0, 255)
            print "turning right while Left aligning"
            TargetData = CheckForTarget(ThresholdArray, 1)
            x = TargetData[0]
            print "updated x while left aligning , x: " , x

        TargetData = CheckForTarget(ThresholdArray, 1)
        if (TargetData[0] > 200 and TargetData[0] < 400):
            print "Alignment to left Done final x :" , TargetData[0]
            return 1
        else:
            print "target lost while left aligning"

    elif x > 400 :

        while x > 400:
            print (Fore.BLUE + "Target is on the right ")
            RobotData = RobotMove(ROBOTRIGHT, 1, 0, 0, 255)
            print "turning right for alignmnt"
            RobotData = RobotMove(ROBOTFORWARD, 1, 0, 0, 255)
            print "moving foward while right aligning"
            RobotData = RobotMove(ROBOTLEFT, 1, 0, 0, 255)
            print "turning left while right aligning"
            TargetData = CheckForTarget(ThresholdArray, 1)
            x = TargetData[0]
            print 'updated x value whle right aligning' , x

        TargetData = CheckForTarget(ThresholdArray, 1)
        if (TargetData[0] > 200 and TargetData[0] < 400):
            print "Alignment Done, final x value while right alignment , x :" , TargetData[0]
            return 1
        else:
            print "Target Lost while Left ALigning"


    elif x < 400 and x > 200:

        print "Target Ahead no need for alignment "
        return 1

    else :

        print "no idea what happened while alignment , x :" , x
        return -1



def ScanForTarget(ThresholdArray):

    print (Fore.BLUE + "Scanning for target")
    #Scan area in front of robot looking for an image target
    TargetData = CheckForTarget(ThresholdArray,1)#Capture image and check for symbol
    print "doubt 1 target data",TargetData
    if TargetData[0] == -1:
        print (Fore.BLUE + "No Target In Image")
        print TargetData
    else: #If the target has been found
        TargetData = CheckForTarget(ThresholdArray,1) #Check 1 time to see if target is still there
        if TargetData[0] == -1:
            print (Fore.BLUE + "Target Lost")
            print TargetData
        else: #Robot is looking at target, check again that target is still there
            print TargetData
            print "Target still in sight ,going for  aligning" , TargetData
            return 1

    return -1



def AlignObjectR(ThresholdArray):
        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        print 'aligning right with object'
        x = ObjectData[0]
        while  x > 400:
                RobotData = RobotMove(ROBOTRIGHT,1,0,0,255)
                RobotData = RobotMove(ROBOTFORWARD,1,0,0,255)
                RobotData = RobotMove(ROBOTLEFT,1,0,0,255)
                TargetData = CheckForTarget(GREENOBJECTS,1)
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
                TargetData = CheckForTarget(GREENOBJECTS,1)
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



def CheckObject(ThresholdArray, num):
     if num == 1:
        ObjectData = mybot_OpenCV.FindObject(PINKOBJECTS)
        return  1
     elif num == 2:
        ObjectData = mybot_OpenCV.FindObject(YELLOWOBJECTS)
        return 2






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
        while b > 20:
            time = int(b / 16)
            RobotData = RobotMove(ROBOTFORWARD, time, 20, 10, 255)
            print "robot is turning forward towards object"
            if RobotData[0] < 20:
                print "sonar shows object 20 cm ahead" , RobotData[0]
                RobotData = RobotMove(ROBOTRIGHT, 1 ,0,0,255)
                RobotData = RobotMove(ROBOTFORWARD,4,0,0,255)
                RobotData = RobotMove(ROBOTLEFT,1,0,0,255)
                print "Avoided Obstacle based on sonar reading "
                break
            else:
                ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
                print "further rechecked object"
                b = int(ObjectData[2])

        ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
        if ObjectData == [-1, -1, -1, -1, -1, -1]:
                 return 1
        else:
                 return -1







#Scans  for Obstacle Ahead
def Scan4Object(ThresholdArray, tries):

    for i in range (0,tries):

        for x in range(0, 4):
            ObjectData = mybot_OpenCV.FindObject(ThresholdArray)
            if ObjectData[0] == -1:
                print "No object found from scan"
                #RobotData = RobotMove(ROBOTLEFT,1,0,0,255)
                #print "turning to left in search of object"
            else:
                print "Object Found"
                return  1



    return -1






#Scans 360 for Target
def Scan4Target(ThresholdArray,tries):

    Result = -1
    for i in range (0,tries):
        for x in range(0, 4):
            Result = ScanForTarget(ThresholdArray)
            if Result == -1:
                print "No Target found from scan"
                # turn 90 degrees to the left
                #RobotData = RobotMove(ROBOTLEFT, 1, 0, 0,255)  # no sonar  so move always completes
                print "Turning to Left in search of target"
                return -1
            else:
                print "Target Aquired"
                return 1





#####MAIN PYTHON FILE


Run = True

"""while 1: 
	print GetData()
while 1:
 
	RobotMove(ROBOTLEFT,2,0,0,255)
	print "LEFT"
 	RobotMove(ROBOTFORWARD,10,5,5,255)        
	MoveForward()
	print "Moved f"
	MoveReverse()
	print "moved b"
	Turn180()
	print "180"
	RobotMove(ROBOTRIGHT , 1 , 0, 0,255) 
	print "turn right"""


while Run is True:



     Onum = -1
     ALIGNED = False
     TargetAquired = False
     ObjectAquired = False
     ObstacleAvoided = False

     ScanT = Scan4Target(GREENOBJECTS,1)
     if (ScanT == -1):
            print "target not found inside main"

     elif(ScanT == 1):
            print "Target found from scan"
            Align = AlignToTarget(GREENOBJECTS)
	    print"alignment  just executed"
            if Align == 1:
	    	print "alignment correctly done "
            	mt = MoveToTarget(GREENOBJECTS)
            	if mt == 1:
                            print "Mission Accomplised"
                            Run = False
                            break
                else :
                            print "Target Lost after Alignment"


            else:
                    print 'Target Lost While Alignning'




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
            RobotData = RobotMove(ROBOTFORWARD, 5, 20, 10,255)
            print "moving to anoher locaion"

     if ObjectAquired is True:

            print "entering object loop"

            if Onum == 1:

                    print "aliging to the pink  object"
                    foralign = CheckObject(PINKOBJECTS, 2)
                    if foralign == -1:
                        'pink  object lost'
                    else:
                        AlignData = mybot_OpenCV.FindObject(PINKOBJECTS)
                        if AlignData[0] < 200 and AlignData[0] > 0:
                            y = AlignObjectL(PINKOBJECTS)
                            if y == 1:
                                ALIGNED = True
                            elif y == 2:
                                TargetAquired = True
                                print 'add here'
                                TargetData = mybot_OpenCV.FindObject(PINKOBJECTS)
                                if TargetData[0] is not -1:

                                    Align = AlignToTarget(GREENOBJECTS)
                                    if Align == 1:
                                        mt = MoveToTarget(GREENOBJECTS)
                                        if mt == 1:
                                            print "Mission Accomplised while in object loop"
                                            Run = False

                                        else:
                                            print "Target Lost after Alignment in object loop"





                                else:
                                    TargetAquired = False
                                    print ' False Case'


                        elif AlignData[0] > 200 and AlignData[0] < 400:
                            print 'No Alignement error'
                            ALIGNED = True


                        else:

                             y = AlignObjectR(PINKOBJECTS)
                             if y == 1:
                                    ALIGNED = True
                             else:
                                    TargetAquired = True
                                    TargetData = mybot_OpenCV.FindObject(GREENOBJECTS)

                                    if TargetData[0] is not -1:

                                        Align = AlignToTarget(GREENOBJECTS)
                                        if Align == 1:
                                            mt = MoveToTarget(GREENOBJECTS)
                                            if mt == 1:
                                                print "Mission Accomplised while in object loop"
                                                Run = False

                                        else:
                                                print "Target Lost after Alignment in object loop"





                                    else:
                                        TargetAquired = False
                                        print ' False Case'

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
                                if TargetData[0] is not -1:

                                    Align = AlignToTarget(GREENOBJECTS)
                                    if Align == 1:
                                        mt = MoveToTarget(GREENOBJECTS)
                                        if mt == 1:
                                            print "Mission Accomplised while in yrllowobject loop"
                                            Run = False

                                        else:
                                            print "Target Lost after Alignment in yrlloeobject loop"





                                else:
                                    TargetAquired = False
                                    print ' False Case'

                                    TargetAquired = False
                                    print ' False Case'



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

                                if TargetData[0] is not -1:

                                    Align = AlignToTarget(GREENOBJECTS)
                                    if Align == 1:
                                        mt = MoveToTarget(GREENOBJECTS)
                                        if mt == 1:
                                            print "Mission Accomplised while in object loop"
                                            Run = False

                                        else:
                                            print "Target Lost after Alignment in object loop"





                                else:
                                    TargetAquired = False
                                    print ' False Case'



                   


     if ALIGNED is True and Onum == 1:
            resi = AvoidObstacle(PINKOBJECTS)
            if resi == 1:
                   ObstacleAvoided = True
                   print 'avoided yellow objects'
            else:
                   print 'hkj'
     if ALIGNED is True and Onum == 2:
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

