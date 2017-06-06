#!/usr/bin/env python

job_files_incoming_folder = '/archive/report/'
job_files_done_folder = '/archive/done_report/'
tar_folder = '/archive/tars'

job_status_folder = '/archive/finalizer_status' 
lock_file = '/archive/locks/ScheduleRecording.lck'
pid_file = '/tmp/finalizer.pid'

# 1: errori non gestiti, 2: errori gestiti, 3: info
debug_level = 3

