# -*- coding: utf-8 -*-

# burnlib/burn.py
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>.
# Copyright © 2003–2009 Gaetano Paolone <bigpaul@hacknight.org>.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.

import os
import os.path
import sys
import optparse
import re
import statvfs
import mad
import ao
import ogg.vorbis
import gettext
import pwd
import fnmatch
import shlex
import subprocess

import burnlib.version
import console
import configure
from configure import config
import audio


gettext.bindtextdomain('burn', '/usr/share/locale/it/LC_MESSAGES/')
gettext.textdomain('burn')
_ = gettext.gettext


class ContentMode(object):
    """ Modes for content handling. """

    (data, iso, copy, audio) = (object() for n in range(4))

    titles = {
        audio: _('Audio-CD'),
        data: _('Data-CD'),
        copy: _('Copy-CD'),
        iso: _('Iso-CD'),
        }


def du(dirname, path_du, follow_symlink=False):
    #is like du. goes through dirname
    #and subdirs and append every file size to path_du
    """Goes deeply through path in order to calculate path's disk usage."""
    for root, dirs, files in os.walk(dirname):
        for file_name in files:
            if os.path.exists(os.path.realpath(os.path.join(root, file_name))):
                path_du += os.path.getsize(os.path.join(root, file_name))
    if follow_symlink:
        for directory in dirs:
            print os.path.join(root, directory)
            #os.walk does not follow symlink directories.
            #Next line will allow it.
            if os.path.islink(os.path.join(root, directory)):
                path_du += du(
                    os.path.realpath(os.path.join(root, directory)), path_du,
                    follow_symlink)
    return path_du


def check_main_option(opt):
    """Checks first argument."""
    if opt not in [
        "-D", "--data-cd",
        "-I", "--iso-cd",
        "-C", "--copy-cd",
        "-A", "--audio-cd",
        ]:
        print _(
            'Invalid syntax. First argument should be a main mode.'
            ' See \'burn -h\' for more info.')
        sys.exit()


def check_media_empty():
    """ Return True if media device is empty. """
    command_args = [
        config.get('executables', 'cdrdao'), "disk-info",
        "--device", config.get('CD-writer', 'device'),
        "--driver", config.get('CD-writer', 'driver'),
        ]
    command_process = subprocess.Popen(
        command_args, close_fds=True,
        stdout=subprocess.PIPE, stderr=open(os.devnull))
    for line in command_process.stdout:
        if line.startswith('CD-R empty'):
            if line.split(':')[1].strip() == 'yes':
                return True
            return False
    return False


def err(why):
    """Prints an error using why as argument."""
    print _('Error. '), why


def err_nf(dir_file):
    """Not found error message."""
    print _('Error. '), dir_file, _(' not found.')


def get_list_from_file(path):
    """extract a list of paths from a file"""
    in_file = open(path)
    in_file_lines = [
        path for path in (
            line.strip() for line in in_file)
        if os.path.isfile(path)]
    return in_file_lines


def get_media_capacity():
    """ Get total capacity of media device. """
    command_args = [
        config.get('executables', 'cdrdao'), "disk-info",
        "--device", config.get('CD-writer', 'device'),
        "--driver", config.get('CD-writer', 'driver'),
        ]
    command_process = subprocess.Popen(
        command_args, close_fds=True,
        stdout=subprocess.PIPE, stderr=open(os.devnull))
    for line in command_process.stdout:
        if line.startswith('Total Capacity'):
            if line.split(':')[1].strip() == 'n/a':
                return None
            return line.split()[6].split('/')[0]
    return None


def prog_intro(mode=None):
    """ Output program introduction message for specified mode. """

    if config.getboolean('general', 'ask_root'):
        if not pwd.getpwuid(os.geteuid())[0] == "root":
            if not console.ask_yesno(_(
                'You are not superuser (root).'
                ' Do you still want to continue'), True):
                sys.exit()
    print _(
        'Burn v.%(version)s  '
        'Written by %(author_name)s.') % vars(burnlib.version)
    print _('Burn until recorded, now!')
    print _(
        'This software comes with absolutely no warranty!'
        ' Use at your own risk!')
    print _('Burn is free software.')
    print _('See software updates at <URL:%(_url)s>.') % vars(burnlib)
    print

    mode_title = ContentMode.titles.get(mode)
    if mode_title is not None:
        print mode_title + "..."
        print


