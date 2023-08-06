#!/usr/bin/python

# The aim of this script is to download recorded information on the keymaze300 GPS
#Python script to download trackpoints and waypoints form a KeyMaze 300 GPS.
    #Copyright (C) 2008  Julien TOUS

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.

## @package gpsd4
#  This package provides an easy to use interface to KeyMaze gps.
#
# 

import struct
import kml
import gpx
import sys
import getopt
import os, pwd

## Test the presence of pyserial
# @return If pyserial is not present, the user is invited to install it.


try:
        import serial
except ImportError:
        print("You need to have python-serial installed to run km.")
        print("Get it from your package manager or http://pyserial.sourceforge.net.")
        sys.exit(2)

firmware_version = 0
download_baud_rate = 4800
upload_baud_rate = 38400
download_dir = os.getenv('HOME') # We may want to add an option to put the downloaded file in a specific location instead of ~

def file_to_serial(f, s):
        """Send the given file (f) to the given open serial port (s)"""
        Str=f.read()
        s.write(Str)        

def read_waypoints(ser):
        # Asking for WayPoints     
        f=open('../../share/km/waypoints.bin','rb') # This file contains the command to upload the WayPoints
        file_to_serial(f, ser)
        f.close()

        binary_garbage = open(download_dir + '/waypoint_garbage.bin', 'ab') # All WayPoints information which isn't used goes there
        ways = open(download_dir + '/waypoints.text','a')
        # Getting something
        binary_garbage.write(ser.read(3)) 
        waypoint_count = 0 # Don't know yet if waypoint_count and waypoint_number will always be the same              
        while True:
                # Getting the WayPoint number
                temp_hundredth = struct.unpack(">B", ser.read(1))[0]
                # If the last waypoint was the last we got, next read will give ''                
                # If not it's the tenth value of the waypoint number                
                check_next = ser.read(1)
                if check_next == '':
                        break
                else:
                        waypoint_count = waypoint_count + 1
                temp_tenth = struct.unpack(">B", check_next)[0]
                temp_unit = struct.unpack(">B", ser.read(1))[0]
                waypoint_number = (temp_hundredth - 48) * 100 + (temp_tenth - 48) * 10 + (temp_unit - 48) * 1 
                ways.write('\n')
                ways.write(str(waypoint_number))
                # Getting 00 41 4C. Don't know what it means !
                binary_garbage.write(ser.read(3))  
                # Getting "icon". Don't know what it is either !
                icon = struct.unpack(">H", ser.read(2))[0]
                ways.write(' ')
                ways.write(str(icon))
                # Getting elevation
                elevation = struct.unpack(">H", ser.read(2))[0]
                ways.write(' ')
                ways.write(str(elevation))                
                # Getting waypoint location
                x = struct.unpack(">i", ser.read(4))[0]
                ways.write(' ')
                ways.write(str(x))                     
                y = struct.unpack(">i", ser.read(4))[0]
                ways.write(' ')
                ways.write(str(y))
        ways.close()
        binary_garbage.close()  
        print "  Got ", waypoint_count, " WayPoints."                
  
