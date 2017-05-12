#include <math.h> 

unsigned char datapacket[4]={0,0,0,0};
int MotorSpeedPinL = 5; 
int MotorDirPinL = 6; 
int brakePinL = 7; 

int MotorSpeedPinR = 9; 
int MotorDirPinR = 10; 
int brakePinR = 2; 

unsigned char time;
unsigned char robotdirection;
unsigned char preamble1;
unsigned char preamble2; 
unsigned char centerS;
unsigned char rightS;
unsigned char speed;


void setup() 
{ 
	Serial.begin(9600); //start serial communication
 
	pinMode(MotorSpeedPinL, OUTPUT);
  	pinMode(MotorDirPinL, OUTPUT); 
  	pinMode(brakePinL,OUTPUT);
	
  	pinMode(MotorSpeedPinR, OUTPUT);
  	pinMode(MotorDirPinR, OUTPUT); 
  	pinMode(brakePinR,OUTPUT);


  	pinMode(13, OUTPUT);
  	digitalWrite(13, LOW); //onboard led off
 
} 


void loop() 
{ 
  
  	if (Serial.available()>=4)
  	{ 
    	Serial.println("Received PI");
    	digitalWrite(13, HIGH); //onboard led on
    	preamble1 = Serial.read();
    	Serial.println(preamble1); 
    	if(preamble1==255)
    	{
      
      		preamble2 = Serial.read();
      		Serial.println(preamble2);
      		if(preamble2==255)
      	{
        	unsigned char instruction = Serial.read();
        	Serial.println(instruction);
        	switch(instruction){
        	case 0: //get data - return a packets of all sensor data
            	Serial.read();
            	Serial.read();		 //read extra bytes of data to tidy up
            	readsensors();
            	writeserialdata(datapacket,4);
           	break;
          	case 1: //robot forward
            		time = Serial.read();
            		Serial.println(time);
            		centerS = Serial.read(); 
			rightS = Serial.read();
			speed = Serial.read();            		
			robotdirection = 1;
            		moverobot(robotdirection,time,centerS,rightS,speed);
            		readsensors();
            		writeserialdata(datapacket,4);
            		break;
          	case 2: //robot left
            		time = Serial.read();
            		Serial.println(time);
            		robotdirection = 2;
            		moverobot(robotdirection,time,centerS,rightS,speed);
            		readsensors();
            		writeserialdata(datapacket,4);
	    		break;
          	case 3: //robot right
            		time = Serial.read();
            		Serial.println(time);
            		robotdirection = 3;
            		moverobot(robotdirection,time,centerS,rightS,speed);
	    		readsensors();
            		writeserialdata(datapacket,4);
            		break;
          	case 4: //robot reverse
            		time = Serial.read();
            		Serial.println(time);
            		robotdirection = 4;
            		moverobot(robotdirection,time, centerS,rightS,speed);
	    		readsensors();
            		writeserialdata(datapacket,4);
            		break;
         
       
        	}
      
      	}

    	}
  	} 
}  









void moverobot(unsigned char robotdirection,unsigned char time, unsigned char centerS, unsigned char rightS,unsigned char speed)
{
  
  
    
   
	if(robotdirection == 1) //robot forward
   	{
     	Serial.println(robotdirection);
     	for(int i = 0 ; i < time ; i++){
		if (obstacleAhead(centerS) == 1){	
			stop();
			return ;  
		}
                   
                    else if(readsonarr() <= 6){
                                 Serial.println("something right obstacle is closing towards robot ");
                                 turnL();
                                 turnR();
                          
                             }
		else{
			moveF(speed);
			}
		}
      	}
  	else if(robotdirection == 2) //robot left
  	{
	     	Serial.println(robotdirection);
		turnL();
      
  	}
  	else if(robotdirection == 3) //robot right
  	{ 
                 if(readsonarr() <= 6){
                                 Serial.println("something right obstacle is closing towards robot ");
                                 turnL();
                                 turnR();
                          
                             }
		Serial.println(robotdirection);
   		turnR();
    	
 
    	}
  	else{	// robot reverse
		Serial.println(robotdirection);
		moveB(speed);
    	
		}


 	}


