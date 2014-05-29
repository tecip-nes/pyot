#!/bin/bash
# ------------------------------------------------------------------
# [Andrea Azzara, Giovanni Pellerano] 
#        Installs general requirements, Contiki and PyoT on the Vagrant machine. 


# Install some packages using apt-get
export DEBIAN_FRONTEND=noninteractive
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
                      linux-headers-generic \
                      openjdk-7-jdk \
                      openjdk-7-jre \
                      ant \
                      unzip \
                      vim \
                      gedit \
                      nautilus-open-terminal \
                      python-pip \
                      gcc-msp430 \
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
                      libpng12-dev


#apt-get -q -y dist-upgrade
update-alternatives --set java /usr/lib/jvm/java-7-openjdk-i386/jre/bin/java
# delete each xsession except gnome-classic.desktop
shopt -s extglob
cd /usr/share/xsessions && rm !(gnome-classic.desktop)

gsettings set org.gnome.desktop.lockdown disable-lock-screen true


cd /home/vagrant
git clone https://github.com/contiki-os/contiki.git
cd contiki
git checkout 2.7
git submodule update --init

#workaround to stop flooding of cooja warning messages
sed -i '221 s/^/\/\//' /home/vagrant/contiki/tools/cooja/apps/mspsim/src/se/sics/cooja/mspmote/MspMote.java

cd tools
make tunslip6
cd cooja
ant run

echo "export CONTIKI=\"/home/vagrant/contiki\"" >> /home/vagrant/.profile

cd /home/vagrant

PYOT=/home/vagrant/pyot
DESKTOP=/home/vagrant/Desktop
git clone https://github.com/tecip-nes/pyot.git
cd $PYOT/libcoap-4.0.1/
./configure
make

cd /home/vagrant/pyot
./install_reqs.sh

ln -s $PYOT                     $DESKTOP/pyot 

./install_db.sh

#echo -e "XKBMODEL=\"pc105\"\n" > /etc/default/keyboard
#echo -e "XKBLAYOUT=\"it\"\n" >> /etc/default/keyboard
#echo -e "XKBVARIANT=\"\"\n" >> /etc/default/keyboard
#echo -e "XKBOPTIONS=\"\"\n" >> /etc/default/keyboard

GDMCONF=/etc/gdm/custom.conf
echo -e "[daemon]" > $GDMCONF
echo -e "TimedLoginEnable=false" >> $GDMCONF
echo -e "AutomaticLoginEnable=true" >> $GDMCONF
echo -e "TimedLogin=vagrant" >> $GDMCONF
echo -e "AutomaticLogin=vagrant" >> $GDMCONF
echo -e "TimedLoginDelay=30" >> $GDMCONF
echo -e "DefaultSession=gnome-2d" >> $GDMCONF

chown -R vagrant /home/vagrant/
