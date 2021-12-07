EESchema Schematic File Version 4
LIBS:raspi_pico_christmas_tree-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	6050 2750 6250 2750
Wire Wire Line
	2650 2300 2500 2300
$Comp
L power:PWR_FLAG #FLG01
U 1 1 61ADD969
P 2500 2100
F 0 "#FLG01" H 2500 2175 50  0001 C CNN
F 1 "PWR_FLAG" H 2500 2273 50  0000 C CNN
F 2 "" H 2500 2100 50  0001 C CNN
F 3 "~" H 2500 2100 50  0001 C CNN
	1    2500 2100
	1    0    0    -1  
$EndComp
Wire Wire Line
	2500 2100 2650 2100
Connection ~ 2500 2100
$Comp
L power:VCC #PWR01
U 1 1 61AE0134
P 2400 2100
F 0 "#PWR01" H 2400 1950 50  0001 C CNN
F 1 "VCC" V 2418 2227 50  0000 L CNN
F 2 "" H 2400 2100 50  0001 C CNN
F 3 "" H 2400 2100 50  0001 C CNN
	1    2400 2100
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2400 2100 2500 2100
$Comp
L power:VCC #PWR010
U 1 1 61AE11AC
P 6250 2750
F 0 "#PWR010" H 6250 2600 50  0001 C CNN
F 1 "VCC" H 6267 2923 50  0000 C CNN
F 2 "" H 6250 2750 50  0001 C CNN
F 3 "" H 6250 2750 50  0001 C CNN
	1    6250 2750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR04
U 1 1 61AE2A5A
P 2400 2300
F 0 "#PWR04" H 2400 2050 50  0001 C CNN
F 1 "GND" V 2405 2172 50  0000 R CNN
F 2 "" H 2400 2300 50  0001 C CNN
F 3 "" H 2400 2300 50  0001 C CNN
	1    2400 2300
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR08
U 1 1 61AE475B
P 5700 1900
F 0 "#PWR08" H 5700 1650 50  0001 C CNN
F 1 "GND" H 5705 1727 50  0000 C CNN
F 2 "" H 5700 1900 50  0001 C CNN
F 3 "" H 5700 1900 50  0001 C CNN
	1    5700 1900
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR09
U 1 1 61AE5413
P 6150 6000
F 0 "#PWR09" H 6150 5750 50  0001 C CNN
F 1 "GND" H 6155 5827 50  0000 C CNN
F 2 "" H 6150 6000 50  0001 C CNN
F 3 "" H 6150 6000 50  0001 C CNN
	1    6150 6000
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 5950 6150 5950
Wire Wire Line
	6150 5950 6150 6000
$Comp
L power:GND #PWR03
U 1 1 61AE8551
P 1950 4200
F 0 "#PWR03" H 1950 3950 50  0001 C CNN
F 1 "GND" H 1955 4027 50  0000 C CNN
F 2 "" H 1950 4200 50  0001 C CNN
F 3 "" H 1950 4200 50  0001 C CNN
	1    1950 4200
	-1   0    0    -1  
$EndComp
Wire Wire Line
	1950 4200 1950 4150
Wire Wire Line
	1950 4150 2050 4150
$Comp
L power:GND #PWR012
U 1 1 61AE93C3
P 6700 4150
F 0 "#PWR012" H 6700 3900 50  0001 C CNN
F 1 "GND" H 6705 3977 50  0000 C CNN
F 2 "" H 6700 4150 50  0001 C CNN
F 3 "" H 6700 4150 50  0001 C CNN
	1    6700 4150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR05
U 1 1 61AEC498
P 3300 5900
F 0 "#PWR05" H 3300 5650 50  0001 C CNN
F 1 "GND" H 3305 5727 50  0000 C CNN
F 2 "" H 3300 5900 50  0001 C CNN
F 3 "" H 3300 5900 50  0001 C CNN
	1    3300 5900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3300 5900 3300 5800
Wire Wire Line
	6050 3750 6700 3750
Wire Wire Line
	6700 3650 6700 3750
Connection ~ 6700 3750
Wire Wire Line
	6700 3750 7150 3750
$Comp
L power:VCC #PWR011
U 1 1 61B11929
P 6700 3350
F 0 "#PWR011" H 6700 3200 50  0001 C CNN
F 1 "VCC" H 6717 3523 50  0000 C CNN
F 2 "" H 6700 3350 50  0001 C CNN
F 3 "" H 6700 3350 50  0001 C CNN
	1    6700 3350
	1    0    0    -1  
