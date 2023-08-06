from django.conf import settings
import os
import sys
import threading
import subprocess
import log
'''
a wrapper for creating and blasting a blast database
'''




def makeNewDB(inputFile, seqtype, out):
    '''
    Makes new blast database
    Returns retcode 
    '''
    if seqtype == 'protein':
        st = 'T'
    else:
        st = 'F'

    command = '%s -i "%s" -p %s -n "%s" ' %(settings.FORMATDB, inputFile, st, out )
#    command = 'formatdb -i "/var/www/html/tagbase/blast/6blastdb" -p T -n "/var/www/html/tagbase/blast/6"'
#    command = 'blastcl3'
#    results = os.popen(command).readlines()
#    log.debug('res=%s' %repr(results))
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout_value, stderr_error = proc.communicate()
        retcode = proc.returncode
        log.debug('stderr_error: %s' %stderr_error)
        
        if retcode < 0:
            log.debug("Child was terminated by signal: %s" %retcode)   #unix only
        else:
            log.debug("Child returned: %s" %retcode)
            return retcode
    except Exception, e:
        log.debug('Exception in blast: %s' %(str(e)))

def runShellCmd(command, seq):    
    try:
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,  
	                        stdout=subprocess.PIPE)
        stdout_value, stderr_value = proc.communicate(seq)
        retcode = proc.returncode
        log.debug('stderr: %s' %stderr_value)
                     
        if retcode < 0:
            log.debug("Child was terminated by signal: %s" %retcode)
        else:
            log.debug("Child returned: %s" %retcode)
            print "Child returned %s", retcode
            return retcode, stdout_value
    except Exception, e:
        log.debug('Exception in blast: %s' %(str(e)))

    
def runBlastAll(db, program, seq):
    command='%s -d "%s" -p %s ' %(settings.BLASTALL, db, program)
    log.debug('command: %s' %command)
    retcode, stdout_value = runShellCmd(command, seq)
    return stdout_value

def runBlastcl3(program, seq):
    command='%s -p %s -d swissprot -v 50 -b 10 \
    -u human[organism] -m 7' %(settings.BLASTCL3, program)
    log.debug('command: %s' %command)
    retcode, stdout_value = runShellCmd(command, seq)
    return retcode, stdout_value
 
def runBlastcl3CDD(seq):
    command =  '%s -p blastp -d cdd ' %(settings.BLASTCL3)
    log.debug('command: %s' %command)
    retcode, stdout_value = runShellCmd(command, seq)
    return retcode, stdout_value

        










    