def show_examples(option, opt, value, parser):
    """Show examples for quick startup"""

    print "# burn -D -p /etc/"
    print _(
        '   Creates a CD/DVD with /etc/ contents. (you will find files'
        ' and directories contained in /etc in CD\'s root)')
    print "# burn -D -p /home/bigpaul/video/summer_2003/spain.tar.gz"
    print _('   Creates a CD/DVD with spain.tar.gz in CD\'s root')
    print "# burn -D -r /etc/"
    print _(
        '   Creates a CD/DVD containing the whole /etc/ directory.'
        ' (-r preserves path)')
    print "# burn -D -c /mail_2003 /home/bigpaul/Mail -p /boot/vmli*"
    print _(
        '   Creates a CD/DVD containing the whole /home/bigpaul/Mail'
        ' renamed into /mail_2003. (-c changes path name).'
        ' This command also adds in CD\'s root every vmli* file'
        ' in /boot/ directory')
    print "# burn -I -n image.iso"
    print _('   Burns image.iso')
    print "# burn -C"
    print _('   Copy CDs (disk at once).')
    print "# burn -A -a *.wav"
    print _('   Creates an Audio CD. Tracks come from wav files')
    print "# burn -A -a *.mp3"
    print _('   Creates an Audio CD. Tracks come from mp3 files')
    print "# burn -A -a *.ogg"
    print _('   Creates an Audio CD. Tracks come from Ogg Vorbis files')
    print "# burn -A -a *.mp3 file.ogg track01.wav"
    print _('   Creates an Audio CD. Tracks come from .wav, .ogg, .mp3 files')

    sys.exit()


def varargs(option, opt, value, parser):
    """Callback function to manage multiple arguments (or shell expansion)"""
    assert value is None
    step = 0
    value = []
    rargs = parser.rargs
    while rargs:
        step = step + 1
        arg = rargs[0]
        if ((arg[:2] == "--" and len(arg) > 2) or
            (arg[:1] == "-" and len(arg) > 1 and arg[1] != "-")):
            if step == 1:
                print _(
                    '%(option)s is an option that takes one or more arguments.'
                    ' So you can\'t put %(arg)s after it') % vars()
                sys.exit()
            else:
                break
        else:
            value.append(arg)
            del rargs[0]
    setattr(parser.values, option.dest, value)


class ISO:
    "ISO class"

    def __init__(self):
        """ Set up a new instance. """
        self.path_o = []
        self.genisoimage_args = []
        self.windows = config.getboolean('ISO', 'windows_read')
        self.tempdir = config.get('ISO', 'tempdir')
        self.image_name = config.get('ISO', 'image')
        self.mount_dir = config.get('ISO', 'mount_dir')
        self.dest = os.path.normpath(self.tempdir + self.image_name)

    def create(self):
        """ Execute data track recording command. """
        print _('Creating temporary image: '), self.dest
        pbar = console.ProgressBar(width=30)
        command_process = subprocess.Popen(
            self.genisoimage_args, close_fds=True,
            stdin=subprocess.PIPE,
            stdout=open(os.devnull), stderr=subprocess.PIPE)
        progress = 0
        for line in command_process.stderr:
            if "done, estimate finish" in line:
                progress = int(float(line.split()[0][:-1]))
                pbar.amount = progress
                pbar.update_display()
        pbar.amount = 100
        pbar.update_display()

    def destroy(self):
        """remove the file"""
        os.remove(self.dest)

    def ask_mount(self, image):
        """asks if user wants to mount image"""
        if console.ask_yesno(_(
            'Do you want to see image\'s contents before proceeding'
            ), True):
            self.mount(image)

    def freespace(self):
        """return free disk space"""
        space = os.statvfs(self.tempdir)
        return (long(space[statvfs.F_BAVAIL]) * \
            long(space[statvfs.F_BSIZE]))/1048576

    def mount(self, image):
        """mount image in self.mount_dir"""
        mount_dir = self.mount_dir
        if os.path.exists(mount_dir) and os.path.isdir(mount_dir):
            command_args = ["mount", "-o", "loop", image, mount_dir]
            if subprocess.call(command_args):
                print _(
                    'Unable to mount %(image)s. Please check if you have'
                    ' permissions to mount it on %(mount_dir)s') % vars()
                sys.exit()
            self.ask_after_mount(self.mount_dir)
        else:
            err(self.mount_dir + _(' is not valid as a mount point'))
            sys.exit()
        command_args = ["umount", self.mount_dir]
        subprocess.call(command_args)

    def ask_after_mount(self, dirname):
        """Choose what to do with the mounted image..."""
        prompt = _(
            '\n\nPlease choose:\n\n'
            '1. Print every file with path\n'
            '2. Print directory tree structure\n'
            '3. Ok, finished... Let\'s burn\n'
            '> ')
        mount_choice = raw_input(prompt)
        if mount_choice in ('1'): #option num. 1 ---> every file
            print
            for root, dirs, files in os.walk(dirname):
                for file_path in files:
                    print os.path.join(root, file_path)
            self.ask_after_mount(dirname) #return True
        if mount_choice in ('2'): #option num. 2 ---> tree structure
            print
            for root, dirs, files in os.walk(dirname):
                for directory in dirs:
                    print os.path.join(root, directory)
            self.ask_after_mount(dirname)
        if mount_choice in ('3'): #option num. 3 ---> done
            return True

    def ask_multisession(self):
        """Asks if user wants to add stuff to a multisession CD or if he wants
        to create a new multisession CD from scratch."""
        prompt = _(
            '\n\nPlease choose:\n\n'
            '1. Create new multisession CD from a blank media\n'
            '2. Append data to an existant multisession CD\n'
            '> ')
        multisession_cd = raw_input(prompt)
        if multisession_cd in ('1'): #option num. 1 new multisession
            return 1
        if multisession_cd in ('2'): #option num. 2 already multisession
            return 2

    def ask_remove(self):
        """asks to remove image"""
        print
        print self.dest, _(' is the image file created...')
        if console.ask_yesno(_('Do you want me to remove it'), False):
            print _('Removing '), self.dest, "..."
            os.remove(self.dest)
            return True
        else:
            return False

    def first_ask_remove(self):
        """asks to remove image at the very beginning"""
        print
        print _(
            'Warning. there is already a temporary image file'
            ' named %(dest)s.') % vars(self)
        if console.ask_yesno(_('Do you want me to remove it'), False):
            print _('Removing '), self.dest, "..."
            os.remove(self.dest)
            return True
        else:
            return False


