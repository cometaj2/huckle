import os
import sys

from ConfigParser import SafeConfigParser
from StringIO import StringIO

version = "0.1.0.dev1"
dependencies = ["restnavigator==1.0.1"]

home = os.path.expanduser("~")
dot_huck = "%s/.huck" % home
dot_huck_profile = dot_huck + "/huck_profile"
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
    config_file_folder = dot_huck + "/" + cli 
    config_file = config_file_folder + "/config"
    create_folder(config_file_folder)
    
    if not os.path.exists(config_file):
        create_file(config_file)
        init_configuration(cli)

def alias_cli(cli):
    if not is_configured(dot_bash_profile, ". " + dot_huck_profile):
        f = open(dot_bash_profile, "a+")
        f.write("\n")
        f.write("# we load the huck aliases profile\n")
        f.write(". " + dot_huck_profile)
        f.close

    if not is_configured(dot_huck_profile, "alias " + cli + "="):
        g = open(dot_huck_profile, "a+")
        g.write("alias " + cli + "=\"huck cli " + cli + "\"\n")
        g.close

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
    parser.set("default", "url", "")
      
    with open(config_file_path, "w") as config:
        parser.write(config)

def is_configured(file_path, contains):
    if contains in open(file_path).read():
        return True
    else:
        return False
