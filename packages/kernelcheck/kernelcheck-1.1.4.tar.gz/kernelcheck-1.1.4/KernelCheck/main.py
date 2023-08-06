#!/usr/bin/env python
#
# KernelCheck
# Copyright (C) Master Kernel 2008 <master.kernel.contact@gmail.com>
#
# KernelCheck is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KernelCheck is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import needed modules
import gnome.ui
import gtk.glade
import os
import sys
import re
import signal
import socket
import urllib2
import tempfile
import build_kernel
import about
import gobject
import pango

# Try to import gtk
try:
  import gtk
except:
  print >> sys.stderr, "You need to install the python gtk bindings"
  sys.exit(1)

# Try to import vte
try:
  import vte
except:
  error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
    'You need to install python bindings for libvte')
  error.run()
  sys.exit (1)

# Set global variables
APPNAME="KernelCheck"
APPVERSION="1.1.4"

# Trap interrupting signals and exit safely
def signal_handler(signal, frame):
    print
    print
    print "Signal caught. Exiting safely."
    try:
        gtk.main_quit()
    except:
        sys.exit(1)
    print

signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Procedure to retrieve all needed information
def kernelinfo():

    try:

        ###---Retrieval: stable
        print "Caching stable webpage from kernel.org"
        htmlFeed = urllib2.urlopen("http://master.kernel.org/kdist/fragments/stable.html")
        stable_contents = htmlFeed.read()
        stable_temp = tempfile.mktemp()
        stable_path = 'file://' + stable_temp
        stable_file = os.open(stable_temp, os.O_CREAT | os.O_RDWR)
        os.write(stable_file, stable_contents)
        os.close(stable_file)
        print "Page successfully cached"
        print

        ###---Retrieval: prepatch
        print "Caching stable prepatch webpage from kernel.org"
        htmlFeed = urllib2.urlopen("http://master.kernel.org/kdist/fragments/stable_prepatch.html")
        prepatch_contents = htmlFeed.read()
        prepatch_temp = tempfile.mktemp()
        prepatch_path = 'file://' + prepatch_temp
        prepatch_file = os.open(prepatch_temp, os.O_CREAT | os.O_RDWR)
        os.write(prepatch_file, prepatch_contents)
        os.close(prepatch_file)
        print "Page successfully cached"
        print

        ###---Retrieval: mm
        print "Caching stable mm patch webpage from kernel.org"
        htmlFeed = urllib2.urlopen("http://master.kernel.org/kdist/fragments/stable_mm_patch.html")
        mm_contents = htmlFeed.read()
        mm_temp = tempfile.mktemp()
        mm_path = 'file://' + mm_temp
        mm_file = os.open(mm_temp, os.O_CREAT | os.O_RDWR)
        os.write(mm_file, mm_contents)
        os.close(mm_file)
        print "Page successfully cached"
        print

    except urllib2.HTTPError:
        print "Error: master.kernel.org site is down."
        print
        sys.exit(1)

    ###---The parse process - stable
    # Retrieves information about stable patch
    htmlFeed = urllib2.urlopen(stable_path)
    htmlLinks = re.searchhtmlLinks = re.search('<td><b><a href="(.*)">', htmlFeed.read())
    patch_url = htmlLinks.group(1)
    patch_url = "http://www.kernel.org" + patch_url
    # Retrieves URL of stable patch
    htmlFeed = urllib2.urlopen(stable_path)
    htmlLinks = re.searchhtmlLinks = re.search('<td><a href="(.*)">', htmlFeed.read())
    url = htmlLinks.group(1)
    # Retrieves date of stable patch
    htmlFeed = urllib2.urlopen(stable_path)
    htmlLinks = re.searchhtmlLinks = re.search('<td>(.*UTC)</td>', htmlFeed.read())
    patch_releasedate = htmlLinks.group(1)

    os.remove(stable_temp)

    # Parse url to get version
    patch = url.split('-')
    patch = patch[1].split('.tar')
    patch = patch[0]
    patch = str(patch)
    point = patch.split('.')
    point1 = point[0]
    point2 = point[1]
    point3 = point[2]
    stable = point1+"."+point2+"."+point3
    stable_url = "http://kernel.org/pub/linux/kernel/v2.6/linux-" + stable + ".tar.bz2"

    ###---The parse process - prepatch
    # Gets information from kernel.org
    if prepatch_contents == "":

        prepatch = "None"
        prepatch_url = "http://www.kernel.org"
        prepatch_releasedate = "None"
        prepatch_flag = 1

        os.remove(prepatch_temp)

    else:
        # Retrieves current stable prepatch
        htmlFeed = urllib2.urlopen(prepatch_path)
        htmlLinks = re.searchhtmlLinks = re.search('<title>(.*):', htmlFeed.read())
        prepatch = htmlLinks.group(1)
        # Retrieves current stable prepatch URL
        htmlFeed = urllib2.urlopen(prepatch_path)
        htmlLinks = re.searchhtmlLinks = re.search('<td><b><a href="(.*)"', htmlFeed.read())
        prepatch_url = htmlLinks.group(1)
        prepatch_url = "http://www.kernel.org"+prepatch_url
        # Retrieves date of stable prepatch
        htmlFeed = urllib2.urlopen(prepatch_path)
        htmlLinks = re.searchhtmlLinks = re.search('<td>(.*UTC)</td>', htmlFeed.read())
        prepatch_releasedate = htmlLinks.group(1)
        prepatch_flag = 0

        os.remove(prepatch_temp)

    ###---The parse process -- mm
    # Gets information from kernel.org
    if mm_contents == "":

        mm = "None"
        mm_url = "http://www.kernel.org"
        mm_flag = 1
        mapplyto = False

        os.remove(mm_temp)

    else:
        # Retrieves current stable prepatch
        htmlFeed = urllib2.urlopen(mm_path)
        htmlLinks = re.searchhtmlLinks = re.search('<title>(.*):', htmlFeed.read())
        mm = htmlLinks.group(1)
        # Retrieves current stable prepatch URL
        htmlFeed = urllib2.urlopen(mm_path)
        htmlLinks = re.searchhtmlLinks = re.search('<td><b><a href="(.*)"', htmlFeed.read())
        mm_url = htmlLinks.group(1)
        mm_url = "http://www.kernel.org"+mm_url

        # Parse the mm string to find out if I can apply the patch
        try:
            splitup = mm.split('-')
            number = len(splitup) -1
            if number >> 1:
                mm_real = splitup[0]+'-'+splitup[1]
            elif number == 1:
                mm_real = splitup[0]
        except:
            mm_real = mm

        mver = mm_real.split('.')
        mver = mver[2]

        try:
            mver = mver.split('-')
            mver = mver[0]
        except:
            pass

        mver = int(mver)
        check = int(point3)

        if mver == check:
            mapplyto = [stable_url, stable]
        elif mver > check:
            mapplyto = ['http://kernel.org/pub/linux/kernel/v2.6/testing/linux-'+str(mm_real)+'.tar.bz2', mm_real]
        elif mver < check:
            mapplyto = False

        mm_flag = 0
        os.remove(mm_temp)

    ###---Return data
    return patch_url, patch_releasedate, patch, stable, stable_url, prepatch, prepatch_url, prepatch_releasedate, prepatch_flag, mm, mm_url, mm_flag, mapplyto

