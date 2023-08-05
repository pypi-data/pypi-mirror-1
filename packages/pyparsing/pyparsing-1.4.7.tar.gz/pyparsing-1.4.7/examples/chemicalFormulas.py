# chemicalFormulas.py
#
# Copyright (c) 2003, Paul McGuire
#

from pyparsing import Word, Optional, OneOrMore, Group, ParseException

atomicWeight = {
    "O"  : 15.9994,
    "H"  : 1.00794,
    "Na" : 22.9897,
    "Cl" : 35.4527,
    "C"  : 12.0107
    }
    
def test( bnf, strg, fn=None ):
    try:
        print strg,"->", bnf.parseString( strg ),
    except ParseException, pe:
        print pe
    else:
        if fn != None:
            print fn( bnf.parseString( strg ) )
        else:
            print
    
caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowers = caps.lower()
digits = "0123456789"

# Version 1
element = Word( caps, lowers )
elementRef = Group( element + Optional( Word( digits ), default="1" ) )
formula = OneOrMore( elementRef )

fn = lambda elemList : sum( [ atomicWeight[elem]*int(qty) for elem,qty in elemList ] )
test( formula, "H2O", fn )
test( formula, "C6H5OH", fn )
test( formula, "NaCl", fn )
print

# Version 2 - access parsed items by field name
element = Word( caps, lowers )
elementRef = Group( element.setResultsName("symbol") + \
                Optional( Word( digits ), default="1" ).setResultsName("qty") )
formula = OneOrMore( elementRef )

fn = lambda elemList : sum( [ atomicWeight[elem.symbol]*int(elem.qty) for elem in elemList ] )
test( formula, "H2O", fn )
test( formula, "C6H5OH", fn )
test( formula, "NaCl", fn )
print

# Version 3 - convert integers during parsing process
element = Word( caps, lowers )
integer = Word( digits ).setParseAction(lambda t:int(t[0]))
elementRef = Group( element.setResultsName("symbol") + \
                Optional( integer, default=1 ).setResultsName("qty") )
formula = OneOrMore( elementRef )

fn = lambda elemList : sum( [ atomicWeight[elem.symbol]*elem.qty for elem in elemList ] )
test( formula, "H2O", fn )
test( formula, "C6H5OH", fn )
test( formula, "NaCl", fn )
    


