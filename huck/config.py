import os
import sys

from ConfigParser import SafeConfigParser

home = os.path.expanduser("~")
dot_huck = "%s/.huck" % home
dot_bash_profile = home + "/.bash_profile"
url = ""

def parse_configuration(cli):
    config_file_path = dot_huck + "/" + "cli_" + cli 
    parser = SafeConfigParser()
    parser.read(config_file_path)
    if parser.has_section("default"):
        for section_name in parser.sections():
            for name, value in parser.items("default"):
                if name == "url":
                    global url
                    url = value
            if url == "": sys.exit("No url defined for " + cli + " under " + config_file_path)
    else:
        sys.exit("No cli configuration " + config_file_path + " available for " + cli) 

def alias_cli(cli):
    f = open(dot_bash_profile, "a+")
    f.write("\n")
    f.write("# huck aliases\n")
    f.write("alias " + cli + "=\"huck cli " + cli + "\"")
    f.close
