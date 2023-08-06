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



def getNiceName(in_div):
	result = ""
	for idx in range(1,len(in_div)):
		next_word = str(in_div[idx]).strip()
		
		#Can't be arsed fixing my parser
		if next_word.lower() == 'fried' and idx==len(in_div)-1:
			next_word = 'Fried Rice'
		result = result + next_word
		if result[len(result)-1] not in ['-']:
			result = result + " "
	return result[:len(result)-1]

def getSpecialByName(search_text=None):
    p = getParsedBody()
    search_text = [a.lower() for a in search_text]
    
    for common_word in ['and','or']:
    	if common_word.lower() in search_text:
    		search_text.remove(common_word)
    
    best_match = -1
    best_match_div = []
    day_of_month = datetime.now().day
    for div in p.div_results:
    	div_text = ' '.join(div)
    	match = 0
    	for word in search_text:
    		if word.lower() in div_text.lower():
    			match = match + 1
       			if match > best_match and str(div[0]).isdigit() and int(div[0]) >= int(day_of_month): 
       				best_match = match
         			best_match_div = div
    if best_match_div:
    	today_weekday = datetime.now().weekday()
    	special_day = int(best_match_div[0])
    	offset = special_day - day_of_month
    	if offset <= 7:
    		days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    	 	return "%s on %s" % (getNiceName(best_match_div),days[(today_weekday+offset)%7])
    	else:
    		special_date = datetime(datetime.now().year,datetime.now().month,special_day)
    		return getNiceName(best_match_div) + " on %s/%s" % (special_date.day,special_date.month)
    	

def getSpecialByDate(date=None):
    p = getParsedBody()
    if not date:
    	day_of_month = datetime.now().day
    else:
    	day_of_month = date.day
    
    found_special = False
    for div in p.div_results:
      if str(div[0]) == str(day_of_month):
      	return getNiceName(div)
    	found_special=True

    if not found_special:
      return None

def getSpecialTomorrow():
	return getSpecialByDate(date=datetime.now() + timedelta(days=1))

def getSpecial(date=None):
	return getSpecialByDate(date=datetime.now())

def get(args=None):
    argv = sys.argv
    if '-t' in argv:
    	special = getSpecialTomorrow()
    	if special:
    		print "The special tomorrow is: %s" % (special)
    	else:
    		print "There is no special tomorrow"
        return True
    
    if '-n' in argv:
     	search_text = list(argv[argv.index('-n')+1:])
     	print getSpecialByName(search_text)
     	return True

    special = getSpecial()
    if special:
    	print "Today's special is: %s" % (special)
    	return True

if __name__ == "__main__":
	get()