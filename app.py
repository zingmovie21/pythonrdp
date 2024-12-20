#@title **Create User**
#@markdown Enter Username and Password

username = "user" #@param {type:"string"}
password = "root" #@param {type:"string"}

print("Creating User and Setting it up")

# Creation of user
! sudo useradd -m $username &> /dev/null

# Add user to sudo group
! sudo adduser $username sudo &> /dev/null
    
# Set password of user to 'root'
! echo '$username:$password' | sudo chpasswd

# Change default shell from sh to bash
! sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd

print("User Created and Configured")

#@title **RDP**
#@markdown  It takes 4-5 minutes for installation

#@markdown  Visit http://remotedesktop.google.com/headless and Copy the command after authentication

CRP = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/0AanRRruXG7_f0lm5l3odlg2dw1dA5-ZpZTNLlCbSY26oQxvS48wgwXsLrSHjNP0tPsj1vg\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=$(hostname)" #@param {type:"string"}

#@markdown Enter a pin more or equal to 6 digits
Pin = 149149 #@param {type: "integer"}

def CRD():
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
    printf "\r$r$b    Error Occured $endc$enda\n" >&2
    exit
fi

printf "\n$g$b    Installing Chrome Remote Desktop $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
    sudo dpkg --install chrome-remote-desktop_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\r$c$b    Chrome Remote Desktop Installed $endc$enda\n" >&2 ||
{ printf "\r$r$b    Error Occured $endc$enda\n" >&2; exit; }
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
{ printf "\r$r$b    Error Occured $endc$enda\n" >&2; exit; }
sleep 3

printf "$g$b    Installing Google Chrome $endc$enda" >&2
{
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg --install google-chrome-stable_current_amd64.deb
    sudo apt install --assume-yes --fix-broken
} &> /dev/null &&
printf "\r$c$b    Google Chrome Installed $endc$enda\n" >&2 ||
printf "\r$r$b    Error Occured $endc$enda\n" >&2
sleep 3

printf "$g$b    Installing other Tools $endc$enda" >&2
if sudo apt install nautilus nano -y &> /dev/null
then
    printf "\r$c$b    Other Tools Installed $endc$enda\n" >&2
else
    printf "\r$r$b    Error Occured $endc$enda\n" >&2
fi
sleep 3

printf "\n$g$b    Installation Completed $endc$enda\n\n" >&2""")

    ! chmod +x install.sh
    ! ./install.sh

    # Adding user to CRP group
    ! sudo adduser $username chrome-remote-desktop &> /dev/null

    # Finishing Work
    ! su - $username -c """$CRP --pin=$Pin""" &> /dev/null

    print("Finished Succesfully")

try:
    if username:
        if CRP == "":
            print("Please enter authcode from the given link")
        elif len(str(Pin)) < 6:
            print("Enter a pin more or equal to 6 digits")
        else:
            CRD()
except NameError:
    print("username variable not found")
    print("Create a User First")
    
