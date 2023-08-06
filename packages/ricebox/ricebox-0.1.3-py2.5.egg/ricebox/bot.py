import sys
import socket
import string
from ricebox import special


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
            
    commands = {"!special":special.getSpecial, "!tomorrow":special.getFutureSpecial, "!quit":lambda: exit}

    while True:
        readbuffer=readbuffer+s.recv(1024)
        temp=string.split(readbuffer, "\n")
        print temp
        readbuffer=temp.pop( )

        for line in temp:
            line=string.rstrip(line)
            line=string.split(line)

            if(line[0]=="PING"):
                s.send("PONG %s\r\n" % line[1])

            if(line[1]=="INVITE"):
                s.send("JOIN #rubber\r\n")

            for command, result in commands.items():
                if(line[1]=="PRIVMSG" and line[2]=="#rubber" and command in " ".join(line)):
                    s.send("PRIVMSG #rubber :%s\r\n" % result())
            