$EndComp
$Comp
L power:PWR_FLAG #FLG02
U 1 1 61B127E1
P 6850 2900
F 0 "#FLG02" H 6850 2975 50  0001 C CNN
F 1 "PWR_FLAG" H 6850 3073 50  0000 C CNN
F 2 "" H 6850 2900 50  0001 C CNN
F 3 "~" H 6850 2900 50  0001 C CNN
	1    6850 2900
	1    0    0    -1  
$EndComp
$Comp
L power:VEE #PWR015
U 1 1 61B141F9
P 7300 2950
F 0 "#PWR015" H 7300 2800 50  0001 C CNN
F 1 "VEE" H 7317 3123 50  0000 C CNN
F 2 "" H 7300 2950 50  0001 C CNN
F 3 "" H 7300 2950 50  0001 C CNN
	1    7300 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	6050 2950 6850 2950
Wire Wire Line
	6850 2900 6850 2950
Connection ~ 6850 2950
Wire Wire Line
	6850 2950 7300 2950
Wire Wire Line
	6700 3800 6700 3750
Wire Wire Line
	6700 4150 6700 4100
$Comp
L power:GND #PWR018
U 1 1 61B1A210
P 7800 3750
F 0 "#PWR018" H 7800 3500 50  0001 C CNN
F 1 "GND" V 7805 3622 50  0000 R CNN
F 2 "" H 7800 3750 50  0001 C CNN
F 3 "" H 7800 3750 50  0001 C CNN
	1    7800 3750
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7800 3750 7550 3750
Wire Wire Line
	3200 5050 3200 5200
Wire Wire Line
	3400 5050 3400 5200
Wire Wire Line
	6100 1300 6250 1300
Wire Wire Line
	6250 1300 6250 1400
Wire Wire Line
	6250 1400 6100 1400
Wire Wire Line
	6100 1500 6250 1500
Wire Wire Line
	6250 1500 6250 1400
Connection ~ 6250 1400
Wire Wire Line
	5700 1700 5700 1800
Wire Wire Line
	5700 1800 6250 1800
Wire Wire Line
	6250 1800 6250 1500
Connection ~ 5700 1800
Wire Wire Line
	5700 1800 5700 1900
Connection ~ 6250 1500
Wire Wire Line
	5700 1800 5200 1800
Wire Wire Line
	5200 1800 5200 1500
Wire Wire Line
	5200 1500 5300 1500
Wire Wire Line
	1950 3450 1950 3550
Wire Wire Line
	1950 3550 2050 3550
$Comp
L power:VEE #PWR07
U 1 1 61B23DA4
P 5700 800
F 0 "#PWR07" H 5700 650 50  0001 C CNN
F 1 "VEE" H 5717 973 50  0000 C CNN
F 2 "" H 5700 800 50  0001 C CNN
F 3 "" H 5700 800 50  0001 C CNN
	1    5700 800 
	1    0    0    -1  
$EndComp
Wire Wire Line
	5300 1400 5050 1400
Wire Wire Line
	5050 1200 5050 1400
Connection ~ 5050 1400
Wire Wire Line
	6050 3550 6500 3550
Wire Wire Line
	5050 2300 6500 2300
Wire Wire Line
	6500 2300 6500 3550
Wire Wire Line
	5050 1400 5050 2300
Wire Wire Line
	3950 1300 3950 4750
Wire Wire Line
	3950 4750 4050 4750
Wire Wire Line
	3950 1300 4700 1300
Wire Wire Line
	5700 800  5700 850 
Wire Wire Line
	5050 900  5050 850 
Wire Wire Line
	5050 850  5700 850 
Connection ~ 5700 850 
Wire Wire Line
	5700 850  5700 1100
Wire Wire Line
	4700 900  4700 850 
Wire Wire Line
	4700 850  5050 850 
Connection ~ 5050 850 
Wire Wire Line
	4700 1200 4700 1300
Connection ~ 4700 1300
Wire Wire Line
	4700 1300 5300 1300
NoConn ~ 3450 3650
NoConn ~ 2050 3750
NoConn ~ 2050 3850
Wire Wire Line
	3450 3750 3650 3750
