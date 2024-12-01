import sys
import os
import keyring

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
            log.debug("keyring backend: " + str(keyring.get_keyring()))

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
                        if config.credential_helper == 'keyring':
                            if name == 'password' or name == 'keyid':
                                pass

                            # For keyring mode, get passwords/apikeys from keyring
                            if name == 'username':
                                new_credentials[str(section_name)].append({str(name): str(value)})
                                password = keyring.get_password(config.url, value)
                                new_credentials[str(section_name)].append({'password': str(password) if password is not None else ''})
                            elif name == 'keyid':
                                new_credentials[str(section_name)].append({str(name): str(value)})
                                apikey = keyring.get_password(config.url, value)
                                new_credentials[str(section_name)].append({'apikey': str(apikey) if apikey is not None else ''})
                        elif config.credential_helper == 'huckle':
                            new_credentials[str(section_name)].append({str(name): str(value)})
                        else:
                            error = f"unknown credential helper configuration: {config.credential_helper}"
                            self._credentials = None
                            raise Exception(error)

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

                    if section_keyid is not None and section_apikey is not None and not section_apikey == '':
                        return section_keyid, section_apikey

                    if section_apikey == '':
                        error = f"the apikey is empty for keyid {section_keyid}. validate expected keyring stored values retrieved for {config.url} and {section_keyid}."
                        raise Exception(error)

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

                    if section_username is not None and section_password is not None and not section_password == '':
                        return section_username, section_password

                    if section_password == '':
                        error = f"the password is empty for username {section_username}. validate expected keyring stored values retrieved for {config.url} and {section_username}."
                        raise Exception(error)

            error = f"unable to find username and password credentials for the [{config.auth_user_profile}] profile under {self.credentials_file_path}."
            raise Exception(error)

        except Exception as e:
            error = f"huckle: error retrieving credentials: {str(e)}"
            raise Exception(error)

    def update_credential(self, key, secret):
        try:
            config.create_file(self.credentials_file_path)
            with config.write_lock(self.credentials_file_path):
                log.debug("updating credentials file.")
                parser = ConfigParser(interpolation=None)
                log.debug(self.credentials_file_path)
                parser.read(self.credentials_file_path)

                is_apikey = secret.startswith('hcoak_')
                id_type = "keyid" if is_apikey else "username"
                value_type = "apikey" if is_apikey else "password"

                # default section created if the credentials file is empty first
                if not parser.sections():
                    # Create default section without number
                    new_section = f"default"
                    parser.add_section(new_section)
                    parser.set(new_section, id_type, key)
                    if config.credential_helper == 'keyring':
                        keyring.set_password(config.url, key, secret)
                    elif config.credential_helper == 'huckle':
                        parser.set(new_section, value_type, secret)
                else:
                    # Find existing credential and track highest section number
                    found_section = None
                    highest_num = 0
                    base_section = f"{id_type}_profile"

                    for section in parser.sections():
                        # Check if this is the credential we're updating
                        if parser.has_option(section, id_type) and parser.get(section, id_type) == key:
                            found_section = section

                        # Track highest section number
                        if section.startswith(base_section):
                            try:
                                section_num = int(section[len(base_section):] or 0)
                                highest_num = max(highest_num, section_num)
                            except ValueError:
                                continue

                    if found_section:
                        # Update existing credential
                        if config.credential_helper == 'keyring':
                            keyring.set_password(config.url, key, secret)
                        elif config.credential_helper == 'huckle':
                            parser.set(found_section, value_type, secret)
                    else:
                        # Create new section with next number
                        new_section = f"{base_section}{highest_num + 1}"
                        parser.add_section(new_section)
                        parser.set(new_section, id_type, key)

                        if config.credential_helper == 'keyring':
                            keyring.set_password(config.url, key, secret)
                        elif config.credential_helper == 'huckle':
                            parser.set(new_section, value_type, secret)

                with open(self.credentials_file_path, 'w') as configfile:
                    parser.write(configfile)
        except Exception as e:
            error = f"huckle: unable to set credentials: {str(e)}"
            raise Exception(error)

    @property
    def is_loaded(self):
        return self._credentials is not None
