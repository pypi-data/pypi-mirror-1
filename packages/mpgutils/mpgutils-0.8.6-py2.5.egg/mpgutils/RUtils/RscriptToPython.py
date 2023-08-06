#!/util/bin/python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage: %prog [options] <input file>

Load an R library, and pass in options from the command line to that library

This is an adapter that should be used by python clients to R code.

"""

import sys
import optparse
import mpgutils.utils
import os
import subprocess

def callRscript (lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True):
    strCall=generateCall(lstLibraries, methodName, dctArguments)
    if (bVerbose): print ("Calling:  " + strCall)
    #os.system(strCall)
    if (captureOutput):
        output=subprocess.Popen(strCall, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0] 
        return (output)
    else:
        subprocess.Popen(strCall, shell=True).wait()
    
    
def generateCall (lstLibraries, methodName, dctArguments):
    
    strCommand="Rscript"
    
    
    #add library calls
    for library in lstLibraries:
        libCommand="-e 'library(" + library + ")'"
        strCommand=strCommand + " " +libCommand
     
    #encode method
    methodCommand="-e '" + methodName +"("
    
    argNames=dctArguments.keys()
    argValues=dctArguments.values()
    
    for i in range(len(argNames)):        
        methodCommand=methodCommand + argNames[i] + "="
        value=encodeValue(argValues[i])
        methodCommand=methodCommand+value
        if i != (len(argNames)-1):
            methodCommand=methodCommand+","
    methodCommand=methodCommand+")'" #finish method call
    
    strCommand=strCommand+" " +methodCommand
    return (strCommand)
    
def encodeValue (value):
    if value==None: return ("NULL")
    if isinstance (value, bool):
        if (value==True): return ("T")
        if (value==False): return ("F")
    
    if isinstance(value, int):
        return str(value)
    
    if isinstance(value, float):
        return str(value)

    if isinstance(value, str):
        return "\""+value+"\"" #encode as a string
        
    #for any type not yet specificed here...
    return value
 
        
