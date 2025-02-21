import configparser
from cryptography.fernet import Fernet


def get_decrypted_secret_key(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    encrypted_data = config['encryption']['encrypted_data'].encode()
    encryption_key = config['encryption']['encryption_key'].encode()
    def get_decrypted_secret_version_v1(encrypted_data, encryption_key):
        cipher_suite = Fernet(encryption_key)
        decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
        return decrypted_data
    secret_key = get_decrypted_secret_version_v1(encrypted_data, encryption_key)
    return secret_key

if __name__ == "__main__":
    pass
