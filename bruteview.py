#!/usr/bin/env python

#python-geoip
#python-geoip-geolite2

import datetime
from geoip import geolite2
import os.path
import re

users_f={}
users_p={}
ip_f={}
ip_p={}
country_f={}
country_p={}
gps_f={}
gps_p={}

def gps_to_str(gps):
	return str(gps[0])+','+str(gps[1])

def analysis(date,user,ip,passed):
	geo=geolite2.lookup(ip)
	country="unknown"
	gps="unknown"
	if geo is not None:
		country=geo.country
		gps=gps_to_str(geo.location)
	if passed:
		if not user in users_p:
			users_p[user]=0
		users_p[user]+=1
		if not ip in ip_p:
			ip_p[ip]=0
		ip_p[ip]+=1
		if not country in country_p:
			country_p[country]=0
		country_p[country]+=1
		if not gps in gps_p:
			gps_p[gps]=0
		gps_p[gps]+=1
	else:
		if not user in users_f:
			users_f[user]=0
		users_f[user]+=1
		if not ip in ip_f:
			ip_f[ip]=0
		ip_f[ip]+=1
		if not country in country_f:
			country_f[country]=0
		country_f[country]+=1
		if not gps in gps_f:
			gps_f[gps]=0
		gps_f[gps]+=1

def parse_ssh_entry(line,year):
	date=datetime.datetime.strptime(str(year)+' '+line[0:15],'%Y %b %d %H:%M:%S')
	pass_str='password for '
	pass_ind=line.find(pass_str)
	passed=None
	if 'Failed password' in line:
		passed=False
	if 'Accepted password' in line:
		passed=True
	if passed!=None and pass_ind>=0:
		tokens=line[pass_ind+len(pass_str):].split()
		if len(tokens)>=3:
			user=tokens[0]
			ip=tokens[2]
			analysis(date,user,ip,passed)

try:
	file_name='auth.log'
	file_year=datetime.datetime.fromtimestamp(os.path.getmtime(file_name)).year
	file=open(file_name,'r')
	for line in file:
		line=line.strip()
		line=line.replace('invalid user ','')
		if 'ssh' in line:
			times=1
			repeat_str='message repeated '
			repeat_ind=line.find(repeat_str)
			if repeat_ind>=0:
				repeat_bkt=line.find('[',repeat_ind)
				if repeat_bkt>=0 and repeat_ind<repeat_bkt:
					times=int(re.search(r'\d+',line[repeat_ind:-1]).group())
					line=line[0:repeat_ind]+line[repeat_bkt+2:-1]
			parse_ssh_entry(line,file_year)
	print(gps_f)
	exit(0)
except Exception as error:
	print(error)
	exit(1)