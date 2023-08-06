#!/bin/bash
# KernelCheck script v. 1.0.0.5

if [ -z "$1" ]; then 
echo
echo "This script should only be run with KernelCheck."
echo
exit
fi

# Define all global variables
FUNCTION=$1
CONFIGURE=$2
RECONFIGURE=$3
DIR=$4
STABLE=$(head -1 $DIR)
STABLE_URL=$(head -2 $DIR | tail -1)
PATCH=$(head -3 $DIR | tail -1)
PATCH_URL=$(head -4 $DIR | tail -1)
ENVY_SUPPORT=$(head -5 $DIR | tail -1)

# Trap signals
trap term_exit TERM HUP INT

function term_exit
{
rm -rf /tmp/$DIR
echo -e "\033[1;31mABORT: interrupted."
echo
exit 2
}

# Function to check the return code of commands
function checkretcode {
ERRORCODE=$?
if [ "$ERRORCODE" -ne 0 ]
then
echo
echo -e "\033[1;31mABORT: $1 returned exit status $ERRORCODE"
echo -e "\033[0m"
touch /tmp/stage-failed.tmp
rm -rf /tmp/$DIR
exit 1
fi 
}

# Test to see if the user is using proprietary graphics drivers
function test_graphics {
PROPRIETARY=$(cat /etc/X11/xorg.conf | grep "nvidia" || cat /etc/X11/xorg.conf | grep "fglrx")
if [ "$PROPRIETARY" != "" ]
    then
    if [ "$(cat /etc/X11/xorg.conf | grep "fglrx")" != "" ]; then DRIVER="fglrx"; else DRIVER="nvidia"; fi
    echo
    echo "A proprietary driver [$DRIVER] has been detected on your system."
    echo "It is strongly recommended that you reconfigure the X server to avoid graphics problems upon reboot."
    echo
    echo -n "Do you wish to reconfigure the X server now? [Y/n] "
    read -e RECONFIGURE
    case $RECONFIGURE in
        "n" | "no" | "NO" | "No" )
            echo -e "\033[1;31mWARNING: Proceeding without X Server configuration"
            echo -e "\033[0m"
        ;;
        * )
            echo -e "\033[1;32mReconfiguring the X Server..."
            echo "NOTE: You will have to reinstall your video driver after rebooting. Press ENTER to continue."
            read
            echo -e "\033[0m"
            dpkg-reconfigure -phigh xserver-xorg
        ;;
    esac
fi
}

function prestage {
cd /usr/src/
if [ ! -d oldpackages ]; then mkdir oldpackages; checkretcode prestage; fi
echo -e "\033[1;31mPrestage: Housekeeping (this may take a few minutes)"
echo -e "\033[0m"
if [ -f *.deb ]; then mv *.deb oldpackages/; fi
checkretcode prestage
rm -rf linux-$STABLE linux
checkretcode prestage

if [ $RECONFIGURE = "True" ]
then
echo -e "\033[1;31mPrestage: Reconfigure the X server"
echo -e "\033[0m"
dpkg-reconfigure -phigh xserver-xorg
checkretcode prestage
fi

if [ $ENVY_SUPPORT = "True" ]
then
echo -e "\033[1;31mPrestage: Installing Envy"
echo -e "\033[0m"
if [ $(cat /etc/lsb-release | grep "hardy") != "" ]
then
echo "deb http://archive.ubuntu.com/ubuntu/ hardy universe multiverse" | sudo tee -a /etc/apt/sources.list.d/kernelcheck.list
checkretcode prestage
apt-get update
checkretcode prestage
apt-get install -y --force-yes envyng-core envyng-gtk envyng-qt
checkretcode prestage
rm -rf /etc/apt/sources.list.d/kernelcheck.list
checkretcode prestage
fi
fi
}

function stage1 {
echo -e "\033[1;31mStage 1/6: Installing dependencies"
echo -e "\033[0m"
apt-get update
apt-get install -y --force-yes build-essential bin86 kernel-package libqt3-headers libqt3-mt-dev wget libncurses5 libncurses5-dev
apt-get install -f
checkretcode stage1
exit
}

function stage2 {
echo -e "\033[1;31mStage 2/6: Downloading packages"
echo -e "\033[0m"
cd /usr/src
wget -c $STABLE_URL
if [ $PATCH != $STABLE ]; then wget -c $PATCH_URL; checkretcode stage2; fi
exit
}

function stage3 {
cd /usr/src
echo -e "\033[1;31mStage 3/6: Extracting packages (this may take a few minutes)"
echo -e "\033[0m"
tar -xjf linux-$STABLE.tar.bz2
checkretcode stage3
cd /usr/src
rm -rf linux
ln -s /usr/src/linux-$STABLE linux
if [ $(echo $PATCH | grep mm) != "" ]; then cd /usr/src/linux; bzcat /usr/src/$PATCH.bz2 | patch -p1
else
if [ $PATCH != $STABLE ]; then cd /usr/src/linux; bzcat /usr/src/patch-$PATCH.bz2 | patch -p1; fi
fi
checkretcode stage3
exit
}

function stage4 {
cd /usr/src/linux
echo ""
echo -e "\033[1;31mStage 4/6: Configuring the new kernel"
echo -e "\033[0m"
cp /boot/config-`uname -r` .config
yes "" | make oldconfig
if [ $CONFIGURE = "True" ]
then make xconfig
fi
echo ""
exit
}

function stage5 {
cd /usr/src/linux
echo -e "\033[1;31mStage 5/6: Cleaning up for the build"
echo -e "\033[0m"
make-kpkg clean
checkretcode stage5
echo ""
exit
}

function stage6 {
cd /usr/src/linux
echo -e "\033[1;31mStage 6/6: Building the new kernel"
echo -e "\033[0m"
INSTALL_MOD_STRIP=1 CONCURRENCY_LEVEL=2 make-kpkg --initrd --append-to-version=-ultimate kernel_image kernel_headers modules_image
checkretcode stage6
test_graphics
exit
}

function stage7 {
cd /usr/src
echo -e "\033[1;31mFinishing up: Installing new kernel packages"
echo -e "\033[0m"
#Fixed 6/24
dpkg -i linux-image-*.deb
dpkg -i linux-headers-*.deb
apt-get install -f
checkretcode dpkg
exit
}

case $FUNCTION in
    prestage) prestage
    ;;
    stage1) stage1
    ;;
    stage2) stage2
    ;;
    stage3) stage3
    ;;
    stage4) stage4
    ;;
    stage5) stage5
    ;;
    stage6) stage6
    ;;
    stage7) stage7
    ;;
esac
