import subprocess
import time

def git_pull():
    subprocess.run(['git', 'pull'])

def open_screen(screen_name):
    subprocess.run(['screen', '-r', screen_name])

def stop_and_start_screen(screen_name, command):
    subprocess.run(['screen', '-r', screen_name, 'stuff', '\003']) 
    time.sleep(5)
    subprocess.run(['stuff', f'{command}\n'])

def start_screen(screen_name, command):
    subprocess.run(['screen', '-r', screen_name, '-X', 'stuff', f'{command}\n'])

if __name__ == "__main__":
    git_pull()
    screen_name = "dev_api"
    # time.sleep(10)
    open_screen(screen_name)
    command = "/home/azureuser/dev_api/icco_venv/bin/gunicorn -c gunicorn_config.py wsgi:app"
    stop_and_start_screen(screen_name, command)