def read_track(ser):
        tracks = open(download_dir + '/trackpoints.text','a') # Text file with all understood informations
        tracks.write('\n\n')
        binary_garbage = open(download_dir + '/trackpoint_garbage.bin', 'ab') # All TrackPoints information which isn't used goes there
        # Getting 0x80. Don't what it is for
        binary_garbage.write(ser.read(1))
        # Getting something. This changes all the time but i haven't corelated this to anything yet.
        binary_garbage.write(ser.read(2))
        # Getting the year
        year = struct.unpack(">B", ser.read(1))[0]
        tracks.write('20'+str(year))
        tracks.write('-')
        # Getting the month
        month = struct.unpack(">B", ser.read(1))[0]        
        tracks.write(str(month))
        tracks.write('-')
        # Getting the day
        day = struct.unpack(">B", ser.read(1))[0]
        tracks.write(str(day))
        tracks.write(':')
        # Getting the hour
        hour = struct.unpack(">B", ser.read(1))[0]
        tracks.write(str(hour))
        tracks.write(':')
        # Getting the minute
        minute = struct.unpack(">B", ser.read(1))[0]
        tracks.write(str(minute))
        tracks.write(':')
        # Getting the second
        second = struct.unpack(">B", ser.read(1))[0]
        tracks.write(str(second))
        tracks.write(' ')
        # Getting the training duration
        duration = struct.unpack(">i", ser.read(4))[0] # Need to verify it realy uses 4 bytes (actualy it begins with 0x00 0x00)

        kml_name = download_dir+ '/20' + str(year) + '-' + str(month) + '-' + str(day) + 'T' + str(hour) + ':' + str(minute) + ':' + str(second)
        # Creating a .kml file 
        kml_file = kml.kml(kml_name)

	gpx_name = download_dir+ '/20' + str(year) + '-' + str(month) + '-' + str(day) + 'T' + str(hour) + ':' + str(minute) + ':' + str(second)
        # Creating a .gpx file
        gpx_file = gpx.gpx(gpx_name)

        tracks.write(' \nTraining duration : ')
        tracks.write(str(duration))
        # Getting the training distance
        distance = struct.unpack(">i", ser.read(4))[0] # Need to verify it realy uses 4 bytes (actualy it begins with 0x00 0x00)
        tracks.write(' \nTraining distance : ')
        tracks.write(str(distance)) 
        # Getting the speed if written
        if (firmware_version >= 2.70):
                ser.read(2) # Not used yet
        # Getting the number of point
        number_of_points = struct.unpack(">H", ser.read(2))[0] # Need to verify it realy uses 2 bytes (actualy it begins with 0x00)
        tracks.write(' \nNumber of points : ')
        tracks.write(str(number_of_points + 1))
        # Getting something
        binary_garbage.write(ser.read(2))
        # Getting all the trackpoints locations
        for i in range(0,number_of_points):
                x = struct.unpack(">i", ser.read(4))[0]
                tracks.write(' \n')
                tracks.write(str(i))
                tracks.write(' : ')
                tracks.write(str(x))
                y = struct.unpack(">i", ser.read(4))[0]
                tracks.write(' ')
                tracks.write(str(y))
                # Adding point to the .kml file
                kml_file.add_point(y/100000.0, x/100000.0)
		gpx_file.add_point(y/100000.0, x/100000.0)
                
        # Getting the last byte 
        binary_garbage.write(ser.read(1)) # Should sort out what is it for.
        kml_file.close()
	gpx_file.close()
        binary_garbage.close()
        tracks.close()
        print "    Got ", number_of_points + 1, " points." 
        return (year + month + day + hour + minute + second + duration + distance + number_of_points)


def read_trackpoints(ser):
        print("  Getting TrackPoints set 1.")
        # Asking for the first TrackPoints set
        f=open('../../share/km/firsttrackpoints.bin','rb') # This file contains the command to upload the first TrackPoints set
        file_to_serial(f, ser)
        f.close()

        # Receiveing the first TrackPoints set
        is_valid = read_track(ser)

        trackpoints_count = 1
        # Testing the validity of the previous TrackPoints set.
        # 0 means it was the last.
        while is_valid != 0:
                # Asking for the next training data
                trackpoints_count = trackpoints_count + 1
                print "  Getting TrackPoints set ", trackpoints_count        
                f=open('../../share/km/nexttrackpoints.bin','rb') # This file contains the command to upload any TrackPoints set but the first
                file_to_serial(f, ser)
                f.close()
                is_valid = read_track(ser)

def upload_firmware(serial_port, firmware_name):
        firmware=open(firmware_name,'rb')
        ser = configure_serial_port(serial_port, upload_baud_rate)

        # Initiate upload
        ser.writes(struct.pack(">BBBB", 0x11, 0x00, 0x01, 0x00))

        # Sending the firmware

        # The firmware file is cut in 1024 bytes pieces
        # Each page is annouced by 0x11 0x04 0x01 followed by the page number
        # An extra byte is sent in the end of each page
        # the GPS will send 0x88 when it's ready to receive a new page
        closure = struct.pack(">B", 0x1) # Actualy on decathlon software this value seems random
        preamble = struct.pack(">BBB", 0x11, 0x04, 0x01)
        for counter in range(1, 128):
                page = firmware.read(1024)
                packet = preamble + struct.pack(">B", counter) + page + closure
                ser.write(packet)
                ser.read(2) # getting 88
        ser.close()