Wire Wire Line
	3650 3750 3650 3700
$Comp
L power:VEE #PWR06
U 1 1 61B766D1
P 3650 3700
F 0 "#PWR06" H 3650 3550 50  0001 C CNN
F 1 "VEE" H 3500 3700 50  0000 C CNN
F 2 "" H 3650 3700 50  0001 C CNN
F 3 "" H 3650 3700 50  0001 C CNN
	1    3650 3700
	-1   0    0    -1  
$EndComp
$Comp
L power:VEE #PWR02
U 1 1 61B7900F
P 1950 3450
F 0 "#PWR02" H 1950 3300 50  0001 C CNN
F 1 "VEE" H 1967 3623 50  0000 C CNN
F 2 "" H 1950 3450 50  0001 C CNN
F 3 "" H 1950 3450 50  0001 C CNN
	1    1950 3450
	-1   0    0    -1  
$EndComp
Wire Wire Line
	3200 4550 4050 4550
Wire Wire Line
	3400 4750 3400 4650
Wire Wire Line
	3400 4650 4050 4650
Wire Wire Line
	3200 4550 3200 4750
NoConn ~ 7550 3950
NoConn ~ 7150 3950
NoConn ~ 2650 2200
$Comp
L power:GND #PWR014
U 1 1 61BD5FA9
P 6950 4650
F 0 "#PWR014" H 6950 4400 50  0001 C CNN
F 1 "GND" V 6955 4522 50  0000 R CNN
F 2 "" H 6950 4650 50  0001 C CNN
F 3 "" H 6950 4650 50  0001 C CNN
	1    6950 4650
	0    1    1    0   
$EndComp
Wire Wire Line
	6950 4650 7050 4650
$Comp
L power:VCC #PWR013
U 1 1 61BD97A7
P 6950 4550
F 0 "#PWR013" H 6950 4400 50  0001 C CNN
F 1 "VCC" V 6968 4677 50  0000 L CNN
F 2 "" H 6950 4550 50  0001 C CNN
F 3 "" H 6950 4550 50  0001 C CNN
	1    6950 4550
	0    -1   -1   0   
$EndComp
Text Label 7650 5150 2    50   ~ 0
D1
Text Label 7650 5250 2    50   ~ 0
RES
Text Label 7650 5350 2    50   ~ 0
DC
Text Label 7650 5450 2    50   ~ 0
CS
$Comp
L power:VCC #PWR017
U 1 1 61BE653E
P 7400 4950
F 0 "#PWR017" H 7400 4800 50  0001 C CNN
F 1 "VCC" V 7400 5150 50  0000 C CNN
F 2 "" H 7400 4950 50  0001 C CNN
F 3 "" H 7400 4950 50  0001 C CNN
	1    7400 4950
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7650 4950 7400 4950
$Comp
L power:GND #PWR016
U 1 1 61BE13E1
P 7400 4850
F 0 "#PWR016" H 7400 4600 50  0001 C CNN
F 1 "GND" V 7405 4722 50  0000 R CNN
F 2 "" H 7400 4850 50  0001 C CNN
F 3 "" H 7400 4850 50  0001 C CNN
	1    7400 4850
	0    1    1    0   
$EndComp
Wire Wire Line
	7650 4850 7400 4850
Text Label 7650 5050 2    50   ~ 0
D0
Text Label 7650 4950 2    50   ~ 0
VCC
Text Label 7650 4850 2    50   ~ 0
GND
Wire Wire Line
	6050 4050 6550 4050
Wire Wire Line
	6550 4050 6550 5050
Wire Wire Line
	6550 5050 7650 5050
Wire Wire Line
	7650 5150 6450 5150
Wire Wire Line
	6450 4150 6050 4150
Wire Wire Line
	6350 4250 6350 5250
Wire Wire Line
	6350 5250 7650 5250
Wire Wire Line
	6050 4250 6350 4250
Wire Wire Line
	6050 4450 7050 4450
Wire Wire Line
	6950 4550 7050 4550
Wire Wire Line
	6450 5150 6450 4150
Wire Wire Line
	6050 3950 6250 3950
Wire Wire Line
	6250 3950 6250 5350
Wire Wire Line
	6250 5350 7650 5350
Wire Wire Line
	6050 3850 6150 3850