int obstacleAhead(unsigned char centerS){

	unsigned char sonarc = readsonarc();
	if (sonarc < centerS ){
		return 1;
	
	}	
	 
	else{
		return -1;
	}
}
 
  
unsigned char readsonarr(){
  //read right sonar sensor
  pinMode(11, OUTPUT);
  digitalWrite(11, LOW);             
  delayMicroseconds(2);
  digitalWrite(11, HIGH);            
  delayMicroseconds(10);
  digitalWrite(11, LOW);             
  pinMode(11, INPUT);
  int duration = pulseIn(11, HIGH);  
  int sonarr = (duration/58);         
  if(sonarr > 255)
  {
    sonarr = 255;
  }
  delay(10);

  return sonarr;
}
  




unsigned char readsonarc(){
	//read head sonar sensor
  	pinMode(3, OUTPUT);
  	digitalWrite(3, LOW);             
  	delayMicroseconds(2);
  	digitalWrite(3, HIGH);           
  	delayMicroseconds(10);
  	digitalWrite(3, LOW);             
 	pinMode(3, INPUT);
  	int duration = pulseIn(3, HIGH);  
  	int sonarc = (duration/58);        
  	if(sonarc > 255)
  	{
    	sonarc = 255;
  	}
  	delay(10);
  
  	return sonarc;
}
 


//Read all of the sensors and form data into a packet ready to send 
unsigned char readsensors() {
  
 
	unsigned char sonarc = readsonarc();

  	unsigned char sonarr = readsonarr();
  
  	//form data into a data packet array
  	datapacket[0] = sonarc;
  	datapacket[1] = sonarr;
  	datapacket[2] = 0;
  	datapacket[3] = 0;
  	return datapacket[4];

}

void writeserialdata(unsigned char datapacket[], int arraysize){
      Serial.write(255);
      Serial.write(255);

      for(int i = 0;i<arraysize;i++)    //write datapacket values to serial
      {
        Serial.write(datapacket[i]);
      }
}



void moveF(unsigned char speed){
	
	digitalWrite(MotorDirPinL,HIGH); 
	digitalWrite(brakePinL,LOW);
	analogWrite(MotorSpeedPinL,speed); 
      	digitalWrite(MotorDirPinR,HIGH); 
      	digitalWrite(brakePinR,LOW);
      	analogWrite(MotorSpeedPinR,speed);
	
      	delay(400);
      	
	digitalWrite(MotorDirPinL,LOW); 
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,0); 

      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,LOW);
     	analogWrite(MotorSpeedPinR,0);	

	return;
}


void moveB(unsigned char speed){
	digitalWrite(MotorDirPinL,LOW); 
	digitalWrite(brakePinL,HIGH);
	analogWrite(MotorSpeedPinL,speed); 
      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,HIGH);
      	analogWrite(MotorSpeedPinR,speed);
	
      	delay(200);
      	
	digitalWrite(MotorDirPinL,LOW); 
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,0); 

      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,LOW);
     	analogWrite(MotorSpeedPinR,0);	

	return;
}

void turnR(){
	digitalWrite(MotorDirPinL,HIGH); 
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,125); 

      	digitalWrite(MotorDirPinR,LOW);  
      	digitalWrite(brakePinR,HIGH);
      	analogWrite(MotorSpeedPinR,125); 
      	
	delay(200);
      	
	digitalWrite(MotorDirPinL,LOW);  
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,0); 

      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,LOW);
      	analogWrite(MotorSpeedPinR,0);
	return;
}

void stop(){
     	
	digitalWrite(MotorDirPinL,LOW); 
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,0); 

      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,LOW);
     	analogWrite(MotorSpeedPinR,0);	

	return;
}


void turnL(){
	digitalWrite(MotorDirPinL,LOW); 
      	digitalWrite(brakePinL,HIGH);
      	analogWrite(MotorSpeedPinL,125); 

      	digitalWrite(MotorDirPinR,HIGH);  
      	digitalWrite(brakePinR,LOW);
      	analogWrite(MotorSpeedPinR,125); 
      	
	delay(200);
      	
	digitalWrite(MotorDirPinL,LOW);  
      	digitalWrite(brakePinL,LOW);
      	analogWrite(MotorSpeedPinL,0); 

      	digitalWrite(MotorDirPinR,LOW); 
      	digitalWrite(brakePinR,LOW);
      	analogWrite(MotorSpeedPinR,0);
	return;

}