def configure_serial_port(which_port, baud_rate):
        try:               
                ser = serial.Serial(which_port, baud_rate)
        except serial.serialutil.SerialException:
                print "Serial port ", which_port, "can't be opened."
                print("You can specify which serial port to use with -d option.")
                sys.exit(2)         
        print("Configuring serial port")                
        ser.bytesize=serial.EIGHTBITS
        ser.parity=serial.PARITY_NONE
        ser.stopbits=serial.STOPBITS_ONE
        ser.timeout=2
        ser.xonxoff=0
        ser.rtscts=0
        ser.flushInput()
        ser.flushOutput()
        return ser


def usage():
        print("Usage km-downloader [OPTION]")
	print("    -h, --help               print this help and exit")
        print("    -v, --version            print version information and exit.")
        print("    -d, --device             specify which serial device to use.")
        print("    -o, --output-directory   specify where to write output files.")
        print("    -w, --waypoints          download waypoints.")
        print("    -t, --trackpoints        download trackpoints.")
        print("    -u, --update-firmware    specify the new firmware to be installed.")
        print("    -V, --firmware-version   specify the version number of the firmware.")
        print("For more informations, please see:")
        print("<http://gpsd4.tuxfamily.org>.")


def version():
        print("km 0.9")
        print("Copyright (C) 2008 Julien TOUS.")
        print("This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
        print("Written by Julien TOUS and Vincent-Xavier JUMEL") # I believe a simple way to parse the AUTHOR file exist ?


def main(argv):
        try:
                opts, args = getopt.getopt(argv, "hvd:o:wtu:V:", ["help", "version", "device=", "output-directory=", "waypoints", "trackpoints", "update-firmware=", "firmware-version="])
        except  getopt.GetoptError:
                usage()
                sys.exit(2)
        
        # Should use a better default name
        # select from /dev/ttyUSB0 for linux, COM1 for windows and anything that suit well MacOS 
        serial_port = '/dev/ttyUSB0' 

        #get_trackpoints and get_waypoints *must* be initialized (to false)
	get_waypoints = False
	get_trackpoints = False
        update_firmware = False
        # Adapting behaviour to option and arguments
        for opt, arg in opts:
                if opt in ("-h", "--help"):
                        usage()                     
                        sys.exit()                  
                elif opt in ("-v", "--version"):
                        version()
                        sys.exit()               
                elif opt in ("-d", "--device"):
                        serial_port = arg
                elif opt in ("-w", "--waypoints"):
                        get_waypoints = True
                elif opt in ("-t", "--trackpoints"):
                        get_trackpoints = True
                elif opt in ("-o", "--output-directory"):
                        download_dir = arg
                elif opt in ("-u", "--update-firmware"):
                        get_waypoints = True
                        get_trackpoints = True
                        update_firmware = False #Not finished yet. This is disabled for now
                        firmware_name = arg
                        print("Downloading TrackPoints and WayPoints before updating firmware.")
                elif opt in ("-V", "--firmware-version"):
                        firmware_version = arg

        # If none of -t or -w has been passed download both TrackPoints and WayPoints
        if ( (get_trackpoints == False) and (get_waypoints == False) ):
                get_waypoints = True
                get_trackpoints = True

        # Configuring serial port
        # udev should call the script with the appropriate device name using -d
        ser = configure_serial_port(serial_port, download_baud_rate) 

        if get_trackpoints:
                # Asking for TrackPoints
                print "Getting TrackPoints"
                read_trackpoints(ser)        

        if get_waypoints:        
                # Asking for WayPoints
                print "Getting WayPoints"
                read_waypoints(ser)

        # Closing serial port
        ser.close()

        if update_firmware:
                # Uploading firmware
                print("Uploading firmware")
                upload_firmware(serial_port, firmware_name)

        # Finishing
        quit()

if __name__ == '__main__':
        main(sys.argv[1:])
