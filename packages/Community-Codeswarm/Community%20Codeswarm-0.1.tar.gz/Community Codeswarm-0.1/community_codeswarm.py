#!/usr/bin/Env python
# encoding: utf-8

"""Community Codeswarm - create a shared codeswarm for multiple projects."""

__copyright__ = """
Copyright © 2008 Arne Babenhauserheide

License: GPLv3
"""

# yaml for parsing the config file - somehow overkill, but very easy to use.
from yaml import load
# Changing directories, cause I don't want to join paths. 
from os import chdir, curdir
from os.path import abspath, join, dirname
# Also mkdir and isdir
from os import mkdir
from os.path import isdir, isfile
# string utilities for escaping stuff which breaks things. 
from string import replace
# For timestamping some timestamps - I like it to know when sites where last changed :) 
from time import strftime
# Calling the shell
from subprocess import call
from sys import argv

### Constants ###

CONFIG_FILE = "simple.config"
INCOMING_REPO_DIR = "incoming"
PROCESSED_REPO_DIR = "processed"
#: The config file for codeswarm. 
CONFIG_FOR_CODESWARM = "codeswarm-shared.config"
SCRIPT_DIR = dirname(__file__)

### Commandline parsing ###

def help(): 
    return """Usage: 
    """ + argv[0] + ' --codeswarm-path "<absolute path to the codeswarm dir>"' + """

    This always uses the folder in which the script is evoked 
    and needs a 'simple.config' file. 
    If available, it takes a 'codeswarm-shared.config' as config file for code_swarm, 
    else it uses the default code_swarm config. 
    
    Please read http://rakjar.de/shared_codeswarm/readme.html 
    for additional requirements. """

if len(argv) < 3: 
    print help()
    exit()
elif argv[1] != "--codeswarm-path": 
    print help()
    exit()

#: The folder in which the codeswarm run.sh lies  TOPDO: use as commandline argument. 
CODESWARM_PROJECT_DIR = argv[2]


### The code :) ###

## Step 1: Create a shared log. 

# First load the config. 

def load_config(): 
    """Load the config file. 
@return: A dict with repo names and update commands.
"""
    f = open(CONFIG_FILE, "r")
    data = f.read()
    f.close()
    return load(data)

simple_config = load_config()

# Then create the dirs. 
for i in [INCOMING_REPO_DIR, PROCESSED_REPO_DIR]: 
    if not isdir(i): 
	mkdir(i)

# Now change into the incoming dir and call all commands. 
#: The (absolute) current directory path, so we can change back later on. 
current_dir = abspath(curdir)
chdir(INCOMING_REPO_DIR)
for i in simple_config.values(): 
    print i
    call(i, shell=True)

# Now change back into the main dir and check incoming for all repoisitories. 
chdir(current_dir)
# First empty shared.log
call("rm shared.log", shell=True)

for repo in simple_config: 
    incoming_path = join(INCOMING_REPO_DIR, repo)
    target_path = join(PROCESSED_REPO_DIR, repo)
    # The log goeds into a temporary file first. We need more that simple sed. 
    # If there's already a repository, we do an incoming check. 
    if isdir(target_path): 
	call("hg incoming --style=code_swarm -q -R " + target_path + " " + incoming_path + " > tmp.log", shell=True)
	# now we pull it. 
	call("hg pull -R " + target_path + " " + incoming_path, shell=True)
    # Else we get the log from the incoming repository and then clone it. 
    else: 
	call("hg log --style=code_swarm -q -R " + incoming_path + " > tmp.log", shell=True)
	call("hg clone " + incoming_path + " " + target_path, shell=True)

    # Now convert the code_swarm styled temp file. 
    # First get it
    f = open("tmp.log", "r")
    temp = f.read()
    f.close()
    
    # Now split it. 
    tmp_lines = temp.splitlines()
    
    # Now create a new nested list with all entries as lists. 
    tmp_nested = [[]] # the last element gets updated if there is no empty line. 
    for line in tmp_lines: 
	if line: # the line isn't empty, so we add the line to the inner list. . 
	    # if the list contains a '"', we replace it with a '. 
	    if '"' in line: 
		line = replace(line, '"', "'")
	    tmp_nested[-1].append(line)
	else: # If the line is empty, we add a new sublist. 
	    tmp_nested.append([])
    
    # Now we need to change all files for the entries entries to begin with the repository name as path - we keep the authors, as they might be active across different projects. 
    for entry in tmp_nested: 
	# Only change the files. 
	for i in range(len(entry[2:])): 
	    entry[i+2] = join(repo, entry[i+2])

    # After this we need to unnest the list. 
    temp_lines = []
    for entry in tmp_nested: 
	# Append all lines in the entry. 
	for line in entry: 
	    temp_lines.append(line)
	# Also append an empty line as entry seperator. 
	temp_lines.append("")

    # Now we append to the log file. 
    f = open("shared.log", "a")
    f.writelines([line + "\n" for line in temp_lines[:-1]]) # with newlines, without the last one. 
    f.close()
    
    # Done - we have a shared log. 

## Step 2: Turn the log into a codeswarm

# First if the log contains anything. If it doesn't, we can stop here. 

f = open("shared.log", "r")
data = f.read()
f.close()
print data
if not "".join(data.splitlines()): 
    print "There aren't any new commits on your projects, so we can't create a (meaningful) codeswarm movie right now."
    exit()

# Now convert the shared.log to an activity xml file. 
call("python " + join(SCRIPT_DIR, "convert_logs_hg.py") + " -m shared.log", shell=True)

# We now have a shared activity file. Now the only thing left to do is to put it through the codeswarm software and generate the new video. YAY! 

# First copy it into the codeswarm data folder 
codeswarm_data_dir = join(CODESWARM_PROJECT_DIR, "data")
call("cp shared.xml " + codeswarm_data_dir, shell=True)

# Also add a config. TODO: auto generate a config for the different projects with different colors - maybe with also matching to .*doc.* and .*test.*
call("cp " + join(SCRIPT_DIR, CONFIG_FOR_CODESWARM) + " " + codeswarm_data_dir, shell=True)

# Now change into the codeswarm dir. 
chdir(CODESWARM_PROJECT_DIR)
# and start the codeswarm - If we have an adapted codeswarm config, we use that. 
if isfile(join(current_dir, CONFIG_FOR_CODESWARM)): 
    call("./run.sh" + " " + join(current_dir, CONFIG_FOR_CODESWARM),  shell=True)
else: # we use the one from the shared codeswarm repository. 
    call("./run.sh" + " " + join(SCRIPT_DIR, CONFIG_FOR_CODESWARM),  shell=True)


## Step 3: Create the video - yes, I am lazy :) . 

chdir("frames")
# encode the video to a file containing the time and date - sorry: no iso; I want to avoid using ":" in filenames. 

video_filename = "shared_movie_" + strftime('%Y-%m-%d_%H-%M-%S') + ".avi"

#: The command to encode the video from inside the frames folder. 
ENCODE_VIDEO_COMMAND_WITHOUT_OUTPUT_FILENAME = r"mencoder mf://*.png -mf fps=24:type=png -lavcopts vcodec=mpeg4:vbitrate=12000 -ovc lavc -oac copy -o "

call(ENCODE_VIDEO_COMMAND_WITHOUT_OUTPUT_FILENAME + video_filename, shell=True)

# And remove the individual frames. 
call(r"rm *png", shell=True)

# DONE! 
# The only thing left is to *enjoy your swarm video!*

call("mplayer " + video_filename, shell=True)
