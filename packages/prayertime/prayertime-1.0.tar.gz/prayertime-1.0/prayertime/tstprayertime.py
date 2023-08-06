#!usr/bin/env python

#       tstprayertime.py
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



#4786|70|Cairo -- (State: Al Qahirah)|Al Qahirah|300599|312599|200|1
#4787|70|Cairo Governorate -- (State: Al Qahirah)|Al Qahirah|300432|312266|200|1

import prayertime as pt
from utils import to_hrtime


def renderPT(p):
    p.calculate()
    print "*"*20
    print "LONGITUDE: ", p.longitude()
    print "LATITUDE: ", p.latitude()
    print "Zone: ", p.zone()
    print "Fajr: ", to_hrtime(p.fajrTime())
    print "Zuhr: ", to_hrtime(p.zuhrTime())
    print "Asr: ", to_hrtime(p.asrTime())
    print "Maghrib: ", to_hrtime(p.maghribTime())
    print "Isha: ", to_hrtime(p.ishaTime())
    print "*"*20
    
    

def test():
#PrayerTime::PrayerTime(double lot,double lat,int zone,int day,int month,int year,Calender calender,Mazhab mazhab,Season season):
    p=pt.PrayerTime(31.2599, 30.0599, 2, 18, 5, 2009)
    renderPT(p)


def time_tostring(t):
    return strftime("%H:%M:%S", t)

test()
