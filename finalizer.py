#!/usr/bin/env python26

# bedo @ ira - v0.3 - 2017

# from __future__ import with_statement

import os
import tarfile
import shutil
import time
import sys
import getopt

##### funcz #####

### debug ###

def report(level, msg):
    if(level <= debug_level):
        print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' ['+str(level)+'] - ' + msg

### job ###

def job_file_read(job):
    filepath = get_jobfile(job)    
    report(3, 'job ' + job + ': reading ' + filepath)
    with open(filepath) as f:
        # schedule_name = os.path.basename(f.readline().rstrip())
        schedule_name = os.path.splitext(os.path.basename(filepath))[0]
        tarfile = os.path.join(tar_folder,schedule_name + '.tar')
        
        report(3, 'job ' + job + ': schedule ' + schedule_name)
        
        scan_number = 1;
        old_status = read_status(job)
        report(3, 'job ' + job + ': got saved status '+ str(old_status))
        
        for line in f:
            if(system_is_busy()): 
                report(2, 'system busy. exiting')
                sys.exit(0)
	    if line.startswith((";", "#")):
		continue

            report(3,'job ' + job + ': processing item ' + str(scan_number))
            
            filename = line.rstrip()
            if(scan_number > old_status):
                report(3, 'job ' + job + ': appending ' + filename + ' in ' + tarfile)
                append_file(tarfile, filename)
                
                report(3, 'job ' + job + ': saving status ' + str(scan_number))
                save_status(job, scan_number)
            else:
                report(3, 'job ' + job + ': scan ' + filename + ' already appended')
            scan_number += 1
        job_done(job)        

def get_jobfile(job):
    return os.path.join(job_files_incoming_folder, job)

def job_done(job):
    report(3, 'job ' + job + ': removing job file ' + job)
    shutil.move(get_jobfile(job), job_files_done_folder)
    report(3, 'job ' + job + ': removing status for job '+ job)
    os.remove(get_statusfile(job))
    
def job_check_folder(folder):
    report(3, 'check for jobs in folder ' + folder)
    files = os.listdir(folder)
    for f in files:
        report(3,'found job ' + f)
        job_file_read(f)

### status ###

def get_statusfile(job):
    return os.path.join(job_status_folder, job + '.status')

def save_status(job, status):
    out_file = open(get_statusfile(job),"w")
    out_file.write(str(status))
    out_file.close()

def read_status(job):
    try:
        with open(get_statusfile(job), 'r') as statusfile:
            return int(statusfile.read().replace('\n', ''))
    except IOError:
            return int(0)
            
### pid ###

def check_pid(pid_number):
    try:
        os.kill(pid_number, 0)
    except OSError:
        return False
    else:
        return True
### tar ###

def append_file(tarfilename, item):
# con py<2.7 non fa
#    with tarfile.open(tarfilename, "a") as tar:
#        tar.add(item)
	try:
		tar = tarfile.open(tarfilename, "a")
		tar.add(item, arcname=os.path.basename(item))
		tar.close()
	except:
		report(2, "error opening file " + tarfilename )		

### lock ###

def system_is_busy():
    if os.path.exists(lock_file):
        return 1
    else:
        return 0

####################################

# carica configurazione

try:
    opts, args = getopt.getopt(sys.argv[1:],"c:",["cfg_file="])
except getopt.GetoptError as err:
    print(err)
    print "finalyzer.py -c <config file>"
    sys.exit(2)

found_f = False
for o, a in opts:
    if o == '-c':
        found_f = True
        if os.path.exists(a):
            execfile(a)
        else:
            print "configuration file not existent, exiting..."
            sys.exit(2)                            
if not found_f:
    print "config file was not given..."
    sys.exit(2)

# controlla pid

if os.path.isfile(pid_file):
    running_pid = int(open(pid_file).read())
    if(check_pid(running_pid)):
        report(2, "already running as " + str(running_pid) + " exiting")
        sys.exit()
    else:
        report(1, "file " + pid_file + " exists, but process " + str(running_pid) + " not running. exiting")
        sys.exit()

# start

pid = os.getpid() 
report(1, "starting as " + str(pid))
file(pid_file, 'w').write(str(pid))
try:
    job_check_folder(job_files_incoming_folder)
finally:
    os.unlink(pid_file)
report(1, "done.")
