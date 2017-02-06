import os
import sys

from ConfigParser import SafeConfigParser

version = "0.0.1.dev1"
home = os.path.expanduser("~")
dot_huck = "%s/.huck" % home
url = ""
cliname = ""

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
                if name == "cliname":
                    global cliname
                    cliname = value
            if url == "": sys.exit("No url defined for " + cli + " under " + config_file_path)
            if cliname == "": sys.exit("No cliname defined for " + cli + " under " + config_file_path)
    else:
        sys.exit("No cli configuration " + config_file_path + " available for " + cli) 
