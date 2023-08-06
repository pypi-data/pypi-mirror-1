#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
#       prayertime.py
#       
#       Copyright 2010 ahmed youssef <xmonader@gmail.com>
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

##THIS CODE IS A PYTHONIC PORT OF -prayertime- part of AL MOAZEN PROJECT BY SUDANIX http://qt-ar.org/community/viewtopic.php?f=3&t=176&start=0
#

__author__="Ahmed Youssef"
__all__=['Season', 'Calendar', 'Prayertime', 'Mazhab']

from math import atan, asin, acos ,cos, sin, tan


def remove_duplication(var):
    if var > 360:
        var/=360   
        var-=int(var) 
        var*=360
    return var;
          
class Season(object):
    Winter, Summer=0,1

class Calendar(object):
        UmmAlQuraUniv,\
        EgyptianGeneralAuthorityOfSurvey,\
        UnivOfIslamicSciencesKarachi,\
        IslamicSocietyOfNorthAmerica,\
        MuslimWorldLeague=range(5)

class Mazhab(object):
    Default, Hanafi=0,1

class Date(object):
    def __init__(self, year, month, day):
        self.year=year
        self.month=month
        self.day=day
        
class Time(object):
    
    def __init__(self, time, isAM=False):
        self.hour=None
        self.minute=None
        self.second=None
        self.zone=None
        self.time=self.convertToTime(time, isAM)
        
        
    def text(self):
        return self.time
    
    def __str__(self):
        return self.text()
    
    def convertToTime(self, var, isAM):
        time=''
        intvar=int(var) #var is double.
        if isAM:
            if intvar%12 and intvar%12 < 12:
                self.zone="AM"
            else:
                self.zone="PM"
        else:
            self.zone="PM"
    
        if intvar>12:
            time+=str(intvar%12)
            self.hour=intvar%12
            
        elif intvar%12 == 12:
            time+=str(intvar)
            self.hour=intvar
        
        else:
            time+=str(intvar)
            self.hour=intvar
            
        time+=":"
        var-=intvar
        var*=60
        min=int(var)
        self.minute=min
        time +=str(min)
        
        time +=":"
        
        var-=int(var)
        var*=60
        sec=int(var)
        self.second=sec
        time+=str(sec)
        time+=" "
        
        time+=self.zone
        
        return time


class Coordinate(object):
    
    def __init__(self, longitude, latitude, zone):
        self.longitude=longitude
        self.latitude=latitude
        self.zone=zone
        
DegToRad = 0.017453292
RadToDeg = 57.29577951

class Prayertime(object):
        
    def __init__(self, longitude, latitude, zone, year, month, day, cal=Calendar.UmmAlQuraUniv, mazhab=Mazhab.Default,season=Season.Winter):
        self.longitude=longitude
        self.latitude=latitude
        self.zone=zone
        self.coordinate=Coordinate(longitude, latitude, zone)
        self.date=Date(year, month, day)
        self.calendar=cal
        self.mazhab=mazhab
        self.season=season
        self._shrouk=None
        self._fajr=None
        self._zuhr=None
        self._asr=None
        self._maghrib=None
        self._isha=None
        self.dec=0
        
    
    def shroukTime(self):
        return Time(self._shrouk, True)
    
    def fajrTime(self):
        return Time(self._fajr, True)
    
    def zuhrTime(self):
        return Time(self._zuhr, True)
    
    def asrTime(self):
        return Time(self._asr)
    
    def maghribTime(self):
        return Time(self._maghrib)
    
    def ishaTime(self):
        return Time(self._isha)
    
    def calculate(self):
        year=self.date.year
        month=self.date.month
        day=self.date.day
        longitude=self.coordinate.longitude
        latitude=self.coordinate.latitude
        zone=self.coordinate.zone
        julianDay=(367*year)-int(((year+int((month+9)/12))*7)/4)+int(275*month/9)+day-730531.5;
        sunLength=280.461+0.9856474*julianDay
        sunLength=remove_duplication(sunLength)
        middleSun=357.528+0.9856003*julianDay
        middleSun=remove_duplication(middleSun)
        
        lamda=sunLength+1.915*sin(middleSun*DegToRad)+0.02*sin(2*middleSun*DegToRad);
        lamda=remove_duplication(lamda);
        
        obliquity=23.439-0.0000004*julianDay;
    
        alpha=RadToDeg*atan(cos(obliquity*DegToRad)*tan(lamda*DegToRad));
    
        if 90 < lamda < 180 :
            alpha+=180
        elif 100 < lamda < 360:
            alpha+=360;
    
        ST=100.46+0.985647352*julianDay;
        ST=remove_duplication(ST);
    
        self.dec=RadToDeg*asin(sin(obliquity*DegToRad)*sin(lamda*DegToRad))
    
        noon=alpha-ST;
    
        if noon < 0:
            noon+=360;
    
        UTNoon=noon-longitude;
        localNoon=(UTNoon/15)+zone;
        zuhr=localNoon;                #Zuhr Time.
        maghrib=localNoon+self.equation(-0.8333)/15;      # Maghrib Time
        shrouk=localNoon-self.equation(-0.8333)/15;      # Shrouk Time
    
        fajrAlt=0;
        ishaAlt=0;
        
        if  self.calendar == Calendar.UmmAlQuraUniv:
            fajrAlt=-19
        elif self.calendar == Calendar.EgyptianGeneralAuthorityOfSurvey :
            fajrAlt=-19.5
            ishaAlt=-17.5
        elif self.calendar == Calendar.MuslimWorldLeague:
            fajrAlt=-18
            ishaAlt=-17
        elif self.calendar == Calendar.IslamicSocietyOfNorthAmerica:
            fajrAlt=ishaAlt=-15
        elif self.calendar == Calendar.UnivOfIslamicSciencesKarachi:
            fajrAlt=ishaAlt=-18
    
    
        fajr=localNoon-self.equation(fajrAlt)/15;  # Fajr Time
        isha=localNoon+self.equation(ishaAlt)/15;  # Isha Time
    
        if self.calendar == Calendar.UmmAlQuraUniv :
            isha=maghrib+1.5
            
        asrAlt=0
        
        if self.mazhab == Mazhab.Hanafi :
            asrAlt=90-RadToDeg*atan(2+tan(abs(latitude-self.dec)*DegToRad));
        else:
            asrAlt=90-RadToDeg*atan(1+tan(abs(latitude-self.dec)*DegToRad));
            
        asr=localNoon+self.equation(asrAlt)/15;   # Asr Time.
        
        #Add one hour to all times if the season is Summmer.
        if self.season == Season.Summer:
            fajr+=1;
            shrouk+=1;
            zuhr+=1;
            asr+=1;
            maghrib+=1;
            isha+=1;
    
        self._shrouk=shrouk
        self._fajr=fajr
        self._zuhr=zuhr
        self._asr=asr
        self._maghrib=maghrib
        self._isha=isha
    
        
    def equation(self, alt):
        return RadToDeg*acos((sin(alt*DegToRad)-sin(self.dec*DegToRad)*sin(self.coordinate.latitude*DegToRad))/(cos(self.dec*DegToRad)*cos(self.coordinate.latitude*DegToRad)));
    
    def _report(self):
        print self.fajrTime()
        print self.shroukTime()
        print self.zuhrTime()
        print self.asrTime()
        print self.maghribTime()
        print self.ishaTime()
        

if __name__=="__main__":
    p=Prayertime(46.7825,24.6505,3, 2009, 10, 5)
    p.calculate()
    p._report()
    
