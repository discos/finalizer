#!/usr/bin/env python

job_files_incoming_folder = '/archive/report/'
job_files_done_folder = '/archive/report.old/'
tar_folder = '/locallustre/finalized_data'

job_status_folder = '/home/manager/.finalizer/finalizer_status' 
lock_file = '/archive/locks/ScheduleRecording.lck'
pid_file = '/home/manager/.finalizer/finalizer.pid'

# 1: errori non gestiti, 2: errori gestiti, 3: info
debug_level = 3