class CDROM:
    "CDROM class"

    def __init__(self, options):
        """ Set up a new instance. """
        self.wodim_args = []
        self.wodim = config.get('executables', 'wodim')
        self.cdrdao = config.get('executables', 'cdrdao')
        self.speed = config.getint('CD-writer', 'speed')
        self.device = config.get('CD-writer', 'device')
        self.source_device = config.get('CD-reader', 'device')
        self.driver = config.get('CD-writer', 'driver')
        self.source_driver = config.get('CD-reader', 'driver')
        self.burnfree = config.getboolean('CD-writer', 'burnfree')

        self.content_mode = options.mode
        self.multisession = options.multisession
        self.simulate = options.simulate
        self.eject = options.eject

        self.iso = ISO()

    def compute_media_size(self):
        """ Get the storage capacity of the media. """
        if config.getboolean('Media', 'media-check'):
            empty = check_media_empty()
            if not empty:
                if not self.multisession:
                    print _('Error. Please insert a blank CD/DVD.')
                    command_args = [
                        self.wodim, "-eject",
                        "dev=%(device)s" % vars(self)]
                    subprocess.call(command_args, stderr=open(os.devnull))
                    sys.exit()

            self.size = get_media_capacity()
            if not self.size:
                print _(
                    "Error. unknown media capacity. "
                    "Using configuration default.")
                self.size = config.getint('Media', 'size')
        else:
            self.size = config.getint('Media', 'size')

    def size_compare(self, tobeburned, space_needed):
        """Checks free space for temporary files and CD oversize"""
        free_disk_space = int(self.iso.freespace())
        self.compute_media_size()
        print
        print _('To be burned: '), "\t\t\t", tobeburned / 1048576, "Mb"
        print _('Disk space needed: '), "\t\t", space_needed/1048576, "Mb"
        print _('Media capacity: '), "\t\t", self.size, "Mb"
        if self.content_mode is not ContentMode.iso:
            print _('Free disk space: '), "\t\t", free_disk_space, "Mb"
        if space_needed == 0:
            space_needed = tobeburned
        if self.content_mode is not ContentMode.iso:
            if (space_needed/1048576) > free_disk_space:
                if self.content_mode is ContentMode.data:
                    print _('You do not have enough free disk space'), \
                        " (", free_disk_space, " Mb )", \
                        _('to create temporary image file '), \
                        "( ", tobeburned / 1048576, " Mb )"
                elif self.content_mode is ContentMode.audio:
                    print _('You do not have enough free disk space'), \
                        " (", free_disk_space, " Mb )", \
                        _('to create temporary audio files '), \
                        "( ", tobeburned / 1048576, " Mb )"
                sys.exit()
        if (tobeburned / 1048576) > int(self.size):
            if not console.ask_yesno(_(
                'It seems you are going to burn more than media\'s capacity.\n'
                'Do you still want to continue'), False):
                sys.exit()
        return True

    def make_command_args(self):
        """ Generate command-line arguments for track recording. """
        self.wodim_args = [self.wodim, "-v", "-pad"]
        if self.simulate:
            self.wodim_args.append("-dummy")
        if self.eject:
            self.wodim_args.append("-eject")
        if self.speed:
            self.wodim_args.append("speed=%(speed)s" % vars(self))
        else:
            print _('no burning speed defined, using 2x')
            self.wodim_args.append("speed=2")
        if self.device:
            self.wodim_args.append("dev=%(device)s" % vars(self))
        else:
            print _('no device specified.')
            sys.exit()
        if self.burnfree:
            self.wodim_args.append("driveropts=burnfree")
        if self.multisession:
            self.wodim_args.append("-multi")
        if self.content_mode in [ContentMode.data, ContentMode.iso]:
            self.wodim_args.extend(["-data", self.iso.dest])

    def create(self):
        """ Execute track recording command. """
        print
        if config.getboolean('general', 'pause'):
            print _('Press a key to begin recording...')
            console.getch()
        print _('Please wait...')
        subprocess.call(self.wodim_args)

    def double_dao_create(self, command_args):
        """ Execute disk-at-once copy with two drives (reader and writer). """
        print
        print _('Place the source CD in the CD drive')
        print _('and place a blank media in the recording unit.')
        print _('Press a key to begin on-the-fly copy')
        console.getch()
        subprocess.call(command_args)

    def single_dao_create(self, command_args):
        """ Execute disk-at-once copy with one drive. """
        print
        print _('Place source CD in the recording unit.')
        print _('Press a key to begin reading...')
        console.getch()
        subprocess.call(command_args)

    def another_copy(self):
        """burn image untill user says no"""
        while console.ask_yesno(_(
            'Do you want to use this image to make another copy now?'
            ), False):
            self.make_command_args()
            self.create()


