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

class kml:

        def __init__(self, name):
                self.name = name
                self.file = open(name+'.kml','w')
                self.file.write('<kml xmlns="http://earth.google.com/kml/2.0">\n\n')
                self.file.write('<Folder>\n\n')
                self.file.write('<name>')
                self.file.write(name)
                self.file.write('</name>\n\n')
                self.file.write('<open>1</open>\n\n')
                self.file.write('<Placemark>\n\n')
                self.file.write('<description>')
                self.file.write(name)
                self.file.write('</description>\n\n')
                self.file.write('<name>')
                self.file.write(name)
                self.file.write('</name>\n\n')
                self.file.write('<styleUrl>root://styleMaps#default+nicon=0x467+hicon=0x477</styleUrl>\n\n')
                self.file.write('<Style>\n\n')
                self.file.write('<LineStyle id="khLineStyle989">\n\n')
                self.file.write('<color>7f0000ff</color>\n\n')
                self.file.write('<width>4</width>\n\n')
                self.file.write('</LineStyle>\n\n')
                self.file.write('</Style>\n\n')
                self.file.write('<LineString>\n\n')
                self.file.write('<tessellate>1</tessellate>\n\n')
                self.file.write('<coordinates>\n\n')

        def add_point(self, x, y, z=0.0):
                self.file.write(str(x))
                self.file.write(', ')
                self.file.write(str(y))
                self.file.write(', ')
                self.file.write(str(z))
                self.file.write('\n\n')

        def close(self):
                self.file.write('</coordinates>\n\n')
                self.file.write('</LineString>\n\n')
                self.file.write('</Placemark>\n\n')
                self.file.write('</Folder>\n\n')
                self.file.write('</kml>\n\n')
                self.file.close()
