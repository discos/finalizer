#!/usr/bin/env python

# bedo @ ira - v0.5 - 2019

# from __future__ import with_statement

import os
import tarfile
import shutil
import time
import sys
import getopt
import ConfigParser
import re

##### funcz #####

### logging ###

def report(level, msg):
    if(level <= config.get('finalizer', 'debug_level')):
        logline = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' ['+str(level)+'] - ' + msg + '\n'
        with open(config.get('finalizer', 'log_file'), "a") as logfile:
                logfile.write(logline)
 
### job ###

def job_file_read(job):
    jobfile_path = get_jobfile(job)
    report(3, 'job ' + job + ': reading ' + jobfile_path)
    with open(jobfile_path) as schedule_lines:
        schedule_name = os.path.splitext(os.path.basename(jobfile_path))[0]

        report(3, 'job ' + job + ': schedule ' + schedule_name)
        
        subscan_number = 1;
        old_status = read_status(job)
        report(3, 'job ' + job + ': got saved status '+ str(old_status))

	schedule_tarfile = os.path.join(config.get('finalizer', 'schedule_tar_folder'), schedule_name + '.tar')
	report(3, 'job ' + job + ': schedule_tarfile ' + schedule_tarfile)

	#add schedule
	schedule_path = schedule_lines.readline().rstrip()
	report(3, 'job ' + job + ': appending schedule_path ' + schedule_path + ' in ' + schedule_tarfile)
	append_file(schedule_tarfile, schedule_path)

	#add log
	log_path = schedule_lines.readline().rstrip()
	report(3, 'job ' + job + ': appending log_path ' + log_path + ' in ' + schedule_tarfile)
	append_file(schedule_tarfile, log_path)

        for schedule_line in schedule_lines:
            if(system_is_busy()): 
                report(2, 'system busy. exiting')
                sys.exit(0)
	    if schedule_line.startswith((";", "#")):
		continue
            if not is_parent(os.path.basename(schedule_line)):
		report(2, os.path.basename(schedule_line) + ' parent dir workaround, continue')
                continue

            report(3,'job ' + job + ': processing item ' + str(subscan_number))

            scan_dirname = schedule_line.rstrip()
	    scan_name = os.path.basename(scan_dirname);
            if os.path.exists(scan_dirname):
            	scan_tarfile = os.path.join(config.get('finalizer', 'tar_folder'), scan_name + '.tar')
		subscan_files = os.listdir(scan_dirname)
		for subscan_file in subscan_files:
			if(system_is_busy()): 
	                	report(2, 'system busy. exiting')
				sys.exit(0)
			if(subscan_number > old_status):
		    		print(subscan_file)
                        	report(3, 'job ' + job + ': appending ' + scan_dirname + '/' + subscan_file + ' in ' + scan_tarfile)
                        	append_file(scan_tarfile, scan_dirname + '/' + subscan_file)
                        	report(3, 'job ' + job + ': saving status ' + str(subscan_number))
                    		save_status(job, subscan_number)
			else:
                		report(3, 'job ' + job + ': subscan ' + subscan_file + ' already appended in ' + scan_tarfile)
            		subscan_number += 1
	    else:
            	report(2, 'job ' + job + ': item ' + scan_dirname + ' missing')
               	job_failed(job)
                return
        job_done(job)

def get_jobfile(job):
    return os.path.join(config.get('finalizer', 'job_files_incoming_folder'), job)

def job_done(job):
    report(3, 'job ' + job + ': job finished, moving job file ' + job + ' to ' + config.get('finalizer', 'job_files_done_folder'))
    shutil.move(get_jobfile(job), config.get('finalizer', 'job_files_done_folder'))
    remove_statusfile(job);

def job_failed(job):
    report(3, 'job ' + job + ': job failed, moving job file ' + job + ' to ' + config.get('finalizer', 'job_files_failed_folder'))
    shutil.move(get_jobfile(job), config.get('finalizer', 'job_files_failed_folder'))
    remove_statusfile(job);
    
def job_check_folder(folder):
    report(3, 'check for jobs in folder ' + folder)
    try:
        files = os.listdir(folder)
        for f in files:
            report(3,'found job ' + f)
            job_file_read(f)
    except OSError, msg:
        report(1, 'error: ' + str(msg))

def is_parent(path):
    return re.match('^\d{8}\-\d{6}', path)
	
### status ###

def get_statusfile(job):
    return os.path.join(config.get('finalizer', 'job_status_folder'), job + '.status')

def remove_statusfile(job):
    if os.path.exists(get_statusfile(job)):
        report(3, 'job ' + job + ': removing status for job '+ job)
        os.remove(get_statusfile(job))
    else:
        report(3, 'job ' + job + ': no status for job '+ job +' to remove')
    
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
    with tarfile.open(tarfilename, "a") as tar:
        tar.add(item, arcname=os.path.basename(item))
	tar.close()

#	try:
#		tar = tarfile.open(tarfilename, "a")
#		tar.add(item, arcname=os.path.basename(item))
#		tar.close()
#	except:
#		report(2, "error opening file " + tarfilename + ", exiting")
#               sys.exit(0)

### lock ###

def system_is_busy():
    if os.path.exists(config.get('finalizer', 'lock_file')):
        return 1
    else:
        return 0

###



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
#           execfile(a)
            config = ConfigParser.ConfigParser()
            config.read(a)
        else:
            print "configuration file not existent, exiting..."
            sys.exit(2)                            
if not found_f:
    print "config file was not given..."
    sys.exit(2)

# controlla pid

if os.path.isfile(config.get('finalizer', 'pid_file')):
    running_pid = int(open(config.get('finalizer', 'pid_file')).read())
    if(check_pid(running_pid)):
        report(2, "already running as " + str(running_pid) + " exiting")
        sys.exit()
    else:
        report(1, "file " + config.get('finalizer', 'pid_file') + " exists, but process " + str(running_pid) + " not running. exiting")
        sys.exit()

# start

pid = os.getpid() 
report(1, "starting as " + str(pid))
file(config.get('finalizer', 'pid_file'), 'w').write(str(pid))
try:
    job_check_folder(config.get('finalizer', 'job_files_incoming_folder'))
finally:
    os.unlink(config.get('finalizer', 'pid_file'))
report(1, "done.")
