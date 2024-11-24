import sys
import os
from configparser import ConfigParser
from contextlib import suppress

from huckle import logger
from huckle import config

log = logger.Logger()


class CredentialManager:
    def __init__(self):
        self._credentials = None
        self.credentials_file_path = config.credentials_file_path

    @property
    def credentials(self):
        return self._credentials

    def parse_credentials(self):
        try:
            with open(self.credentials_file_path, 'r') as cred_file:
                parser = ConfigParser(interpolation=None)
                log.debug("Loading credentials")
                log.debug(self.credentials_file_path)
                parser.read_file(cred_file)

                # Check for unique usernames across all sections
                usernames = set()
                for section in parser.sections():
                    if parser.has_option(section, "username"):
                        username = parser.get(section, "username")
                        if username in usernames:
                            error = f"duplicate username '{username}' found in {self.credentials_file_path}."
                            self._credentials = None
                            raise Exception(error)
                        usernames.add(username)

                new_credentials = {}
                for section_name in parser.sections():
                    new_credentials[str(section_name)] = []
                    for name, value in parser.items(section_name):
                        new_credentials[str(section_name)].append({str(name): str(value)})

                self._credentials = new_credentials
                return

        except Exception as e:
            error = f"huckle: unable to load credentials: {str(e)}"
            self._credentials = None
            raise Exception(error)

    def hcoak_find(self):
        try:
            self.parse_credentials()

            if not self._credentials:
                return None

            for section, cred_list in self._credentials.items():
                if section == config.auth_apikey_profile:
                    section_keyid = None
                    section_apikey = None
                    for cred in cred_list:
                        if 'keyid' in cred:
                            section_keyid = cred['keyid']
                        if 'apikey' in cred:
                            section_apikey = cred['apikey']

                    if section_keyid is not None and section_apikey is not None:
                        return section_keyid, section_apikey

            error = f"unable to find keyid or apikey credentials for the [{config.auth_apikey_profile}] profile under {self.credentials_file_path}."
            raise Exception(error)

        except Exception as e:
            error = f"huckle: error retrieving credentials: {str(e)}"
            raise Exception(error)

    def find(self):
        try:
            self.parse_credentials()

            if not self._credentials:
                return None

            for section, cred_list in self._credentials.items():
                if section == config.auth_user_profile:
                    section_username = None
                    section_password = None
                    for cred in cred_list:
                        if 'username' in cred:
                            section_username = cred['username']
                        if 'password' in cred:
                            section_password = cred['password']

                    if section_username is not None and section_password is not None:
                        return section_username, section_password

            error = f"unable to find username and password credentials for the [{config.auth_user_profile}] profile under {self.credentials_file_path}."
            raise Exception(error)

        except Exception as e:
            error = f"huckle: error retrieving credentials: {str(e)}"
            raise Exception(error)

    @property
    def is_loaded(self):
        return self._credentials is not None
