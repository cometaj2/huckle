import hutils
import config
import huckle

def main():
    hutils.create_folder(config.dot_huckle)
    hutils.create_file(config.dot_huckle_profile)
    hutils.create_file(config.dot_bash_profile)
    
    huckle.cli()
