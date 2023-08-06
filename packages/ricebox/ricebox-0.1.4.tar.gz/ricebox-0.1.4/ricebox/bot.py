import sys
import socket
import string
from ricebox import special
import datetime

def connect():

    HOST="irc.freenode.net"
    PORT=6667
    NICK="specialbot"
    IDENT="special"
    REALNAME="Specialbot"
    readbuffer=""

    s=socket.socket( )
    s.connect((HOST, PORT))
    s.send("NICK %s\r\n" % NICK)
    s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
    s.send("JOIN #rubber\r\n")
            
    commands = {"!special":special.getSpecial, "!tomorrow":special.getSpecialTomorrow, "!named":special.getSpecialByName, "!quit":lambda: sys.exit(0)}
    
    last = 0
    counter = 0
    
    while True:
        counter += 1
        readbuffer=readbuffer+s.recv(1024)
        temp=string.split(readbuffer, "\n")
        #print temp
        readbuffer=temp.pop( )
        dotm = datetime.datetime.now().day
        
        if counter > 13 and dotm != last and datetime.datetime.now().hour >= 11:
            if "weet" in special.getSpecial() or "urry" in special.getSpecial():
                s.send("PRIVMSG #rubber :Excuse me gents, the special today is %s.\n" % (special.getSpecial()))
            last = dotm
        
        
        for line in temp:
            line=string.rstrip(line)
            line=string.split(line)

            if(line[0]=="PING"):
                s.send("PONG %s\r\n" % line[1])

            if(line[1]=="INVITE"):
                s.send("JOIN #rubber\r\n")

            for command, result in commands.items():
                if(line[1]=="PRIVMSG" and line[2]=="#rubber" and command in " ".join(line)):
                    if command == '!named':
                        search_text = list(line[line.index(':!named')+1:])
                        s.send("PRIVMSG #rubber :%s\r\n" % result(search_text))
                    else:
                        s.send("PRIVMSG #rubber :%s\r\n" % result())
            