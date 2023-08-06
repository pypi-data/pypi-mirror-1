#       utils.py
#       
#       Copyright 2009 ahmed youssef <xmonader@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


def to_hrtime(var):
    time=""
    ch="AM"
    if int(var)>12:
        time+=str(int(var)-12)
        ch="PM"
    elif int(var)==12:
        time+=str(int(var))
        ch="PM"
    else:
        time+=str(int(var))
        
    time+=":"
    var -=int(var)
    var *=60
    min=int(var)
    time+=str(min)
    time+=":"
    var -=int(var)
    var *=60
    sec=int(var)
    time+=str(sec)
    time+=" "+ch
    return time