def main():
    """ Program mainline procedure. """

    usage = """%prog -MODE [general_option] [mode_option] ...

For quick start you can get common examples with:

burn -e
"""
    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        "-e", "--examples", action="callback", callback=show_examples,
        dest="examples",
        help=_('show examples for quick startup'))

    #Modes
    mode_options = optparse.OptionGroup(
        parser, _('Main burn MODES'),
        _('They _have_ to be the first argument after program name'))
    mode_options.add_option(
        "-D", "--data-cd",
        action="store_const", dest="mode", const=ContentMode.data,
        help=_('creates a Data CD/DVD.'))
    mode_options.add_option(
        "-I", "--iso-cd",
        action="store_const", dest="mode", const=ContentMode.iso,
        help=_('creates a CD/DVD from ISO.'))
    mode_options.add_option(
        "-C", "--copy-cd",
        action="store_const", dest="mode", const=ContentMode.copy,
        help=_('copy CD/DVD.'))
    mode_options.add_option(
        "-A", "--audio-cd",
        action="store_const", dest="mode", const=ContentMode.audio,
        help=_('creates an Audio CD from .wav, .mp3 and .ogg files.'))

    #General options
    general_option = optparse.OptionGroup(
        parser, "General options",
        _(
            'These options could be used for every burn mode'
            ' unless stated otherwise'))

    general_option.add_option(
        "-s", "--simulate", action="store_true", dest="simulate",
        help=_('This option will perform a burn simulation.'))
    general_option.add_option(
        "-j", "--eject", action="store_true", dest="eject",
        help=_(
            'This option will eject disk when burn process is over.'))
    general_option.add_option(
        "--dao", action="store_true", dest="dao",
        help=_(
            'Enable disk at once. Enabling this option, you will not have'
            ' 2 seconds gap between tracks.'))

    #DATA-CD Options
    data_cd = optparse.OptionGroup(parser, _('Data CD Mode (-D) options'),
        _('Data CD: adds files and directories.'))
    data_cd.add_option(
        "-p", "--path",
        action="callback", callback=varargs, dest="path",
        help=_(
            'add file/s or path\'s content to CD-ROM/DVD\'s root.'
            ' e.g.: -p /cvs/myproj/ <return>. In this example we will find'
            ' CD-ROM/DVD\'s root filled with /cvs/myproj/ contents, but'
            ' no /cvs/myproj/ will be created.'))
    data_cd.add_option(
        "-r", "--preserve-path",
        action="callback", callback=varargs, dest="preserve_path",
        help=_(
            'add file/s or path\'s content to CD-ROM/DVD preserving'
            ' original path. e.g.: -r /cvs/myproj/ <return>. In this'
            ' example we will find /cvs/myproj/ in CD-ROM/DVD\'s root.'))
    data_cd.add_option(
        "-x", "--exclude-path",
        #action="append", type="string", dest="exclude_path",
        action="callback", callback=varargs, dest="exclude_path",
        help=_(
            'every file or directory matching this string'
            ' will not be included.'))
    data_cd.add_option(
        "-c", "--change-path", action="append",
        nargs=2, type="string", dest="change_path",
        help=_(
            'usage: -c <new_path> <old_path>. With this option,'
            ' old_path will be named new_path in CD-ROM/DVD.'
            ' e.g.: -c /my_home/2004_Jan/ /home/bigpaul/ <return>.'
            ' Thus /home/bigpaul/ will be named  /my_home/2004_Jan/'
            ' in CD-ROM/DVD.'))
    data_cd.add_option(
        "-l", "--follow-symlink", action="store_true", dest="follow_symlink",
        help=_('this option allows burn to follow symbolic link directories'))
    data_cd.add_option(
        "-m", "--multisession", action="store_true", dest="multisession",
        help=_('this option allows multisession CDs'))

    #ISO-CD Options
    iso_cd = optparse.OptionGroup(parser, "ISO CD Mode (-I) options",
        _('Creates a CD-ROM/DVD from an existing image.'))

    iso_cd.add_option(
        "-n", "--name", action="store", type="string", dest="iso_name",
        help=_('image name'))

    #COPY-CD Options
    copy_cd = optparse.OptionGroup(
        parser, _('Copy CD Mode (-C) options'),
        _(
            'If you have both a reader and a recording unit'
            ' you can perform a copy on-the-fly. You can also copy a CD'
            ' even if you only have the recording unit.'))

    #AUDIO-CD Options
    audio_cd = optparse.OptionGroup(
        parser, _('Audio CD Mode (-A) options'),
        _(
            'Audio CD is used to create an audio CD-ROM'
            ' from .wav, .ogg and .mp3 files. You can can use -a option'
            ' to perform an Audio CD from different source audio files.'))
    audio_cd.add_option(
        "-a", "--audio-file",
        action="callback", callback=varargs, dest="general_audio_file_list",
        help=_(
            '.wav, .mp3, .ogg file/s. Files must have extensions'
            ' (no matter if they are upper or lowercase).'))
    audio_cd.add_option(
        "--audio-list",
        action="store", type="string", dest="file_list",
        help=_('m3u playlist or file with one audio file per line.'))
    audio_cd.add_option(
        "--clear-audiotemp",
        action="store_true", dest="clear_audio_temp",
        help=_('remove temporary audio files.'))
    audio_cd.add_option(
        "--no-gaps", action="store_true", dest="nogaps",
        help=_(
            'Enable disk at once. Enabling this option, you will not have'
            ' 2 seconds gap between tracks.'))

    parser.add_option_group(mode_options)
    parser.add_option_group(general_option)
    parser.add_option_group(data_cd)
    parser.add_option_group(iso_cd)
    parser.add_option_group(copy_cd)
    parser.add_option_group(audio_cd)
    (options, args) = parser.parse_args()

    if len(sys.argv) > 1:
        check_main_option(sys.argv[1])
    else:
        prog_intro()
        parser.print_help()
        sys.exit()

    configure.read_from_files()

    prog_intro(options.mode)
    cdrom = CDROM(options)

    if options.mode is ContentMode.data:
        print _('Checking files, directories and disk usage. Please wait...')
        print
        path = ''
        path_preserved = ''
        path_changed = ''
        paths_excluded = []
        size = 0
        first_time_multisession = 0

        if options.path:
            for directory in options.path:
                if os.path.exists(directory):
                    abspath = os.path.abspath(directory)
                    path = path + '\'' + abspath + '\'' + ' '
                    if os.path.isfile(abspath):
                        size = size + os.path.getsize(abspath)
                    elif os.path.isdir(abspath):
                        size = size + du(abspath, 0, options.follow_symlink)
                    else:
                        err(abspath + _(': no such file or directory.'))
                else:
                    err_nf(directory)
        if options.preserve_path:
            for directory in options.preserve_path:
                if os.path.exists(directory):
                    abspath = os.path.abspath(directory)
                    if os.path.isdir(abspath):
                        size = size + du(abspath, 0, options.follow_symlink)
                    elif os.path.isfile(abspath):
                        size = size + os.path.getsize(abspath)
                    else:

                        err(abspath + _(': no such file or directory.'))
                        sys.exit()
                    path_preserved = path_preserved \
                        + '\'' + abspath + '\'' + '=' \
                        + '\'' + abspath + '\'' + ' '
                else:
                    err_nf(directory)
        if options.change_path:
            for (new_path, old_path) in options.change_path:
                if os.path.exists(old_path):
                    abspath = os.path.abspath(old_path)
                    if os.path.isfile(abspath):
                        size += os.path.getsize(abspath)
                    elif os.path.isdir(abspath):
                        size += du(abspath, 0, options.follow_symlink)
                    else:
                        err(abspath + _(': no such file or directory.'))
                        sys.exit()
                    path_changed = path_changed \
                        + '\'' + new_path + '\'' + '=' \
                        + '\'' + abspath + '\'' + ' '
                else:
                    err_nf(old_path)
                    print _(
                        'nothing will be done for %(old_path)s -> %(new_path)s'
                        ) % vars()
        if options.exclude_path:
            testsize = size
            for directory in options.path:
                if os.path.isdir(directory):
                    for exclude_path in options.exclude_path:
                        for root, dirs, files in os.walk(directory):
                            for file_name in files:
                                if fnmatch.fnmatch(file_name, exclude_path):
                                    if os.path.exists(
                                        os.path.join(root, file_name)):
                                        if os.path.isfile(
                                            os.path.join(root, file_name)):
                                            size = size - os.path.getsize(
                                                os.path.join(root, file_name))
                                            paths_excluded.append(
                                                os.path.join(root, file_name))
                            for subdir in dirs:
                                if fnmatch.fnmatch(subdir, exclude_path):
                                    if os.path.exists(
                                        os.path.join(root, subdir)):
                                        size = size - du(
                                            os.path.join(root, subdir), 0,
                                            options.follow_symlink)
                                        paths_excluded.append(
                                            os.path.join(root, subdir))
            print
            print _('Size without exclusions: '), "\t", testsize/1048576, "Mb"

        global_path = path + path_preserved + path_changed
        if global_path == '':
            err(_('Nothing to be burned...'))
            sys.exit()
        cdrom.size_compare(size, size)

        cdrom.iso.genisoimage_args.extend(
            [config.get('executables', 'genisoimage'), "-R"])
        if os.path.exists(cdrom.iso.tempdir):
            cdrom.iso.genisoimage_args.extend(["-o", cdrom.iso.dest])
        else:
            err(_('Error: ') + cdrom.iso.tempdir + _(' does not exist'))
            sys.exit()

        if cdrom.iso.windows:
            cdrom.iso.genisoimage_args.extend(["-J", "-joliet-long"])

        for path_excluded in paths_excluded:
            cdrom.iso.genisoimage_args.extend(["-x", path_excluded])

        if options.multisession:
            multisession_choose = cdrom.iso.ask_multisession()
            if multisession_choose == 2:
                #ciao
                print _(
                    'Place target CD in CD/DVD writer unit and press a key...')
                console.getch()
                print _('Please wait...')
                command_args = [
                    config.get('executables', 'wodim'), "-msinfo",
                    "dev=%(device)s" % vars(cdrom)]
                command_process = subprocess.Popen(
                    command_args,
                    stdout=subprocess.PIPE, stderr=open(os.devnull))
                msinfo = command_process.communicate()[0]
                cdrom.iso.genisoimage_args.extend(
                    ["-C", msinfo, "-M", cdrom.device])
            elif not multisession_choose == 1:
                sys.exit()
            else:
                first_time_multisession = 1
        cdrom.iso.genisoimage_args.extend(["-graft-points", global_path])
        cdrom.make_command_args()
        if os.path.exists(cdrom.iso.dest):
            if not cdrom.iso.first_ask_remove():
                cdrom.another_copy()
                sys.exit()
        cdrom.iso.create()
        if first_time_multisession == 1:
            cdrom.iso.ask_mount(cdrom.iso.dest)
        cdrom.create()
        if os.path.exists(cdrom.iso.dest):
            if not cdrom.iso.ask_remove():
                cdrom.another_copy()
        sys.exit()

    if options.mode is ContentMode.iso:
        if os.path.exists(options.iso_name):
            if cdrom.size_compare(os.path.getsize(options.iso_name), 0):
                print
                cdrom.iso.dest = options.iso_name
                cdrom.iso.ask_mount(options.iso_name)
                cdrom.make_command_args()
                cdrom.create()
                if os.path.exists(cdrom.iso.dest):
                    if not cdrom.iso.ask_remove():
                        cdrom.another_copy()
            else:
                sys.exit()
        else:
            err_nf(options.iso_name)
            sys.exit()
        sys.exit()

    if options.mode is ContentMode.copy:
        cdrom.compute_media_size()
        single_drive_mode = 0
        if cdrom.device == cdrom.source_device or cdrom.source_device == '':
            single_drive_mode = 1
            #print single_drive_mode
        cdrdao_args = [config.get('executables', 'cdrdao')]

        if single_drive_mode == 1:
            cdrdao_args.append("copy")
            if options.simulate:
                cdrdao_args.append("--simulate")
            if options.eject:
                cdrdao_args.append("--eject")
            cdrdao_args.extend(["--datafile", cdrom.iso.dest])
            cdrdao_args.extend(["--device", cdrom.device])
            if not cdrom.driver == '':
                cdrdao_args.extend(["--driver", cdrom.driver])
            cdrdao_args.extend(["--speed", str(cdrom.speed)])
            cdrdao_args.append("--fast-toc")
            cdrom.single_dao_create(cdrdao_args)
        else:
            cdrdao_args.append("copy")
            if options.simulate:
                cdrdao_args.append("--simulate")
            if options.eject:
                cdrdao_args.append("--eject")
            cdrdao_args.extend(["--device", cdrom.device])
            if not cdrom.driver == '':
                cdrdao_args.extend(["--driver", cdrom.driver])
            cdrdao_args.extend(["--source-device", cdrom.source_device])
            if not cdrom.source_driver == '':
                cdrdao_args.extend(["--source-driver", cdrom.source_driver])
            cdrdao_args.extend(["--speed", str(cdrom.speed)])
            cdrdao_args.append("--on-the-fly")
            cdrdao_args.append("--fast-toc")
            cdrom.double_dao_create(cdrdao_args)
        sys.exit()

    if options.mode is ContentMode.audio:
        print _('Audio file processing. Please wait...')
        print
        audio_list = []
        to_be_removed = []
        old_temp_wavs = []
        file_list = []
        track_type = ''
        size = 0
        track_number = 0
        track_number2 = 0
        mp3_ogg_size = 0
        counter = 1000
        total_audio_time = 0

        #61196 wav header????
        #176400 kb 1 wav second comes from:
        #44100 * 16 * 2bit / 8 = byte

        list_dir = os.listdir(cdrom.iso.tempdir)

        if options.clear_audio_temp:
            for file_path in list_dir:
                if re.compile("^burn_1").search(file_path[:5], 0):
                    old_temp_wavs.append(
                        os.path.normpath(cdrom.iso.tempdir + file_path))
            if old_temp_wavs:
                print
                for old_wavs in old_temp_wavs:
                    print _('removing '), old_wavs, "..."
                    os.remove(old_wavs)
        if options.general_audio_file_list:
            file_list = options.general_audio_file_list

        if options.file_list:
            file_list.extend(get_list_from_file(options.file_list))

        for file_path in file_list:
            base, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext == '.ogg' or ext == '.mp3':
                mp3_ogg_size += (
                    audio.file_duration(file_path) * 176400)
            if ext == '.wav':
                size += os.path.getsize(file_path)
            if ext != '.ogg' and ext != '.mp3' and ext != '.wav':
                print file_path, _(': not a regular audio file. Skipped')

        cdrom.size_compare((size+mp3_ogg_size), mp3_ogg_size)
        print

        list_dir = os.listdir(cdrom.iso.tempdir)
        old_temp_wavs = []
        for file_path in list_dir:
            if re.compile("^burn_1").search(file_path[:5], 0):
                old_temp_wavs.append(
                    os.path.normpath(cdrom.iso.tempdir + file_path))
        if old_temp_wavs:
            print
            for wav_path in old_temp_wavs:
                print wav_path
            if console.ask_yesno(_(
                'You have old burn audio files in temporary directory.'
                ' Remove these files and continue'
                ), False):
                for oldwavs in old_temp_wavs:
                    print _('removing '), oldwavs, "..."
                    os.remove(oldwavs)
            else:
                sys.exit()
        print
        print "---------------------------------------------"
        print "Burn - " + _('Track summary')
        print "---------------------------------------------"
        for file_path in file_list:
            track_number = track_number + 1
            base, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext == '.mp3' or ext == '.ogg':
                if os.path.exists(file_path):
                    abspath = os.path.abspath(file_path)
                    if os.path.isfile(abspath):
                        info = audio.FileInfo(abspath)
                        if info.title:
                            print track_number, ")\t", \
                                info.duration, "-", info.title
                        else:
                            print track_number, ")\t", \
                                info.duration, "-", os.path.abspath(file_path)
                        total_audio_time += info.total_time
            else:
                print track_number, ")\t", audio.compute_duration(
                    os.path.getsize(os.path.abspath(file_path)) / 176400), \
                    "-", os.path.abspath(file_path)
                total_audio_time += os.path.getsize(
                    os.path.abspath(file_path)) / 176400
        # print "Total audio time: ", int(total_audio_time)
        print
        print _('Total Audio-CD: '), audio.compute_duration(
            int(total_audio_time))
        print
        if config.getboolean('general', 'external_decoding'):
            print _('Performing audio decoding with external decoder.')
            ogg_decoder = config.get('executables', 'ogg_decoder')
            mp3_decoder = config.get('executables', 'mp3_decoder')
            ogg_decoder_option = config.get(
                'executables', 'ogg_decoder_option')
            mp3_decoder_option = config.get(
                'executables', 'mp3_decoder_option')
        else:
            print _('Performing audio decoding with burn\'s native functions.')
        for file_path in file_list:
            track_number2 = track_number2 + 1
            base, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext == '.mp3' or ext == '.ogg':
                counter = counter + 1
                if ext == '.mp3':
                    track_type = 'MP3'
                else:
                    track_type = 'OGG'
                if os.path.exists(file_path):
                    abspath = os.path.abspath(file_path)
                    if os.path.isfile(abspath):
                        #Shows full path ogg files
                        print _(
                            "[%(track_number2)d/%(track_number)d]"
                            " %(track_type)s\tProcessing %(abspath)s") % vars()
                        info = audio.FileInfo(abspath)
                        #Shows ID3 TAGS
                        #print "\t\tTitle: \t\t",info.title
                        #print "\t\tAlbum: \t\t",info.album
                        #print "\t\tArtist: \t",info.artist
                        #Convert mp3/ogg file in tempdir/file.[mp3|ogg].wav
                    if ext == '.mp3':
                        if config.getboolean('general', 'external_decoding'):
                            wav_name = "burn_%(counter)d.wav" % vars()
                            wav_path = os.path.normpath(os.path.join(
                                cdrom.iso.tempdir, wav_name))
                            command_args = [mp3_decoder]
                            command_args.extend(
                                shlex.split(mp3_decoder_option))
                            command_args.extend([wav_path, abspath])
                            subprocess.call(command_args)
                        else:
                            dev = ao.AudioDevice(
                                'wav', filename=(
                                    os.path.normpath(
                                        cdrom.iso.tempdir
                                        + 'burn_' + repr(counter))
                                    + '.wav'),
                                overwrite=True)
                            pbar = console.ProgressBar(width=30)
                            audio_buffer = mad.MadFile(abspath)
                            old_progress = 0
                            while True:
                                buf = audio_buffer.read()
                                if buf is None:
                                    break
                                progress = \
                                    audio_buffer.current_time() * 100 / \
                                        audio_buffer.total_time()
                                if progress > old_progress:
                                    pbar.amount = progress
                                    pbar.update_display()
                                old_progress = progress
                                dev.play(buf, len(buf))
                        audio_list.append(os.path.normpath(
                            cdrom.iso.tempdir
                            + 'burn_' + repr(counter)) + '.wav')
                        to_be_removed.append(os.path.normpath(
                            cdrom.iso.tempdir
                            + 'burn_' + repr(counter)) + '.wav')
                    elif ext == '.ogg':
                        size = 4096
                        if config.getboolean('general', 'external_decoding'):
                            wav_name = "burn_%(counter)d.wav" % vars()
                            wav_path = os.path.normpath(os.path.join(
                                cdrom.iso.tempdir, wav_name))
                            command_args = [ogg_decoder]
                            command_args.extend(
                                shlex.split(ogg_decoder_option))
                            command_args.extend([wav_path, abspath])
                            subprocess.call(command_args)
                        else:
                            dev = ao.AudioDevice(
                                'wav', filename=os.path.normpath(
                                    cdrom.iso.tempdir
                                    + 'burn_' + repr(counter))
                                + '.wav',
                                overwrite=True)
                            pbar = console.ProgressBar(width=30)
                            audiofile = ogg.vorbis.VorbisFile(abspath)
                            old_progress = 0
                            while True:
                                (buf, bytes, bit) = audiofile.read(size)
                                if bytes == 0:
                                    break
                                progress = \
                                    audiofile.time_tell() * 100 / \
                                        audiofile.time_total(-1)
                                if progress > old_progress:
                                    pbar.amount = progress
                                    pbar.update_display()
                                old_progress = progress
                                dev.play(buf, bytes)

                        audio_list.append(os.path.normpath(
                            cdrom.iso.tempdir
                            + 'burn_' + repr(counter)) +'.wav')
                        to_be_removed.append(os.path.normpath(
                            cdrom.iso.tempdir
                            + 'burn_' + repr(counter)) +'.wav')
                    else:
                        err(abspath + _(': not a valid audio file.'))

            if ext == '.wav':
                track_type = 'WAV'
                if os.path.exists(file_path):
                    abspath = os.path.abspath(file_path)
                    print _(
                        "[%(track_number2)d/%(track_number)d]"
                        " %(track_type)s\tProcessing %(abspath)s") % vars()
                    audio_list.append(abspath)

        cdrom.make_command_args()
        if options.nogaps:
            cdrom.wodim_args.append("-dao")
        cdrom.wodim_args.append("-audio")
        cdrom.wodim_args.extend(audio_list)

        #burning CD
        cdrom.create()
        if config.getboolean('general', 'pause'):
            while console.ask_yesno(_(
                'Do you want to use processed audio files to create'
                ' another Audio CD now'), False):
                cdrom.create()
        else:
            while console.ask_yesno(_(
                'Write another copy (insert a blank disc now)'),
                False):
                console.getch()
                cdrom.create()

        #removing temp audio files
        for file_path in to_be_removed:
            if os.path.exists(file_path):
                print _('removing '), file_path, "..."
                os.remove(file_path)

        sys.exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print
        print _('burn: exiting now...')


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
