#!/usr/bin/Env python
# -*- coding: utf-8 -*-

"""Community Codeswarm - create a shared codeswarm for multiple projects."""

__copyright__ = """
Copyright © 2008 Arne Babenhauserheide

License: GPLv3
"""

# TODO: Ignore changesets with the same ID. 


# yaml for parsing the config file - somehow overkill, but very easy to use.
from yaml import load
# Changing directories, cause I don't want to join paths. 
from os import chdir, curdir
from os.path import abspath, join, dirname
# Also mkdir and isdir
from os import mkdir, mknod
from os.path import isdir, isfile
# List directory contents for selecting files
from os import listdir
# Select a random file from a list
from random import choice
# string utilities for escaping stuff which breaks things. 
from string import replace
# For timestamping some timestamps - I like it to know when sites where last changed :) 
from time import strftime
# Calling the shell
from subprocess import call
from sys import argv
# Mercurial for using PyMarkdownMinisite - committing the change to the website file and pushing the data. 
from mercurial import dispatch
# also we need the color range for choosing colors automatically. 
from color_range import get_color_string

### Constants ###

CONFIG_FILE = "simple.config"
INCOMING_REPO_DIR = "incoming"
PROCESSED_REPO_DIR = "processed"
#: The config file for codeswarm. 
CONFIG_FOR_CODESWARM = "codeswarm-shared.config"
SCRIPT_DIR = dirname(__file__)
#: The filename of the file to use for the automatic website creation. 
MARKDOWN_FILE = "index.mdwn" # TODO: allow pasing the target file via the commandline.

### Commandline parsing ###