Wire Wire Line
	6150 3850 6150 5450
Wire Wire Line
	6150 5450 7650 5450
NoConn ~ 6050 5850
NoConn ~ 6050 5450
NoConn ~ 6050 5350
NoConn ~ 6050 5150
NoConn ~ 6050 5050
NoConn ~ 6050 4950
NoConn ~ 6050 4750
NoConn ~ 6050 4650
NoConn ~ 6050 4550
NoConn ~ 6050 4350
NoConn ~ 6050 3650
NoConn ~ 6050 3350
NoConn ~ 6050 3250
NoConn ~ 6050 3050
NoConn ~ 6050 2850
NoConn ~ 4050 3250
NoConn ~ 4050 3350
NoConn ~ 4050 3550
NoConn ~ 4050 3650
NoConn ~ 4050 3750
NoConn ~ 4050 3850
NoConn ~ 4050 4150
NoConn ~ 4050 4250
NoConn ~ 4050 4350
NoConn ~ 4050 4450
Wire Wire Line
	3450 3950 4050 3950
Wire Wire Line
	3450 4050 4050 4050
$Comp
L power:PWR_FLAG #FLG0101
U 1 1 61C6C31E
P 2500 2300
F 0 "#FLG0101" H 2500 2375 50  0001 C CNN
F 1 "PWR_FLAG" H 2500 2473 50  0000 C CNN
F 2 "" H 2500 2300 50  0001 C CNN
F 3 "~" H 2500 2300 50  0001 C CNN
	1    2500 2300
	1    0    0    1   
$EndComp
Connection ~ 2500 2300
Wire Wire Line
	2500 2300 2400 2300
$Comp
L power:GND #PWR0101
U 1 1 61AE7882
P 6150 5650
F 0 "#PWR0101" H 6150 5400 50  0001 C CNN
F 1 "GND" V 6150 5450 50  0000 C CNN
F 2 "" H 6150 5650 50  0001 C CNN
F 3 "" H 6150 5650 50  0001 C CNN
	1    6150 5650
	0    -1   -1   0   
$EndComp
Wire Wire Line
	6150 5650 6050 5650
$Comp
L Memory_EEPROM:24LC512 U3
U 1 1 61AC357F
P 5700 1400
F 0 "U3" H 5900 1700 50  0000 C CNN
F 1 "24LC512" H 5400 1700 50  0000 C CNN
F 2 "Housings_DIP:DIP-8_W7.62mm" H 5700 1400 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/21754M.pdf" H 5700 1400 50  0001 C CNN
	1    5700 1400
	-1   0    0    -1  
$EndComp
$Comp
L Device:LED_Dual_ACA D1
U 1 1 61AC681A
P 3300 5500
F 0 "D1" H 3300 5925 50  0000 C CNN
F 1 "LED_ACA" H 3300 5834 50  0000 C CNN
F 2 "LEDs:LED_D5.0mm-3" H 3300 5500 50  0001 C CNN
F 3 "~" H 3300 5500 50  0001 C CNN
	1    3300 5500
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R5
U 1 1 61AC77CC
P 6700 3500
F 0 "R5" H 6770 3546 50  0000 L CNN
F 1 "R" H 6770 3455 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 6630 3500 50  0001 C CNN
F 3 "~" H 6700 3500 50  0001 C CNN
	1    6700 3500
	1    0    0    -1  
$EndComp
$Comp
L Device:R R4
U 1 1 61AC8223
P 5050 1050
F 0 "R4" H 5120 1096 50  0000 L CNN
F 1 "R" H 5120 1005 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4980 1050 50  0001 C CNN
F 3 "~" H 5050 1050 50  0001 C CNN
	1    5050 1050
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 61AC8842
P 3200 4900
F 0 "R1" H 3270 4946 50  0000 L CNN
F 1 "R" H 3270 4855 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3130 4900 50  0001 C CNN
F 3 "~" H 3200 4900 50  0001 C CNN
	1    3200 4900
	-1   0    0    1   
$EndComp
$Comp
L Device:R R2
U 1 1 61AC97E6
P 3400 4900
F 0 "R2" H 3470 4946 50  0000 L CNN
F 1 "R" H 3470 4855 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3330 4900 50  0001 C CNN
F 3 "~" H 3400 4900 50  0001 C CNN
	1    3400 4900
	1    0    0    -1  
