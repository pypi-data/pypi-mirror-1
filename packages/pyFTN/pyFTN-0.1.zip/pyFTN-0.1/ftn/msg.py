#!/usr/bin/python

import struct
from addr import *

attrs=[	"Private",
	"Crash",
	"Recd",
	"Sent",
	"FileAttached",
	"InTransit",
	"Orphan",
	"KillSent",
	"Local",
	"HoldForPickup",
	"unused",
	"FileRequest",
	"ReturnReceiptRequest",
	"IsReturnReceipt",
	"AuditRequest",
	"FileUpdateReq"
      ]

class MSG:
  """ FTN message
  Init methods:
    read_from(file) - read
    write_to(file) - write
  Fields: 
    from - (name,addr)
    to - (name,addr)
    subj
    date
    area - defined if echomail
    kludge - dict
    body
    path
    seenby
    via
  """  
  def __init__(self,file=None):
    if( file != None ):
      f=open(file,"rb")
      h=f.read(190)
      #assert(len(h)==190)
      try:
        fn,tn,subj,date,readcount,tnode,fnode,cost,fnet,tnet,\
          tzone,fzone,tpnt,fpnt,replyto,attr,nextreply \
          = struct.unpack("<36s36s72s20s13H",h)
      except:
        raise "msg - failed to unpack header of " + file
      while len(fn) and (fn[-1]=="\0"): fn=fn[:-1]
      while len(tn) and (tn[-1]=="\0"): tn=tn[:-1]
      while len(subj) and (subj[-1]=="\0"): subj=subj[:-1]
      while len(date) and (date[-1]=="\0"): date=date[:-1]

      tpnt=fpnt=tzone=fzone=0 # these fields garbaged with golded

      self.load((fn,(fzone,fnet,fnode,fpnt)),
                (tn,(tzone,tnet,tnode,tpnt)),
                subj,date,attr,cost,f.read())

      self.readcount=readcount
      self.replyto=replyto
      self.nextreply=nextreply

    else:
      pass

  def load(self,src,dst,subj,date,attr,cost,body):
    while len(body) and (body[-1]=="\0"): body=body[:-1]
    text=body.replace("\r\n","\r").split("\r")
    if len(text) and (text[-1]==''):
      del text[-1]

    self.body = []
    self.kludge = {}
    self.via = []
    self.path = []
    self.seenby = []

    (fname,(fzone,fnet,fnode,fpnt)) = src
    (tname,(tzone,tnet,tnode,tpnt)) = dst

    self.area=None
    if len(text) and (text[0][0:4]=="AREA"):
      #print "echomail"
      self.area=text[0][5:]
      del text[0]

    for l in text:
      if l and l[0]=="\1":
        spc=l.find(" ")
        name = l[1:spc]
        value = l[spc+1:]
        if name.upper()=="FMPT":
	  try: 
            fpnt = int(value)
          except:
	    raise "MSG: bad FMPT "+`value`
        elif name.upper()=="TOPT":
	  try:
            tpnt = int(value)
          except:
	    raise "MSG: bad TOPT "+value
        elif name.upper()=="INTL":
	  try:
            to,frm=value.split(" ")
            tzone,tnet,tnode,xpnt=str2addr(to)
            fzone,fnet,fnode,xpnt=str2addr(frm)
          except:
	    raise "MSG: bad INTL "+value
        elif name.upper()=="VIA" or name.upper()=="FORWARDED":
          self.via+=[(name,value)]
        elif name.upper()=="PATH:":
	  try:
           self.path += map(
            addr2str, addr_expand(filter(bool,value.split(" ")),(None,None,None,None)))
          except:
	    raise "MSG: bad PATH "+value
        else:
          if self.kludge.has_key(name):
            if type(self.kludge[name]) is list:
              self.kludge[name]+=[value]
            else:
              self.kludge[name]=[self.kludge[name], value]
          else:
            self.kludge[name]=value
      else:
        self.body += [l]

    while len(self.body) and (self.body[-1][:8] == "SEEN-BY:"):
      self.seenby += \
        addr_expand(filter(bool,self.body[-1][9:].split(" ")),(None,None,None,None))
      del self.body[-1]

    self.orig=(fname, (fzone,fnet,fnode,fpnt))
    self.dest=(tname, (tzone,tnet,tnode,tpnt))
    self.subj=subj
    self.date=date
    self.attr=attr
    self.cost=cost
    self.readcount=0
    self.replyto=0
    self.nextreply=0

  def make_body(self, invalidate=0):
    if invalidate:
      c="@"
      eol="\n"
    else:
      c="\1"
      eol="\r"
    s=""
    if self.area:
      s+="AREA:"+self.area+eol

    if self.orig[1][0]!=0: # zone
      s+=c+"INTL "+\
        addr2str((self.dest[1][0],self.dest[1][1],self.dest[1][2],None))+" "+\
        addr2str((self.orig[1][0],self.orig[1][1],self.orig[1][2],None))+eol

    if self.orig[1][3]!=0: # fmpt
      s+=c+"FMPT "+str(self.orig[1][3])+eol

    if self.dest[1][3]!=0: # topt
      s+=c+"TOPT "+str(self.dest[1][3])+eol

    for k in self.kludge.keys():
      v=self.kludge[k]
      if type(v) is list:
        for x in v:
          s+=c+"%s %s"%(k,x)+eol
      else:
        s+=c+"%s %s"%(k,v)+eol
    if invalidate:
      s+=(eol+eol.join(self.body)+eol).replace("\n---","\n-+-").replace("\n * Origin","\n + Origin")
    else:
      s+=eol+eol.join(self.body)+eol
    s+="".join(map(lambda x: "@%s %s"%x+eol,self.via))

    self.seenby.sort()
    if invalidate:
      s+=addr_makelist(map(addr2str,self.seenby),"SEEN+BY:",eol)
    else:
      s+=addr_makelist(map(addr2str,self.seenby),"SEEN-BY:",eol)

    s+=addr_makelist(self.path,c+"PATH:",eol)
    return s

  def __str__(self):
    s = (
      "From: %s, %s\n"%(self.orig[0],addr2str(self.orig[1])) +
      "To  : %s, %s\n"%(self.dest[0],addr2str(self.dest[1])) +
      "Subj: %s\n"%self.subj +
      "Date: %s\n"%self.date +
      "Attr: %d reads %s\n"%(self.readcount,
        " ".join(map(lambda x: x[1], filter(lambda x: self.attr&(1<<x[0]),
				            zip(range(16),attrs))))
      ) + "\n" +
      self.make_body(invalidate=1)
    )
    return s

  def __repr__(self):
    faddr=self.orig[1]
    taddr=self.dest[1]
    return struct.pack("<36s36s72s20s13H",self.orig[0],self.dest[0],self.subj,
      self.date, self.readcount, taddr[2], faddr[2], self.cost, faddr[1],
      taddr[1], taddr[0], faddr[0] ,taddr[3], faddr[3], self.replyto, 
      self.attr, self.nextreply)+self.make_body()

  def add_seenby(self, a):
    self.seenby+=[str2addr(a)]

  def add_path(self, a):
    self.path+=[addr2str(str2addr(a))]

if __name__ == "__main__":
  x=MSG("1.msg")
  open("x.msg","wb").write(`x`)
  print x