def help(): 
    return """Usage: 
    """ + argv[0] + ' --codeswarm-path "<absolute path to the codeswarm dir>"' + """

    This always uses the folder in which the script is evoked 
    and needs a 'simple.config' file. 
    If available, it takes a 'codeswarm-shared.config' as config file for code_swarm, 
    else it uses the default code_swarm config. 

    For it to work, you need pyyaml, Mercurial with code_swarm style 
    and naturally code_swarm installed
    
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
    print "\n" + str(i)
    call(i, shell=True)

# Now change back into the main dir and check incoming for all repoisitories. 
chdir(current_dir)
# First empty shared.log
call("rm shared.log", shell=True)

# Now init a list of known node IDs, so we never count any changeset twice. 
known_nodes = []

for repo in simple_config: 
    incoming_path = join(INCOMING_REPO_DIR, repo)
    target_path = join(PROCESSED_REPO_DIR, repo)
    # The log goeds into a temporary file first. We need more that simple sed. 
    # If there's already a repository, we do an incoming check. 
    if isdir(target_path): 
	call("hg incoming --style=code_swarm_ext -q -R " + target_path + " " + incoming_path + " > tmp.log", shell=True)
	# now we pull it. 
	call("hg pull -R " + target_path + " " + incoming_path, shell=True)
    # Else we get the log from the incoming repository and then clone it. 
    else: 
	call("hg log --style=code_swarm_ext -q -R " + incoming_path + " > tmp.log", shell=True)
	call("hg clone -U " + incoming_path + " " + target_path, shell=True)

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
    
    # Now we need to change all files for the entries entries to begin with the repository name as path - we keep the node IDs (which are unique) and the authors, as they might be active across different projects, as well as the date. 
    for entry in tmp_nested:
	# Only change the files. 
	for i in range(len(entry[3:])): 
	    entry[i+3] = join(repo, entry[i+3])

    # After this we need to unnest the list
    # and make sure we only add each changeset once. 
    temp_lines = []
    for entry in tmp_nested: 
        # If the node has already been added, ignore this changeset. 
        if entry and entry[0] in known_nodes: 
            continue
        elif entry: 
            known_nodes.append(entry[0])
	# Append all lines after the first (the node ID) in the entry. 
	for i in range(len(entry)-1): 
	    temp_lines.append(entry[i+1])
	# Also append an empty line as entry seperator. 
	temp_lines.append("")

    # Now we append to the log file. 
    f = open("shared.log", "a")
    f.writelines([line + "\n" for line in temp_lines[:-1]]) # with newlines, without the last one. 
    f.close()
    
    # Done - we have a shared log. 

# We can now safely delete the known_nodes list, since we don't need it anymore. 
del known_nodes

## Step 2: Turn the log into a codeswarm

# Only go on if the log contains something. If it doesn't, we can stop here. 

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

# Also add a config. 
call("cp " + join(SCRIPT_DIR, CONFIG_FOR_CODESWARM) + " " + codeswarm_data_dir, shell=True)

# Now change into the codeswarm dir. 
chdir(CODESWARM_PROJECT_DIR)
# and start the codeswarm - If we have an adapted codeswarm config, we use that. 
if isfile(join(current_dir, CONFIG_FOR_CODESWARM)): 
    call("./run.sh" + " " + join(current_dir, CONFIG_FOR_CODESWARM),  shell=True)
else: # we use the one from the shared codeswarm repository and add a color string. 
    # for this we copy the config and add custom color lines
    conf = CONFIG_FOR_CODESWARM + "_tmp"
    call("cat " + join(SCRIPT_DIR, CONFIG_FOR_CODESWARM) + " > " + join(SCRIPT_DIR, conf), shell=True)
    color_lines = get_color_string(simple_config.keys())
    call("echo '\n" + color_lines + "' >> " + join(SCRIPT_DIR, conf), shell=True)
    call("./run.sh" + " " + join(SCRIPT_DIR, conf),  shell=True)


## Step 3: Create the video - yes, I am lazy :) . 

chdir(join(CODESWARM_PROJECT_DIR, "frames"))
# encode the video to a file containing the time and date - sorry: no iso; I want to avoid using ":" in filenames. 

video_filename = "shared_movie_" + strftime('%Y-%m-%d_%H-%M-%S') + ".avi"

#: The command to encode the video from inside the frames folder. 
ENCODE_VIDEO_COMMAND_WITHOUT_OUTPUT_FILENAME = r"mencoder mf://*.png -mf fps=24:type=png -lavcopts vcodec=mpeg4:vbitrate=2400000 -ovc lavc -oac copy -o "

call(ENCODE_VIDEO_COMMAND_WITHOUT_OUTPUT_FILENAME + video_filename, shell=True)

# DONE! 
# The only thing left is to *enjoy your swarm video!*

call("mplayer " + video_filename, shell=True)

# At this point we can use pyMarkdownMinisite to create a website with all videos. 

# Prepare a static folder for pyMM
static_dir = join(current_dir, "static")
if not isdir(static_dir): 
    mkdir(static_dir)

# To move the video into the dir. 
call(["mv",video_filename,static_dir])

# Select a random snapshot as screenshot for the video. 
screenshot = choice(listdir("."))
while not screenshot.endswith("png"): 
   screenshot = choice(listdir("."))

# Copy the screenshot into the current dir. 
call(["cp",screenshot,static_dir])

# And to remove the individual frames.
call(r"rm *png", shell=True)

# Now change back into the dir the script was started in. 
chdir(current_dir)

# And check if we have an index file. 
# If we have no index file, we create one
if not isfile(MARKDOWN_FILE): 
    mknod(MARKDOWN_FILE)

# First get the current file
f = open(MARKDOWN_FILE, "r")
data = f.read()
f.close()

# Now append a new section with the date and the video at the top. 
data += "\n\n---\n\ncode_swarm " + strftime('%Y-%m-%d_%H-%M-%S') + "\n------\n\n" + "[![code_swarm]" + "(" + screenshot + ")](" + video_filename + ")"

# TODO: Split the file into an intro part and show the code_swarms in reversed order.

# and save the data to the file
f = open(MARKDOWN_FILE, "w")
f.write(data)
f.close()


# Now , if this is a Mercurial repository, commit the changes and push them. If this repo has an outgoing pyMM hook, it will parse and upload itself with the push. 
# commit using mercurials dispatch function
try: 
    # add
    dispatch.dispatch(["add", MARKDOWN_FILE])
    # commit
    commit_string = 'ci -m "' + video_filename + '" ' + MARKDOWN_FILE
    dispatch.dispatch(commit_string.split())
    # and push
    dispatch.dispatch(["push"])
except: 
    print "This is no Mercurial repository, or we can't push."
