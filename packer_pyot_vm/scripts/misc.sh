#!/bin/bash
# ------------------------------------------------------------------
# [Andrea Azzara, Giovanni Pellerano] 
#        Installs general requirements, Contiki and PyoT on the Vagrant machine. 


# Install some packages using apt-get
export DEBIAN_FRONTEND=noninteractive
rm -rf /var/lib/apt/lists/*
apt-get update -q
apt-get install -q -y -o Dpkg::Options::="--force-confdef" \
                      -o Dpkg::Options::="--force-confold" \
                      xorg \
                      gnome-core \
                      gnome-applets \
                      gnome-system-tools \
                      gnome-utils \
                      git \
                      build-essential \
                      autoconf \
                      linux-headers-generic \
                      openjdk-7-jdk \
                      openjdk-7-jre \
                      ant \
                      unzip \
                      vim \
                      gedit \
                      nautilus-open-terminal \
                      python-pip \
                      chromium-browser\
                      python-mysqldb \
                      libmysqlclient-dev \
                      rabbitmq-server \
                      python-pip \
                      python-dev \
                      libcurl4-gnutls-dev \
                      graphviz \
                      libgraphviz-dev  \
                      libfreetype6-dev \
                      libpng12-dev \
                      software-properties-common \
                      ttf-ubuntu-font-family

add-apt-repository -y ppa:fkrull/deadsnakes
apt-get update -q                       

apt-get install -q -y -o Dpkg::Options::="--force-confdef" \
                      -o Dpkg::Options::="--force-confold" \
                      python2.6 \
                      python2.6-dev

#apt-get -q -y dist-upgrade
update-alternatives --set java /usr/lib/jvm/java-7-openjdk-i386/jre/bin/java
# delete each xsession except gnome-classic.desktop
shopt -s extglob
cd /usr/share/xsessions && rm !(gnome-classic.desktop)

gsettings set org.gnome.desktop.lockdown disable-lock-screen true

#sudo apt-get install  ttf-ubuntu-font-family  sudo aptitude install --without-recommends ubuntu-desktop

cd /opt/
wget http://retis.sssup.it/~a.azzara/mspgcc-4.7.2.zip
unzip mspgcc-4.7.2.zip

cd /home/vagrant

PYOT=/home/vagrant/pyot
DESKTOP=/home/vagrant/Desktop
git clone https://github.com/tecip-nes/pyot.git

cd $PYOT
./a_install_reqs.sh
./b_install_db.sh

ln -s $PYOT                     $DESKTOP/pyot 

GDMCONF=/etc/gdm/custom.conf
echo -e "[daemon]" > $GDMCONF
echo -e "TimedLoginEnable=false" >> $GDMCONF
echo -e "AutomaticLoginEnable=true" >> $GDMCONF
echo -e "TimedLogin=vagrant" >> $GDMCONF
echo -e "AutomaticLogin=vagrant" >> $GDMCONF
echo -e "TimedLoginDelay=30" >> $GDMCONF
echo -e "DefaultSession=gnome-2d" >> $GDMCONF

PROFILE=/home/vagrant/.profile
echo -e "gsettings set org.gnome.desktop.screensaver lock-enabled false" >> $PROFILE
echo -e "export PATH=${PATH}:/opt/mspgcc-4.7.2/bin"  >> $PROFILE
chown -R vagrant /home/vagrant/
