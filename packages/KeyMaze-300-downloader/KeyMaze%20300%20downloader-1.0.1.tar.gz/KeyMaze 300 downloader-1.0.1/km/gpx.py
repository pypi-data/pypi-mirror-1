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

class gpx:

        def __init__(self, name):
                self.name = name
                self.file = open(name+'.gpx','w')
                self.file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                self.file.write('<gpx\nversion="1.0"\nxmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\nxmlns="http://www.topografix.com/GPX/1/0"\nxsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n')
#<time>2008-07-22T21:19:37Z</time>
#<bounds minlat="48.888570000" minlon="2.321040000" maxlat="48.949450000" maxlon="2.568290000"/>
                self.file.write('<trk>\n<name>')
		self.file.write(name)
		self.file.write('</name>\n<trkseg>\n')


        def add_point(self, x, y, z=0.0):
	        self.file.write('<trkpt lat="')
                self.file.write(str(x))
                self.file.write('" lon="')
                self.file.write(str(y))
                self.file.write('">\n\t<ele>')
                self.file.write(str(z))
                self.file.write('</ele>\n</trkpt>\n')

        def close(self):
                self.file.write('</trkpt>\n</trkseg>\n</trk>\n</gpx>\n')
                self.file.close()