$EndComp
$Comp
L Device:C C1
U 1 1 61ACB887
P 6700 3950
F 0 "C1" H 6815 3996 50  0000 L CNN
F 1 "C" H 6815 3905 50  0000 L CNN
F 2 "Capacitors_THT:C_Disc_D3.0mm_W2.0mm_P2.50mm" H 6738 3800 50  0001 C CNN
F 3 "~" H 6700 3950 50  0001 C CNN
	1    6700 3950
	1    0    0    -1  
$EndComp
$Comp
L ESP8266-01_ESP-01:ESP8266-01_ESP-01 U1
U 1 1 61ACC534
P 2750 3850
F 0 "U1" H 2750 4417 50  0000 C CNN
F 1 "ESP-01" H 2750 4326 50  0000 C CNN
F 2 "esp01:ESP-01" H 2750 3850 50  0001 L BNN
F 3 "" H 2750 3850 50  0001 L BNN
F 4 "V1.2" H 2750 3850 50  0001 L BNN "PARTREV"
F 5 "AI-Thinker" H 2750 3850 50  0001 L BNN "MANUFACTURER"
F 6 "11.2 mm" H 2750 3850 50  0001 L BNN "MAXIMUM_PACKAGE_HEIGHT"
F 7 "Manufacturer recommendations or IPC 7351B" H 2750 3850 50  0001 L BNN "STANDARD"
	1    2750 3850
	-1   0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 61ACA97F
P 4700 1050
F 0 "R3" H 4770 1096 50  0000 L CNN
F 1 "R" H 4770 1005 50  0000 L CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4630 1050 50  0001 C CNN
F 3 "~" H 4700 1050 50  0001 C CNN
	1    4700 1050
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push_Dual SW1
U 1 1 61AC50C9
P 7350 3750
F 0 "SW1" H 7350 4035 50  0000 C CNN
F 1 "Button" H 7350 3944 50  0000 C CNN
F 2 "stomp:Switches-Push_switch_THD" H 7350 3950 50  0001 C CNN
F 3 "~" H 7350 3950 50  0001 C CNN
	1    7350 3750
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J2
U 1 1 61BD0D9B
P 7250 4550
F 0 "J2" H 7330 4592 50  0000 L CNN
F 1 "WS8212" H 7330 4501 50  0000 L CNN
F 2 "def-footprints:CONN_HEADER_1_3" H 7250 4550 50  0001 C CNN
F 3 "~" H 7250 4550 50  0001 C CNN
	1    7250 4550
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x07 J3
U 1 1 61BDC0E3
P 7850 5150
F 0 "J3" H 7930 5192 50  0000 L CNN
F 1 "SSD1306" H 7930 5101 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x07_Pitch2.54mm" H 7850 5150 50  0001 C CNN
F 3 "~" H 7850 5150 50  0001 C CNN
	1    7850 5150
	1    0    0    -1  
$EndComp
$Comp
L Connector:Barrel_Jack_Switch J1
U 1 1 61C57C18
P 2950 2200
F 0 "J1" H 2720 2242 50  0000 R CNN
F 1 "PWR" H 3100 2400 50  0000 R CNN
F 2 "Connectors:BARREL_JACK" H 3000 2160 50  0001 C CNN
F 3 "~" H 3000 2160 50  0001 C CNN
	1    2950 2200
	-1   0    0    -1  
$EndComp
$Comp
L raspberrypi_pico:SC0915 U2
U 1 1 61ACE4E2
P 5050 4350
F 0 "U2" H 5050 6217 50  0000 C CNN
F 1 "RaspiPico" H 5050 6126 50  0000 C CNN
F 2 "raspberrypi_pico:MODULE_SC0915" H 5050 4350 50  0001 L BNN
F 3 "" H 5050 4350 50  0001 L BNN
F 4 "1.6" H 5050 4350 50  0001 L BNN "PARTREV"
F 5 "Raspberry Pi" H 5050 4350 50  0001 L BNN "MANUFACTURER"
F 6 "3.73mm" H 5050 4350 50  0001 L BNN "MAXIMUM_PACKAGE_HEIGHT"
F 7 "Manufacturer Recommendations" H 5050 4350 50  0001 L BNN "STANDARD"
	1    5050 4350
	1    0    0    -1  
$EndComp
$EndSCHEMATC
