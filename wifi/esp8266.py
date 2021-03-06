from machine import UART, Pin
import time
from httpParser import HttpParser

ESP8266_OK_STATUS = "OK\r\n"
ESP8266_ERROR_STATUS = "ERROR\r\n"
ESP8266_FAIL_STATUS = "FAIL\r\n"
ESP8266_WIFI_CONNECTED = "WIFI CONNECTED\r\n"
ESP8266_WIFI_GOT_IP_CONNECTED = "WIFI GOT IP\r\n"
ESP8266_WIFI_DISCONNECTED = "WIFI DISCONNECT\r\n"
ESP8266_WIFI_AP_NOT_PRESENT = "WIFI AP NOT FOUND\r\n"
ESP8266_WIFI_AP_WRONG_PWD = "WIFI AP WRONG PASSWORD\r\n"
ESP8266_TCP_CONNECTED = "TCP CONNECTED\r\n"
ESP8266_TCP_DISCONNECTED = "TCP CONNECTED\r\n"
ESP8266_BUSY_STATUS = "busy p...\r\n"
NO_ACCESS_POINT="NO AP"
TCP_STATUS_CONNECTED="STATUS:2" 
UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024*2


class ESP8266:
    """
    This is a class for access ESP8266 using AT commands
    Using this class, you access WiFi and do HTTP Post/Get operations.
    
    Attributes:
        uartPort (int): The UART port number of the RPI Pico's UART BUS [Default UART1]
        baudRate (int): UART Baud-Rate for communicating between RPI Pico's & ESP8266 [Default 115200]
        txPin (init): RPI Pico's Tx pin [Default Pin 4]
        rxPin (init): RPI Pico's Rx pin [Default Pin 5]
    """

    __rxData = None
    __txData = None
    __httpResponse = None

    def __init__(self, uartPort=1, baudRate=115200, txPin=4, rxPin=5):
        """
        The constructor for ESP8266 class
        
        Parameters:
            uartPort (int): The UART port number of the RPI Pico's UART BUS [Default UART1]
            baudRate (int): UART Baud-Rate for communicating between RPI Pico's & ESP8266 [Default 115200]
            txPin (init): RPI Pico's Tx pin [Default Pin 4]
            rxPin (init): RPI Pico's Rx pin [Default Pin 5]
        """
        self.__uartPort = uartPort
        self.__baudRate = baudRate
        self.__txPin = txPin
        self.__rxPin = rxPin
        #print(self.__uartPort,       self.__baudRate,        self.__txPin,        self.__rxPin)
        self.__uartObj = UART(self.__uartPort, baudrate=self.__baudRate, tx=Pin(self.__txPin), rx=Pin(
            self.__rxPin), txbuf=UART_Tx_BUFFER_LENGTH, rxbuf=UART_Rx_BUFFER_LENGTH)
        #print(self.__uartObj)

    def _createHTTPParseObj(self):
        """
        This is private function for create HTTP response every time
        before doing the HTTP Post/Get operation
        
        """
        if(self.__httpResponse != None):
            del self.__httpResponse
            self.__httpResponse = HttpParser()
        else:
            #del self.__httpResponse
            self.__httpResponse = HttpParser()

    def _sendToESP8266(self, atCMD, delay=1):
        """
        This is private function for complete ESP8266 AT command Send/Receive operation.
        """
        self.__rxData = str()
        self.__txData = atCMD
        print("---------------------------"+self.__txData)
        self.__uartObj.write(self.__txData)
        self.__rxData = bytes()

        time.sleep(delay)

        #while self.__uartObj.any()>0:
        #    self.__rxData += self.__uartObj.read(1)

        while True:
            #print(".")
            if self.__uartObj.any() > 0:
                #print(self.__uartObj.any())
                break

        while self.__uartObj.any() > 0:
            self.__rxData += self.__uartObj.read(UART_Rx_BUFFER_LENGTH)

        #print(self.__rxData)
        if ESP8266_OK_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_ERROR_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_FAIL_STATUS in self.__rxData:
            return self.__rxData
        elif ESP8266_BUSY_STATUS in self.__rxData:
            return "ESP BUSY\r\n"
        else:
            return None

    def startUP(self):
        """
        This function is used to check the communication between ESP8266 & RPI Pico
        
        Return:
            True if communication success with the ESP8266
            False if unable to communication with the ESP8266
        """
        retData = self._sendToESP8266("AT\r\n")
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False

    def reStart(self):
        """
        This function is used to Reset the ESP8266
        
        Return:
            True if Reset successfully done with the ESP8266
            False if unable to reset the ESP8266
        """
        retData = self._sendToESP8266("AT+RST\r\n")
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                time.sleep(5)
                #self.startUP()
                return self.startUP()
            else:
                return False
        else:
            False

    def echoING(self, enable=False):
        """
        This function is used to enable/diable AT command echo [Default set as false for diable Echo]
        
        Return:
            True if echo off/on command succefully initiate with the ESP8266
            False if echo off/on command failed to initiate with the ESP8266
        
        """
        if enable == False:
            retData = self._sendToESP8266("ATE0\r\n")
            if(retData != None):
                if ESP8266_OK_STATUS in retData:
                    return True
                else:
                    return False
            else:
                return False
        else:
            retData = self._sendToESP8266("ATE1\r\n")
            if(retData != None):
                if ESP8266_OK_STATUS in retData:
                    return True
                else:
                    return False
            else:
                return False

    def getVersion(self):
        """
        This function is used to get AT command Version details
        
        Return:
            Version details on success else None
        """
        retData = self._sendToESP8266("AT+GMR\r\n")
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                #print(str(retData,"utf-8"))
                retData = str(retData).partition(r"OK")[0]
                #print(str(retData,"utf-8"))
                retData = retData.split(r"\r\n")
                retData[0] = retData[0].replace("b'", "")
                retData = str(retData[0]+"\r\n"+retData[1]+"\r\n"+retData[2])
                return retData
            else:
                return None
        else:
            return None

    def reStore(self):
        """
        This function is used to reset the ESP8266 into the Factory reset mode & delete previous configurations
        Return:
            True on ESP8266 restore succesfully
            False on failed to restore ESP8266
        """
        retData = self._sendToESP8266("AT+RESTORE\r\n")
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return None
    """    
    def chcekSYSRAM(self):
        #retData = self._sendToESP8266("AT+SYSRAM?\r\n")   
        self.__rxData=b''
        self.__txData="AT+SYSRAM?\r\n"
        self.__uartObj.write(self.__txData)
        self.__rxData=bytes()
        
        time.sleep(2)
        
        while self.__uartObj.any()>0:
            self.__rxData += self.__uartObj.read(1)
            
        print(self.__rxData.decode())
        if ESP8266_OK_STATUS in self.__rxData:
            return self.__rxData
        else:
            return 1
    """

    def getCurrentWiFiMode(self):
        """
        This function is used to query ESP8266 WiFi's current mode [STA: Station, SoftAP: Software AccessPoint, or Both]
        
        Return:
            STA if ESP8266's wifi's current mode pre-config as Station
            SoftAP if ESP8266's wifi's current mode pre-config as SoftAP
            SoftAP+STA if ESP8266's wifi's current mode set pre-config Station & SoftAP
            None failed to detect the wifi's current pre-config mode
        """
        retData = self._sendToESP8266("AT+CWMODE_CUR?\r\n")
        if(retData != None):
            if "1" in retData:
                return "STA"
            elif "2" in retData:
                return "SoftAP"
            elif "3" in retData:
                return "SoftAP+STA"
            else:
                return None
        else:
            return None

    def setCurrentWiFiMode(self, mode=3):
        """
        This function is used to set ESP8266 WiFi's current mode [STA: Station, SoftAP: Software AccessPoint, or Both]
        
        Parameter:
            mode (int): ESP8266 WiFi's [ 1: STA, 2: SoftAP, 3: SoftAP+STA(default)]
        
        Return:
            True on successfully set the current wifi mode
            False on failed set the current wifi mode
        
        """
        txData = "AT+CWMODE_CUR="+str(mode)+"\r\n"
        retData = self._sendToESP8266(txData)
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def getDefaultWiFiMode(self):
        """
        This function is used to query ESP8266 WiFi's default mode [STA: Station, SoftAP: Software AccessPoint, or Both]
        
        Return:
            STA if ESP8266's wifi's default mode pre-config as Station
            SoftAP if ESP8266's wifi's default mode pre-config as SoftAP
            SoftAP+STA if ESP8266's wifi's default mode set pre-config Station & SoftAP
            None failed to detect the wifi's default pre-config mode
        
        """
        retData = self._sendToESP8266("AT+CWMODE_DEF?\r\n")
        if(retData != None):
            if "1" in retData:
                return "STA"
            elif "2" in retData:
                return "SoftAP"
            elif "3" in retData:
                return "SoftAP+STA"
            else:
                return None
        else:
            return None

    def setDefaultWiFiMode(self, mode=3):
        """
        This function is used to set ESP8266 WiFi's default mode [STA: Station, SoftAP: Software AccessPoint, or Both]
        
        Parameter:
            mode (int): ESP8266 WiFi's [ 1: STA, 2: SoftAP, 3: SoftAP+STA(default)]
            
        Return:
            True on successfully set the default wifi mode
            False on failed set the default wifi mode
            
        """
        txData = "AT+CWMODE_DEF="+str(mode)+"\r\n"
        retData = self._sendToESP8266(txData)
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def getAvailableAPs(self):
        """
        This function is used to query ESP8266 for available WiFi AccessPoints
        
        Retuns:
            List of Available APs or None
        """
        retData = str(self._sendToESP8266("AT+CWLAP\r\n", delay=10))
        if(retData != None):
            retData = retData.replace("+CWLAP:", "")
            retData = retData.replace(r"\r\n\r\nOK\r\n", "")
            retData = retData.replace(r"\r\n", "@")
            retData = retData.replace("b'(", "(").replace("'", "")
            retData = retData.split("@")
            retData = list(retData)
            apLists = list()

            for items in retData:
                data = str(items).replace("(", "").replace(")", "").split(",")
                data = tuple(data)
                apLists.append(data)

            return apLists
        else:
            return None

    def connectWiFi(self, ssid, pwd):
        """
        This function is used to connect ESP8266 with a WiFi AccessPoints
        
        Parameters:
            ssid : WiFi AP's SSID
            pwd : WiFi AP's Password
        
        Retuns:
            WIFI DISCONNECT when ESP8266 failed connect with target AP's credential
            WIFI AP WRONG PASSWORD when ESP8266 tried connect with taget AP with wrong password
            WIFI AP NOT FOUND when ESP8266 cann't find the target AP
            WIFI CONNECTED when ESP8266 successfully connect with the target AP
        """
        txData = "AT+CWJAP_CUR="+'"'+ssid+'"'+','+'"'+pwd+'"'+"\r\n"
        #print(txData)
        retData = self._sendToESP8266(txData, delay=15)
        #print(".....")
        #print(retData)
        if(retData != None):
            if "+CWJAP" in retData:
                if "1" in retData:
                    return ESP8266_WIFI_DISCONNECTED
                elif "2" in retData:
                    return ESP8266_WIFI_AP_WRONG_PWD
                elif "3" in retData:
                    return ESP8266_WIFI_AP_NOT_PRESENT
                elif "4" in retData:
                    return ESP8266_WIFI_DISCONNECTED
                else:
                    return None
            elif ESP8266_WIFI_CONNECTED in retData:
                if ESP8266_WIFI_GOT_IP_CONNECTED in retData:
                    return ESP8266_WIFI_CONNECTED
                else:
                    return ESP8266_WIFI_DISCONNECTED
            else:
                return ESP8266_WIFI_DISCONNECTED
        else:
            return ESP8266_WIFI_DISCONNECTED

    def testAT(self, command, delay=None):
        """
        This function is to test AT commands
        
        Return:
            False on no connection to WiFi
            True on good connection
        """
        if delay:
            retData = self._sendToESP8266(command + "\r\n", delay=5)
        else:
            retData = self._sendToESP8266(command + "\r\n")
        if retData:
            print("Returned from \'{}\': {}".format(command, retData))
        else:
            return False

    def getWifiAccessPointConnectionStatus(self):
        """
        This function is used to check connection status of ESP8266 with its WiFi AccessPoint
        
        Return:
            WIFI DISCONNECTED on no connection to WiFi
            WIFI CONNECTED on good connection
            False if no response
        """
        retData = self._sendToESP8266("AT+CWJAP?\r\n")
        if retData:
            print("Returned from \'AT+CWJAP?\': {}".format(retData))
            if NO_ACCESS_POINT not in retData.decode("utf-8"):
                return ESP8266_WIFI_CONNECTED
            else:
                return ESP8266_WIFI_DISCONNECTED
        else:
            return False

    def getTcpConnectionStatus(self):
        """
        This function is used to check TCP connection status of ESP8266 
        
        Return:
            TCP DISCONNECTED on no connection to WiFi
            TCP CONNECTED on good connection
            False if no response
        """
        retData = self._sendToESP8266("AT+CIPSTATUS\r\n")
        if retData:
            print("Returned from \'AT+CIPSTATUS\': {}".format(retData))
            if TCP_STATUS_CONNECTED in retData.decode("utf-8"):
                return ESP8266_TCP_CONNECTED
            else:
                return ESP8266_TCP_DISCONNECTED
        else:
            return False

    def disconnectWiFi(self):
        """
        This function is used to disconnect ESP8266 with a connected WiFi AccessPoints
        
        Return:
            False on failed to disconnect the WiFi
            True on successfully disconnected
        """
        retData = self._sendToESP8266("AT+CWQAP\r\n")
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            return False

    def deviceHostname(self,hostname=None):
        """
        This function is used to set a hostname for ESP8266
        
        Return:
            False on failed to set hostname
            True on successfully set hostname
        """
        if hostname:
            retData = self._sendToESP8266("AT+CWHOSTNAME=\"{}\"\r\n".format(hostname))
            if(retData != None):
                print(str(retData))
                if ESP8266_OK_STATUS in retData:
                    return True
                else:
                    return False
            else:
                return False
        else:
            retData = self._sendToESP8266("AT+CWHOSTNAME?\r\n")
            if(retData != None):
                return str(retData)
            else:
                return False

    def _createTCPConnection(self, link, port=80):
        """
        This function is used to create connect between ESP8266 and Host.
        Just like create a socket before complete the HTTP Get/Post operation.
        
        Return:
            False on failed to create a socket connection
            True on successfully create and establish a socket connection.
        """
        #self._sendToESP8266("AT+CIPMUX=0")
        txData = "AT+CIPSTART="+'"'+"TCP"+'"' + \
            ','+'"'+link+'"'+','+str(port)+"\r\n"
        #print(txData)
        retData = self._sendToESP8266(txData)
        #print(".....")
        #print(retData)
        if(retData != None):
            if ESP8266_OK_STATUS in retData:
                return True
            else:
                return False
        else:
            False

    def doHttpGet(self, host, path, user_agent="RPi-Pico", port=80):
        """
        This function is used to complete a HTTP Get operation
        
        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            post (int): HTTP post number [Default port number 80]
        
        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None
        
        """
        if(self._createTCPConnection(host, port) == True):
            self._createHTTPParseObj()
            #getHeader="GET "+path+" HTTP/1.1\r\n"+"Host: "+host+":"+str(port)+"\r\n"+"User-Agent: "+user_agent+"\r\n"+"\r\n";
            getHeader = "GET "+path+" HTTP/1.1\r\n"+"Host: " + \
                host+"\r\n"+"User-Agent: "+user_agent+"\r\n"+"\r\n"
            #print(getHeader,len(getHeader))
            txData = "AT+CIPSEND="+str(len(getHeader))+"\r\n"
            retData = self._sendToESP8266(txData)
            print('response: {}'.format(retData))
            if(retData != None):
                if ">" in retData:
                    retData = self._sendToESP8266(getHeader, delay=2)
                    self._sendToESP8266("AT+CIPCLOSE\r\n")
                    retData = self.__httpResponse.parseHTTP(retData)
                    return retData, self.__httpResponse.getHTTPResponse()
                else:
                    return 0, None
            else:
                return 0, None
        else:
            self._sendToESP8266("AT+CIPCLOSE\r\n")
            return 0, None

    def doHttpPost(self, host, path, user_agent="RPi-Pico", content_type="", content="", port=80):
        """
        This function is used to complete a HTTP Post operation
        
        Parameter:
            host (str): Host URL [ex: get operation URL: www.httpbin.org/ip. so, Host URL only "www.httpbin.org"]
            path (str): Get operation's URL path [ex: get operation URL: www.httpbin.org/ip. so, the path "/ip"]
            user-agent (str): User Agent Name [Default "RPi-Pico"]
            content_type (str): Post operation's upload content type [ex. "application/json", "application/x-www-form-urlencoded", "text/plain"
            content (str): Post operation's upload content 
            post (int): HTTP post number [Default port number 80]
        
        Return:
            HTTP error code & HTTP response[If error not equal to 200 then the response is None]
            On failed return 0 and None
        
        """
        if(self._createTCPConnection(host, port) == True):
            self._createHTTPParseObj()
            postHeader = "POST "+path+" HTTP/1.1\r\n"+"Host: "+host+"\r\n"+"User-Agent: "+user_agent+"\r\n" + \
                "Content-Type: "+content_type+"\r\n"+"Content-Length: " + \
                str(len(content))+"\r\n"+"\r\n"+content+"\r\n"
            #print(postHeader,len(postHeader))
            txData = "AT+CIPSEND="+str(len(postHeader))+"\r\n"
            retData = self._sendToESP8266(txData)
            if(retData != None):
                if ">" in retData:
                    retData = self._sendToESP8266(postHeader, delay=2)
                    #print(".......@@",retData)
                    self._sendToESP8266("AT+CIPCLOSE\r\n")
                    #print(self.__httpResponse)
                    retData = self.__httpResponse.parseHTTP(retData)
                    return retData, self.__httpResponse.getHTTPResponse()
                else:
                    return 0, None
            else:
                return 0, None
        else:
            self._sendToESP8266("AT+CIPCLOSE\r\n")
            return 0, None

    def __del__(self):
        """
        The destructor for ESP8266 class
        """
        print('Destructor called, ESP8266 deleted.')
        pass