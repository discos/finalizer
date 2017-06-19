finalizer.py - v0.3 - INAF/IRA


# INSTALLATION

dependencies:

* python >= 2.6


# USAGE

finalizer.py -c *config file*

File *config file* should contain the following variables:

* job_files_incoming_folder = *folder containing jobsfiles to be executed*
* job_files_done_folder = *folder where jobfiles are moved after completion*
* tar_folder = *folder *
* job_status_folder = *folder used to store the jobs state*
* lock_file = *lock file path*
* pid_file = *pid file path*
* debug_level = *debug level (1: critical errors, 2: non-critical errors, 3: debug info)*


# HOW IT WORKS

* read the configuration file
* check if there are other running instances
* check for files named *<schedule_name>.rep* inside folder *job_files_incoming_folder* contaning the following lines:
  * path log
  * path scan1
  * path scan(n)
* for each file, produce inside *tar_folder* a file named *<schedule_name>.tar* containing the specified files
* if a file *lock_file* is present, any operation will be interrupted, the current state is saved and the program exit.
* if the file is correctly produced, the jobfile is moved to *job_files_done_folder*.
