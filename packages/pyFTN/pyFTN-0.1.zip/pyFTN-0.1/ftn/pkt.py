import struct
import mmap
from msg import MSG
from addr import *

# FSC-0048 Type 2+ support

class PKT:
  def __init__(self, file=None):
    self.msg = []
    if file:
      #read packet header
      #read messages
      f=open(file,"r+b")
      f.seek(0,2)
      m=mmap.mmap(f.fileno(),f.tell())

      h=m[:58]
      pos=58

      (fnode,tnode,year,month,day,hour,minute,second,	# 00-0F
       baud,sig,fnet,tnet,prod_l,rev_h,password,	# 10-21
       qfzone,qtzone,auxnet,CW_xchgcopy,prod_h,rev_l,   # 22-2B
       capability,fzone,tzone,fpoint,tpoint             # 2C-35
       ) = struct.unpack("<12H2B8s4H2B5H4x",h)

      assert(sig==2)
      #print fnet,fnode,tnet,tnode,password

      self.password=password
      self.source=(fzone or qfzone,fnet,fnode,fpoint)
      self.destination=(tzone or qtzone,tnet,tnode,tpoint)
      if year<1900:
        year+=1900
      self.date=(year,month,day,hour,minute,second)

      #print self.source, self.destination

      #print "now reading messages"
      msg_n=0
      while pos!=len(m): # for packets without 00 00 terminator
        try:
          (sig,)=struct.unpack("<H",m[pos:pos+2])
        except:
          raise "Unexpected end of packet"
        pos+=2
        if sig!=2:
          if sig!=0:
	    raise "bad signature (message %d)"%msg_n
	  else:
            break
        (fnode,tnode,fnet,tnet,attr,cost,date)=struct.unpack("<6H20s",m[pos:pos+32])
	pos+=32
	while len(date) and (date[-1]=="\0"): date=date[:-1]

        e=m.find("\0",pos)
        assert(e!=-1)
        if e>pos+36:
          e=pos+36
	tname=m[pos:e]
	pos=e+1

        e=m.find("\0",pos)
        assert(e!=-1)
        if e>pos+36:
          e=pos+36
	fname=m[pos:e]
	pos=e+1

        e=m.find("\0",pos)
        assert(e!=-1)
        if e>pos+72:
          e=pos+72
        subj=m[pos:e]
	pos=e+1

        e=m.find("\0",pos)
        assert(e!=-1)
	body=m[pos:e]
	pos=e+1

	#print "load msg", msg_n, tnet, tnode
	msg=MSG()
	msg.load( (fname,(0,fnet,fnode,0)),
	        (tname,(0,tnet,tnode,0)),subj,date,attr,cost,body )
	#print m
	self.msg+=[msg]
        msg_n+=1

      #if msg_n==10000:
      #  raise "paket too large (10000 messages is maximum limit)"

    else:
      pass

  def __str__(self):
    return "SRC: %s\n"%addr2str(self.source) + \
      "DST: %s\n"%addr2str(self.destination) + \
      "PASS %s\n"%self.password + \
      "DATE %04d-%02d-%02d %02d:%02d:%02d\n"%self.date + \
      "Messages: %d\n"%len(self.msg) + \
"===============================================================================\n".join([""]+map(str,self.msg)+[""])

  def save(self, file):
    f=open(file, "wb")
    print `self.source`, `self.destination`
    print `self.date`,`self.password`
    f.write(struct.pack("<13H8s12H",self.source[2],self.destination[2],
      self.date[0],self.date[1],self.date[2],self.date[3],
      self.date[4],self.date[5],0,2,self.source[1],self.destination[1],0,
       self.password,
       self.source[0],self.destination[0],
       0,0,0,1,self.source[0],self.destination[0],
       self.source[3],self.destination[3],0,0))
    for m in self.msg:
      f.write(struct.pack("<7H20s", 2, m.orig[1][2],m.dest[1][2],
        m.orig[1][1],m.dest[1][1],m.attr,m.cost,m.date)+
        m.dest[0][:35]+"\0"+m.orig[0][:35]+"\0"+m.subj[:71]+"\0"+
        m.make_body()+"\0")

    f.write("\0\0")

if __name__=="__main__":
  from glob import glob
  j=0
  for file in glob("*.pkt"):
    print file
    p=PKT(file)
#    for m in p.msg:
#      m.add_seenby("5020/9999")
#      m.add_path("5020/9999")

#    p.save(file+"_")
    #i=0
    #print len(p.msg)
    #while i<len(p.msg):
    #  msg=`p.msg[i]`
    #  if( len(msg)>50000 ):
    #    open("%04d.msg"%j,"wb").write(msg)
    #    del p.msg[i]
    #    j+=1
    #  else:
    #    i+=1
    #print len(p.msg)
    #p.save(file)
