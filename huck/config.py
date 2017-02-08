import os
import sys

from ConfigParser import SafeConfigParser
from StringIO import StringIO

home = os.path.expanduser("~")
dot_huck = "%s/.huck" % home
dot_bash_profile = home + "/.bash_profile"
url = ""
cliname = ""

def parse_configuration(cli):
    config_file_path = dot_huck + "/" + cli + "/config"
    parser = SafeConfigParser()
    parser.read(config_file_path)
    if parser.has_section("default"):
        for section_name in parser.sections():
            for name, value in parser.items("default"):
                if name == "url":
                    global url
                    url = value
                    global cliname
                    cliname = cli
            if url == "": sys.exit("No url defined for " + cli + " under " + config_file_path)
    else:
        sys.exit("No cli configuration " + config_file_path + " available for " + cli) 

def create_configuration(cli):
    config_file_path = dot_huck + "/" + cli 
    create_folder(config_file_path)
    create_file(config_file_path + "/config")
    init_configuration(cli)

def alias_cli(cli):
    f = open(dot_bash_profile, "a+")
    f.write("\n")
    f.write("# huck aliases\n")
    f.write("alias " + cli + "=\"huck cli " + cli + "\"")
    f.close

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_file(path):
    if not os.path.exists(path):
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        try:
            file_handle = os.open(path, flags, 0o0600)
        except OSError as e:
            if e.errno == errno.EEXIST:  # Failed as the file already exists.
                pass
            else:
                raise
        else:
            with os.fdopen(file_handle, 'w') as file_obj:
                file_obj.write("")
                file_obj.close        

def init_configuration(cli):
    config_file_path = dot_huck + "/" + cli + "/config"
    parser = SafeConfigParser()
    parser.readfp(StringIO("[default]"))
    parser.set("default", "url", " ")
      
    with open(config_file_path, "w") as config:
        parser.write(config)