def checkrelease():
    try:

        ###---Retrieval: KernelCheck
        print "Caching banner from kcheck.sf.net"
        htmlFeed = urllib2.urlopen("http://kcheck.sourceforge.net/pool/finger_banner2")
        kcheck_contents = htmlFeed.read()
        kcheck_temp = tempfile.mktemp()
        kcheck_path = 'file://' + kcheck_temp
        kcheck_file = os.open(kcheck_temp, os.O_CREAT | os.O_RDWR)
        os.write(kcheck_file, kcheck_contents)
        os.close(kcheck_file)
        print "Page successfully cached"
        print

    except urllib2.HTTPError:
        print "Error: kcheck.sourceforge.net site is down."
        print
        sys.exit(1)

    ###---The parse process -- version
    htmlFeed = urllib2.urlopen(kcheck_path)
    htmlLinks = re.searchhtmlLinks = re.search('(.*)', htmlFeed.read())
    kernelcheck_release = htmlLinks.group(1)
    kernelcheck_release = kernelcheck_release.split('=')
    kernelcheck_release = kernelcheck_release[1].split(']')
    kernelcheck_release = kernelcheck_release[0]
    kernelcheck_release = str(kernelcheck_release)
    split = kernelcheck_release.split('.')
    major = split[0]
    minor = split[1]
    revision = split[2]
    os.remove(kcheck_temp)

    return kernelcheck_release, major, minor, revision

