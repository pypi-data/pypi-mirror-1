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

att=[	"Pvt",
	"Cra",
	"Rcd",
	"Snt",
	"Att",
	"Trs",
	"Orp",
	"K/S",
	"Loc",
	"HFP",
	"unused",
	"FRq",
	"RRq",
	"IRc",
	"ARq",
	"URq"
      ]

def decode(a):
  res=0
  a=a.capitalize()
  for i in xrange(16):
    if a.count(att[i].capitalize()):
      res+=1<<i
  return res
