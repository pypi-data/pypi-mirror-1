#!/usr/local/bin/python
"""
	Ricebox daily special getter :)
	by Alan & Matt
"""


import httplib
import sgmllib
import time
from datetime import datetime,timedelta
import sys

class RbParser(sgmllib.SGMLParser):
	div_results = []
	in_day=False
	day_text=[]
	
	def start_div(self, attrs):
		for attr in attrs:
			if attr[0].lower()=='class' and attr[1].lower().find('normal')!=-1:
				self.in_day=True
				self.day_text=[]
		
	def end_div(self):
		if self.in_day:
			self.in_day=False
			if self.day_text:
				self.div_results.append(self.day_text)
	
	def handle_data(self,text):
		if self.in_day:
			filtered_text = text
			for bad_char in [' ','\n','\r']:
				filtered_text = filtered_text.replace(bad_char,'')
			if filtered_text:
				self.day_text.append(text)

			
def parse_url(URL):
	result = {}
	URL = URL.replace("http://","")
	host = URL[:URL.index("/")]
	path = URL[URL.index("/"):]
	filename = URL.split("/")[len(URL.split("/"))-1]
	result = {'host':host,'path':path,'filename':filename}
	return result
	

def get_url(URL):
	URL = parse_url(URL)
	conn = httplib.HTTPConnection(URL['host'])
	conn.putrequest("GET",URL['path'])
	conn.endheaders()
	result = conn.getresponse()
	body = result.read()
	conn.close()
	return body


def getParsedBody():
    body = get_url("http://freespace.virgin.net/kuanwai.law/page3.html")
    #Got response
    p = RbParser()
    p.feed(body)
    return p

def getSpecial(date=None):
    p = getParsedBody()
    if not date:
    	day_of_month = datetime.now().day
    else:
    	day_of_month = date.day
    
    found_special = False
    for div in p.div_results:
      if str(div[0]) == str(day_of_month):
    	result = ""
      	for idx in range(1,len(div)):
      	  result = result + str(div[idx]).strip() + " "
    	return result
    	found_special=True

    if not found_special:
      return None


def getFutureSpecial(days=None,date=None):
	if days:
		return getSpecial(date=datetime.now() + timedelta(days=int(days)))
	if date:
		return getSpecial(date=date)

def get(args=None):
    if '-t' in sys.argv:
        special = getFutureSpecial(days=1)
        dname = "tomorrow"
    else:
        special = getSpecial()
        dname = "today"
    if special is None:
        print "Sorry, no special %s :(" % (dname, )
    else:
        print """%s's special is %s""" % (dname, special)

if __name__ == "__main__":
    if '-t' in sys.argv:
        getFutureSpecial(days=1)
    else:
        get()