# Procedure to retrieve running kernel information
def runninginfo():
    # Gets your running kernel info
    running_kernel = os.uname()
    running_kernel = running_kernel[2]

    # Gets the running kernel information without the revision
    try:
        running_kernel = running_kernel.split('-')
        running_kernel = running_kernel[0]
    except:
        pass

    return running_kernel

class KernelCheck:

    def __init__(self):

        # Check if there is an internet connection
        if self.net_test():
            print "Connection found."
        else:
            error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, 'You are not connected to the internet. Certain features may be disabled.')
            error.run()
            print "Connection refused."
            sys.exit(1)

        # Initialize the program in Gnome's memory
        gnome.init(APPNAME, APPVERSION)

        # Get the Glade file and retrieve needed widgets
        self.widgets = gtk.glade.XML("/usr/lib/python2.5/site-packages/KernelCheck/library/main.glade")
        self.lblRunningKernel = self.widgets.get_widget("lblRunningKernel")
        self.lblLatestKernel = self.widgets.get_widget("lblLatestKernel")
        self.lblLatestKernelPatch = self.widgets.get_widget("lblLatestKernelPatch")
        self.lblLatestPrepatch = self.widgets.get_widget("lblLatestPrepatch")
        self.lblLatestMMPatch = self.widgets.get_widget("lblLatestMMPatch")
        self.lblLatestZenPatchset = self.widgets.get_widget("lblLatestZenPatchset")
        self.lblKernelPatchRelease = self.widgets.get_widget("lblKernelPatchRelease")
        self.lblKernelPrepatchRelease = self.widgets.get_widget("lblKernelPrepatchRelease")
        self.radPatch = self.widgets.get_widget("radPatch")
        self.radPrepatch = self.widgets.get_widget("radPrepatch")
        self.radNoPatch = self.widgets.get_widget("radNoPatch")
        self.radMMPatch = self.widgets.get_widget("radMMPatch")
        self.radCustomPatch = self.widgets.get_widget("radCustomPatch")
        self.chkConfigure = self.widgets.get_widget("chkConfigure")
        self.chkReconfigureX = self.widgets.get_widget("chkReconfigureX")
        self.chkEnvy = self.widgets.get_widget("chkEnvy")
        self.statusbar = self.widgets.get_widget("statusbar")
        self.ProgressBar = self.widgets.get_widget("ProgressBar")
        self.expander1 = self.widgets.get_widget("expander1")
        self.expander2 = self.widgets.get_widget("expander2")
        self.expander3 = self.widgets.get_widget("expander3")
        self.expander4 = self.widgets.get_widget("expander4")
        self.mnuBuild = self.widgets.get_widget("mnuBuild")
        self.mnuConnect = self.widgets.get_widget("mnuConnect")
        self.mnuUpdates = self.widgets.get_widget("mnuUpdates")
        self.mnuDocumentation = self.widgets.get_widget("mnuDocumentation")
        self.mnuQuit = self.widgets.get_widget("mnuQuit")
        self.btnQuit = self.widgets.get_widget("btnQuit")

        # Let the program know a kernel is not building
        self.buildlock = False

        # Add a terminal
        self.Terminal = vte.Terminal()
        self.widgets.get_widget("TerminalFrame").add(self.Terminal)
        font = pango.FontDescription("monospace normal 8")
        self.Terminal.set_font(font)
        self.Terminal.show()
        # If the program exits, stop the loop
        self.Terminal.connect ("child-exited", self.run_command_done_callback)
        self.Terminal.connect('eof', self.run_command_done_callback)

        # Define and connect the event dictionary
        signalDic = { "on_MainWindow_destroy" : self.destroy_window,
                      "on_btnQuit_clicked" : self.destroy_window,
                      "on_mnuBuild_activate" : self.build,
                      "on_btnConnect_clicked" : self.getdata,
                      "on_mnuConnect_activate" : self.getdata,
                      "on_mnuAbout_activate" : self.about,
                      "on_mnuUpdates_activate" : self.updates,
                      "on_mnuDocumentation_activate" : self.help,
                      "on_MainWindow_delete_event" : self.returnt,
                      "on_mnuQuit_activate" : self.destroy_window }
        self.widgets.signal_autoconnect(signalDic)

        # Add a message to the statusbar
        context_id = self.statusbar.get_context_id("data")
        self.push_item(context_id, "Download the kernel information to begin")
        gtk.main_iteration()

    # Traps the destroy signal so the program doesn't close before the message box is shown
    def returnt(self, widget, arg):
        self.destroy_window("argument")
        return True

    # Procedure for the network connection
    def net_test(self):
        print "\nTesting your network connection..."
        try:
            internet = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            internet.connect(("www.google.com", 80))
            return True
        except socket.error:
            return False

    # Make sure the user cannot accidentally close the window when the kernel is building
    def closeallowed(self, sensitivity):
        self.btnQuit.set_sensitive(sensitivity)
        self.mnuQuit.set_sensitive(sensitivity)
        self.mnuUpdates.set_sensitive(sensitivity)
        self.mnuBuild.set_sensitive(sensitivity)

    # Removes the last item in the statusbar
    def poplast(self):
        if self.buildlock == False:
            context_id = self.statusbar.get_context_id("data")
            self.pop_item(context_id)

    # Statusbar push item (put it into the status bar)
    def push_item(self, data, prompt):
        try:
            context_id = self.statusbar.get_context_id("data")
            self.pop_item(context_id)
        except:
            pass
        self.statusbar.push(data, prompt)
        return

    # Statusbar pop item (remove it from the statusbar)
    def pop_item(self, data):
        self.statusbar.pop(data)
        return

    # Run a command in the terminal
    def run_command(self, command_string):
        '''''run_command runs the command_string in the terminal. This
        function will only return when self.thread_running is set to
        True, this is done by run_command_done_callback'''
        self.thread_running = True

        command = command_string.split(' ')
        pid = self.Terminal.fork_command(command=command[0], argv=command, directory=os.getcwd())

        while self.thread_running:
            gtk.main_iteration()

    # Command finished
    def run_command_done_callback(self, terminal):
        '''''When called this function sets the thread as done allowing
        the run_command function to exit'''
        self.thread_running = False
        return

    # Close the about window
    def close(self, w, res):
        if res == gtk.RESPONSE_CLOSE:
            w.hide()

    # When an error occurs, reset everything
    def errorreset(self):
        error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, 'An error has occurred. Please check the terminal for details.')
        error.connect("response", self.close)
        error.run()
        context_id = self.statusbar.get_context_id("data")
        self.push_item(context_id, "An error has occurred.")
        self.ProgressBar.set_fraction(0.0)
        self.ProgressBar.set_text('An error has occurred.')
        self.error = True
        self.buildlock = False
        self.closeallowed(True)

    # Check if there was an error with the last command ran in the terminal
    def checkerror(self):
        try:
            file = open('/tmp/stage-failed.tmp', 'r')
        except IOError:
            pass
        else:
            file.close()
            os.remove('/tmp/stage-failed.tmp')
            self.errorreset()

    # Get the data for the program
    def getdata(self, widget):

        context_id = self.statusbar.get_context_id("data")
        self.pop_item(context_id)

        # Put this message in the status bar
        self.push_item(context_id, "Retrieving data from Kernel.org")
        gtk.main_iteration()

        global stable, stable_url, patch, patch_url, prepatch, prepatch_url, mapplyto, prepatch_flag, mm, mm_url
        patch_url, patch_releasedate, patch, stable, stable_url, prepatch, prepatch_url, prepatch_releasedate, prepatch_flag, mm, mm_url, mm_flag, mapplyto = kernelinfo()

        # Check if any patches are unavailable
        self.check_patches()

        # Get the running kernel info
        self.push_item(context_id, "Getting running kernel")
        gtk.main_iteration()
        running_kernel = runninginfo()

        # Add a message and remove it after 10 seconds
        self.push_item(context_id, "Data retrieved")
        self.buildlock = False
        gtk.main_iteration()
        gobject.timeout_add(10000, self.poplast)

        # Data is put into labels in main window
        self.lblRunningKernel.set_text("Running Kernel: " + running_kernel)
        self.lblLatestKernel.set_text("Latest Kernel: " + stable)
        self.lblLatestKernelPatch.set_text("Latest Kernel Patch: " + patch)
        self.lblLatestPrepatch.set_text("Latest Kernel Prepatch: " + prepatch)
        self.lblLatestMMPatch.set_text("Latest MM Patch: " + mm)
        self.lblKernelPatchRelease.set_text("Kernel Patch Release: " + patch_releasedate)
        self.lblKernelPrepatchRelease.set_text("Kernel Prepatch Release: " + prepatch_releasedate)
        self.mnuBuild.set_sensitive(True)
        self.expander1.set_sensitive(True)
        self.expander2.set_sensitive(True)
        self.expander3.set_sensitive(True)

    # Disable those patches that cannot be used
    def check_patches(self):
        if mapplyto == False:
            self.radMMPatch.set_sensitive(False)
            print "MM patch unavailable for kernels older than "+ stable
        if prepatch_flag == 1:
            self.radPrepatch.set_sensitive(False)
            print "Development prepatch unavailable"
        if patch == stable:
            self.radPatch.set_sensitive(False)
            print "No performance patch available at this time"
            self.radNoPatch.set_active(True)

    # When the user wants to build the kernel, run this
    def build(self, widget):
        context_id = self.statusbar.get_context_id("data")
        self.pop_item(context_id)

        # Get the state of the checkboxes
        reconfigure = self.chkReconfigureX.get_active()
        config = self.chkConfigure.get_active()
        envy = self.chkEnvy.get_active()

        global stable, stable_url, patch, patch_url, prepatch, prepatch_url, mm, mm_url, mapplyto
        if self.radPatch.get_active() == True:
            patchtype = "Normal"
            source = stable
            source_url = stable_url
            call = patch
            call_url = patch_url
        elif self.radPrepatch.get_active() == True:
            patchtype = "Prepatch"
            source = stable
            source_url = stable_url
            call = prepatch
            call_url = prepatch_url
        elif self.radNoPatch.get_active() == True:
            patchtype = "None"
            source = stable
            source_url = stable_url
            call = stable
            call_url = patch_url
        elif self.radMMPatch.get_active() == True:
            patchtype = "MM"
            source = mapplyto[1]
            source_url = mapplyto[0]
            call = mm
            call_url = mm_url
        elif self.radCustomPatch.get_active() == True:
            patchtype = "Custom"
            source = stable
            source_url = stable_url
            call = stable
            call_url = patch_url

        # Put the data in an array
        data = [source, source_url, call, call_url, envy]

        # Pop out the expander and allow the building process to be viewed
        self.expander4.set_sensitive(True)
        self.expander4.set_expanded(True)

        # Get the temporary file where the KC settings are stored
        self.error = False
        self.buildlock = True
        self.closeallowed(False)
        self.push_item(context_id, "Getting temporary path")
        gtk.main_iteration()
        temp_path = build_kernel.build(config, reconfigure, patchtype, data)

        # Run the various stages of the shell script
        self.push_item(context_id, "Running prestages")
        gtk.main_iteration()
        self.ProgressBar.set_fraction(0.04)
        self.ProgressBar.set_text("Running prestages")
        self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh prestage '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
        self.checkerror()

        if not self.error:
            self.push_item(context_id, "Installing dependencies")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.1)
            self.ProgressBar.set_text("Installing dependencies")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage1 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Downloading packages")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.2)
            self.ProgressBar.set_text("Downloading packages")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage2 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Extracting the packages")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.3)
            self.ProgressBar.set_text("Extracting the packages")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage3 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error and (self.radCustomPatch.get_active() == True):
            self.push_item(context_id, "Apply custom patch")
            gtk.main_iteration()
            self.ProgressBar.set_text("Apply custom patch")
            import virtualterminal
            virtualterminal.console()

        if not self.error:
            self.push_item(context_id, "Configuring the packages")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.4)
            self.ProgressBar.set_text("Configuring the kernel")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage4 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Cleaning up for the build")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.5)
            self.ProgressBar.set_text("Cleaning up for the build")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage5 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Building kernel: process takes about 2-4 hours")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.7)
            self.ProgressBar.set_text("Building kernel: process takes about 2-4 hours")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage6 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Finishing up: Installing new kernel packages")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(0.9)
            self.ProgressBar.set_text("Finishing up: Installing new kernel packages")
            process = self.run_command('bash /usr/lib/python2.5/site-packages/KernelCheck/library/kscript.sh stage7 '+str(config)+' '+str(reconfigure)+' '+str(temp_path)+'\n')
            self.checkerror()

        if not self.error:
            self.push_item(context_id, "Process finished")
            gtk.main_iteration()
            self.ProgressBar.set_fraction(1.0)
            self.ProgressBar.set_text("Process finished")
            self.closeallowed(True)
            self.buildlock = False

        return

    # Open the about dialog box
    def about(self, widget):
        about.run()

    def help(self,widget):
        import webbrowser
        webbrowser.open('http://kcheck.sourceforge.net/pool/Documentation.pdf')

    # Check for program updates
    def updates(self, widget):
        kernelcheck_release, major, minor, revision = checkrelease()

        # Parse running version
        version = APPVERSION
        split = version.split('.')
        running_major = split[0]
        running_minor = split[1]
        running_revision = split[2]

        if major > running_major:
            print "Found new major."
            update = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, 'An update has been found. Do you wish to apply it? KernelCheck will be closed to apply the update.')
            update.connect("response", self.close3)
            update.run()
        elif minor > running_minor:
            print "Found new minor."
            update = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, 'An update has been found. Do you wish to apply it? KernelCheck will be closed to apply the update.')
            update.connect("response", self.close3)
            update.run()
        elif revision > running_revision:
            print "Found new revision."
            update = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, 'An update has been found. Do you wish to apply it? KernelCheck will be closed to apply the update.')
            update.connect("response", self.close3)
            update.run()
        else:
            os.chdir('/tmp/')
            os.system('wget http://kcheck.sourceforge.net/pool/patches/bugfix.list')
            b = open('/tmp/bugfix.list', 'r')
            f = open('/usr/lib/python2.5/site-packages/KernelCheck/library/fixed.list', 'r')
            buglist = []
            for line2 in b:
                f = open('/usr/lib/python2.5/site-packages/KernelCheck/library/fixed.list', 'r')
                for line1 in f:
                    if line1 != line2:
                        notfound = True
                    else:
                        notfound = False
                        break
                f.close()
                if notfound:
                    line2 = line2.split('\n')
                    buglist.append(line2[0])
            os.remove('/tmp/bugfix.list')

            if len(buglist) > 0:
                print "Found new bugfix."
                update = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, 'An update has been found. Do you wish to apply it? KernelCheck will be closed to apply the update.')
                update.connect("response", self.close4, buglist)
                update.run()
            else:
                update = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, 'No updates available.')
                update.connect("response", self.close5)
                update.run()

    # Response events for no updates
    def close5(self, w, res):
        if res == gtk.RESPONSE_CLOSE:
            w.hide()

    # Response events for bugfix
    def close4(self, w, res, buglist):
        if res == gtk.RESPONSE_YES:
            w.hide()
            gtk.main_iteration()
            for i in buglist:
                os.system('wget http://kcheck.sourceforge.net/pool/patches/fix-'+i)
                os.system('bash fix-'+i)
                os.remove('fix-'+i)
        elif res == gtk.RESPONSE_NO:
            w.hide()

    # Response events for version updates
    def close3(self, w, res):
        if res == gtk.RESPONSE_YES:
            w.hide()
            gtk.main_iteration()
            os.chdir('/tmp')
            os.system('wget http://kcheck.sourceforge.net/pool/patches/updater.sh')
            os.system('bash updater.sh &')
        elif res == gtk.RESPONSE_NO:
            w.hide()

    # Response events for destroy_window
    def close2(self, w, res):
        if res == gtk.RESPONSE_YES:
            self.run_command_done_callback(self.Terminal)
            self.error = True
            gtk.main_quit()
        elif res == gtk.RESPONSE_NO:
            w.hide()

    # Destroy the window
    def destroy_window(self, widget):
        if self.buildlock == True:
            error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_YES_NO, 'The kernel building lock is engaged. Are you sure you want to quit?')
            error.connect("response", self.close2)
            error.run()
        else:
            self.run_command_done_callback(self.Terminal)
            self.error = True
            gtk.main_quit()

def start():
    window = KernelCheck()
    gtk.main()
