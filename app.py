import os
import subprocess

# Function to create a user and configure it
def create_user(username, password):
    try:
        print("Creating User and Setting it up")
        
        # Create the user
        subprocess.run(["sudo", "useradd", "-m", username], check=True, stdout=subprocess.DEVNULL)
        
        # Add the user to the sudo group
        subprocess.run(["sudo", "adduser", username, "sudo"], check=True, stdout=subprocess.DEVNULL)
        
        # Set the user's password
        subprocess.run(f"echo '{username}:{password}' | sudo chpasswd", shell=True, check=True)
        
        # Change the default shell to bash
        subprocess.run(["sudo", "sed", "-i", "s|/bin/sh|/bin/bash|g", "/etc/passwd"], check=True)
        
        print("User Created and Configured Successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error during user creation: {e}")

# Function to install and set up Chrome Remote Desktop
def setup_crd(username, crp_command, pin):
    try:
        print("Setting up Chrome Remote Desktop. This may take a few minutes...")

        # Create the installation script
        with open('install.sh', 'w') as script:
            script.write("""#! /bin/bash

b='\033[1m'
r='\E[31m'
g='\E[32m'
c='\E[36m'
endc='\E[0m'
enda='\033[0m'

printf "\n\n$c$b    Loading Installer $endc$enda" >&2
if sudo apt-get update &> /dev/null
then
    printf "\r$g$b    Installer Loaded $endc$enda\n" >&2
else
    printf "\r$r$b    Error Occurred $endc$enda\n" >&2
    exit
fi

printf "\n$g$b    Installing Chrome Remote Desktop $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
    sudo dpkg --install chrome-remote-desktop_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\r$c$b    Chrome Remote Desktop Installed $endc$enda\n" >&2 ||
{ printf "\r$r$b    Error Occurred $endc$enda\n" >&2; exit; }
sleep 3

printf "$g$b    Installing Desktop Environment $endc$enda" >&2
{
    sudo DEBIAN_FRONTEND=noninteractive \
        apt install --assume-yes xfce4 desktop-base xfce4-terminal
    sudo bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'
    sudo apt remove --assume-yes gnome-terminal
    sudo apt install --assume-yes xscreensaver
    sudo systemctl disable lightdm.service
} &> /dev/null &&
printf "\r$c$b    Desktop Environment Installed $endc$enda\n" >&2 ||
{ printf "\r$r$b    Error Occurred $endc$enda\n" >&2; exit; }
sleep 3

printf "$g$b    Installing Google Chrome $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg --install google-chrome-stable_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\r$c$b    Google Chrome Installed $endc$enda\n" >&2 ||
printf "\r$r$b    Error Occurred $endc$enda\n" >&2
sleep 3

printf "$g$b    Installing other Tools $endc$enda" >&2
if sudo apt install nautilus nano -y &> /dev/null
then
    printf "\r$c$b    Other Tools Installed $endc$enda\n" >&2
else
    printf "\r$r$b    Error Occurred $endc$enda\n" >&2
fi
sleep 3

printf "\n$g$b    Installation Completed $endc$enda\n\n" >&2
""")

        # Run the installation script
        os.chmod('install.sh', 0o755)
        subprocess.run(["./install.sh"], check=True)
        
        # Add the user to the Chrome Remote Desktop group
        subprocess.run(["sudo", "adduser", username, "chrome-remote-desktop"], check=True, stdout=subprocess.DEVNULL)
        
        # Execute the CRP command with the provided pin
        subprocess.run(f"su - {username} -c \"{crp_command} --pin={pin}\"", shell=True, check=True, stdout=subprocess.DEVNULL)
        
        print("Chrome Remote Desktop Setup Completed Successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error during CRD setup: {e}")

if __name__ == "__main__":
    # User Configuration
    username = "user"  # Enter desired username
    password = "root"  # Enter desired password

    # Chrome Remote Desktop Configuration
    crp_command = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/0AanRRruxUkD2l4b6TDe4kxUXvnxjEh_gz60hA3cBYo6aiF5sg1-BtJF44j9ujMJONhbbTQ\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=$(hostname)"
    pin = 123394  # Enter a pin of 6 or more digits

    # Run the functions
    create_user(username, password)
    if crp_command and len(str(pin)) >= 6:
        setup_crd(username, crp_command, pin)
    else:
        print("Invalid CRP command or PIN")
