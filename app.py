import os
import subprocess

# Function to create user and configure
def create_user(username, password):
    print("Creating User and Setting it up")
    
    # Creation of user
    os.system(f"sudo useradd -m {username} &> /dev/null")
    
    # Add user to sudo group
    os.system(f"sudo adduser {username} sudo &> /dev/null")
    
    # Set password of user
    os.system(f"echo '{username}:{password}' | sudo chpasswd")
    
    # Change default shell from sh to bash
    os.system("sed -i 's/\\/bin\\/sh/\\/bin\\/bash/g' /etc/passwd")
    
    print("User Created and Configured")

# Function for Chrome Remote Desktop setup
def crd_setup(username, crp_command, pin):
    def write_script():
        script_content = """\
#! /bin/bash
b='\\033[1m'
r='\\E[31m'
g='\\E[32m'
c='\\E[36m'
endc='\\E[0m'
enda='\\033[0m'

printf "\\n\\n$c$b    Loading Installer $endc$enda" >&2
if sudo apt-get update &> /dev/null
then
    printf "\\r$g$b    Installer Loaded $endc$enda\\n" >&2
else
    printf "\\r$r$b    Error Occurred $endc$enda\\n" >&2
    exit
fi

printf "\\n$g$b    Installing Chrome Remote Desktop $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
    sudo dpkg --install chrome-remote-desktop_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\\r$c$b    Chrome Remote Desktop Installed $endc$enda\\n" >&2 ||
{ printf "\\r$r$b    Error Occurred $endc$enda\\n" >&2; exit; }
sleep 3

printf "$g$b    Installing Desktop Environment $endc$enda" >&2
{
    sudo DEBIAN_FRONTEND=noninteractive apt install --assume-yes xfce4 desktop-base xfce4-terminal
    sudo bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'
    sudo apt remove --assume-yes gnome-terminal
    sudo apt install --assume-yes xscreensaver
    sudo systemctl disable lightdm.service
} &> /dev/null &&
printf "\\r$c$b    Desktop Environment Installed $endc$enda\\n" >&2 ||
{ printf "\\r$r$b    Error Occurred $endc$enda\\n" >&2; exit; }
sleep 3

printf "$g$b    Installing Google Chrome $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg --install google-chrome-stable_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\\r$c$b    Google Chrome Installed $endc$enda\\n" >&2 ||
printf "\\r$r$b    Error Occurred $endc$enda\\n" >&2
sleep 3

printf "$g$b    Installing other Tools $endc$enda" >&2
if sudo apt install nautilus nano -y &> /dev/null
then
    printf "\\r$c$b    Other Tools Installed $endc$enda\\n" >&2
else
    printf "\\r$r$b    Error Occurred $endc$enda\\n" >&2
fi
sleep 3

printf "\\n$g$b    Installation Completed $endc$enda\\n\\n" >&2"""
        with open("install.sh", "w") as f:
            f.write(script_content)
    
    write_script()
    
    os.system("chmod +x install.sh")
    os.system("./install.sh")
    
    # Adding user to CRP group
    os.system(f"sudo adduser {username} chrome-remote-desktop &> /dev/null")
    
    # Finishing setup
    os.system(f"su - {username} -c '{crp_command} --pin={pin}' &> /dev/null")
    print("Finished Successfully")

# Input details
username = "curseofwithcer"
password = "curseofwitcher"
crp_command = """DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="4/0AanRRrtSQdTkGDFyLl3JmgsPQZuQqHgWBLPWkj0k3EOTE9ye7V4Zf3awKXdNAw9ZgmeT_Q" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)"""
pin = 149149

if __name__ == "__main__":
    try:
        if not username or not password:
            raise ValueError("Please set username and password.")
        
        if not crp_command:
            raise ValueError("Please enter the authentication command from the provided link.")
        
        if len(str(pin)) < 6:
            raise ValueError("Pin must be 6 or more digits.")
        
        create_user(username, password)
        crd_setup(username, crp_command, pin)
    except Exception as e:
        print(str(e))
