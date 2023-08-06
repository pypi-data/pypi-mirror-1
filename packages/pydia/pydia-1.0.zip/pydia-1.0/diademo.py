# Simple DIA application that searches a symbol in a PDB file.
import sys,dia,uuid

if len(sys.argv) != 3:
    print "Usage: diatest.py <pdbfile> <symbol>"

symtag2name = {}
for n in dir(dia):
    if n.startswith("Sym"):
        symtag2name[getattr(dia,n)] = n

ds = dia.DataSource()
ds.loadDataFromPdb(sys.argv[1].decode("mbcs"))
session = ds.openSession()
globals = session.globalScope

syms = globals.findChildren(dia.SymTagNull, sys.argv[2].decode("mbcs"), dia.nsNone)
try:
    syms = syms.Next(1)
except ValueError:
    print "Symbol",sys.argv[2],"not found in PDB."
else:
    try:
        print "Symbol",sys.argv[2],"found in PDB.", symtag2name[syms[0].symTag]
    except ValueError, e:
        print e, ds.lastError
    
