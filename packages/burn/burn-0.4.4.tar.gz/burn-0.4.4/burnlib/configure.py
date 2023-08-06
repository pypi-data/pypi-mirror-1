# -*- coding: utf-8 -*-

# burnlib/configure.py
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>.
# Copyright © 2004 Gaetano Paolone <bigpaul@hacknight.org>.
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

import sys
import os
import os.path
import gettext
import ConfigParser
import pwd
import textwrap

import burnlib.version


template_file_name = 'burn.conf-dist'
template_directory = '/usr/share/burn'
target_conf_file_name = 'burn.conf.new'

#gettext
gettext.bindtextdomain('burn_configure', '/usr/share/locale/it/LC_MESSAGES/')
gettext.textdomain('burn_configure')
_ = gettext.gettext

yes = ('y', 'ye', 'yes', 'Y', 'YE', 'YES', 'Yes')
no = ('n', 'no', 'N', 'NO', 'No')


def ask_ok(prompt, complaint=_('Yes or no, please!')):
    """If invoked, returns true if user answer yes to the
        question and false if he answer no """
    while True:
        ok = raw_input(prompt)
        if ok in yes:
            return True
        if ok in no:
            return False
        print complaint


def ask_value(addictional_prompt, default):
    print
    return raw_input(
        '\t(' + addictional_prompt + ')\n'
        '\tCurrent/default: (' + default + ') --> ')


def prog_intro(path):
    print _(
        'Burn-configure v.%(version)s'
        + '  Written by %(author_name)s.') % vars(burnlib.version)
    print _(
        'This tool helps writing configuration file for'
        ' burn - Burn until recorded, now!')
    print _(
        'This software comes with absolutely no warranty!'
        ' Use at your own risk!')
    print _('Burn-configure is free software.')
    print _('See software updates at <URL:%(_url)s>.') % vars(burnlib)
    print
    print _('This utility will create: '), path
    print _('Place this file as ~/.burnrc or /etc/burn.conf .')
    print
    print
    if not pwd.getpwuid(os.geteuid())[0] == "root":
        print _('You are not superuser (root).')
        print _(
            'You can still go through this configuration process'
            ' but remember that you should be root (or have permissions'
            ' on programs and devices) in order to use burn.')
        if not ask_ok(_('Do you still want to continue? ')):
            sys.exit()


def main():
    """ Mainline routine for the burn-configure program. """

    target_conf_file_path = os.path.normpath(
        pwd.getpwuid(os.geteuid())[5] + '//' + target_conf_file_name)

    prog_intro(path=target_conf_file_path)

    if os.path.exists(target_conf_file_path):
        print
        if ask_ok(_(
            'Target configuration file ('
            + target_conf_file_path
            + ') already exists.  Do you want to remove this file? ')):
            print _(
                'Removing last configuration file created with burn-configure'
                '...')
            os.remove(target_conf_file_path)
        else:
            print _(
                'Exiting... Please remove or rename last configuration file: '
                '%(target_conf_file_path)s') % vars()
    conf_new = open(target_conf_file_path, 'w')

    #Getting values from template
    config = ConfigParser.ConfigParser()
    if not template_directory == '':
        template_file_path = os.path.normpath(
            template_directory + '/' + template_file_name)
    conf = open((template_file_path), 'r')
    config.readfp(conf)

    cs = config.sections()
    section = ''

    if 'general' in cs:
        section = 'general'
        options = config.options(section)
        if 'external_decoding' in options:
            print
            current = config.get(section, 'external_decoding')
            print _('Keep native audio decoding?')
            print _(
                '\tBurn is able to transform compressed audio files'
                ' (MP3, Ogg Vorbis) in WAV.')
            print _('\tChoose \'y\' if you want to keep native decoding. ')
            print _(
                '\tChoose \'n\' if you want to use external decoders'
                ' such as mpg321, ogg123, lame, etc.')
            print _(
                '\t(You will need further editing of burn configuration file)')
            while 1:
                xtrnl_dcdng = ask_value('yes/no', current)
                if xtrnl_dcdng == '':
                    break
                if xtrnl_dcdng in yes:
                    config.set(section, 'external_decoding', xtrnl_dcdng)
                    break
                if xtrnl_dcdng in no:
                    config.set(section, 'external_decoding', xtrnl_dcdng)
                    break
        if 'ask_root' in options:
            print
            current = config.get(section, 'ask_root')
            print _('Prompt user if he is not root?')
            print _('\tBurn can prompt the user if he is not root.')
            print _('\tChoose \'y\' if you want to keep burn prompting you. ')
            print _('\tChoose \'n\' if you don\'t want this question anymore.')
            print _(
                '\t(disable this option if your user has'
                ' permissions to write with cd-writer)')
            while 1:
                sk_rt = ask_value('yes/no', current)
                if sk_rt == '':
                    break
                if sk_rt in yes:
                    config.set(section, 'ask_root', sk_rt)
                    break
                if sk_rt in no:
                    config.set(section, 'ask_root', sk_rt)
                    break
    if 'ISO' in cs:
        section = 'ISO'
        options = config.options(section)
        if 'tempdir' in options:
            print
            current = config.get(section, 'tempdir')
            print _('Which is your temporary directory?')
            while 1:
                tmpdr = ask_value('path', current)
                if tmpdr == '':
                    break
                if os.path.exists(tmpdr) and os.path.isdir(tmpdr):
                    config.set(section, 'tempdir', tmpdr)
                    break
                else:
                    print tmpdr, _('invalid path... skipped.')
                    break
        if 'image' in options:
            print
            current = config.get(section, 'image')
            print _('Temporary ISO name?')
            while 1:
                mg = ask_value('filename', current)
                if mg == '':
                    break
                else:
                    config.set(section, 'image', mg)
                    break
        if 'windows_read' in options:
            print
            current = config.get(section, 'windows_read')
            print _('Enable Joliet?')
            print _(
                '\tYou should enable this option if you want'
                ' to use your CDs on a Windows system too.')
            while 1:
                wndws_rd = ask_value('yes/no', current)
                if wndws_rd == '':
                    break
                if wndws_rd in yes:
                    config.set(section, 'windows_read', wndws_rd)
                    break
                if wndws_rd in no:
                    config.set(section, 'windows_read', wndws_rd)
                    break
        if 'mount_dir' in options:
            print
            current = config.get(section, 'mount_dir')
            print _('Which is your preferred mount point?')
            print _('\tBurn allows you to see image contents.')
            print _('\tWhere do you want to mount the image?')
            while 1:
                tmpdr = ask_value('path', current)
                if tmpdr == '':
                    break
                if os.path.exists(tmpdr) and os.path.isdir(tmpdr):
                    config.set(section, 'mount_dir', tmpdr)
                    break
                else:
                    print tmpdr, _('invalid path... skipped.')
                    break
    if 'CD-writer' in cs:
        section = 'CD-writer'
        options = config.options(section)
        if 'device' in options:
            print
            current = config.get(section, 'device')
            print _('Which is the device of your CD-writer?')
            print _(
                '\tYou have to use this syntax:'
                ' SCSIBUS,TARGET,LUN. E.g.: 1,0,0')
            if os.path.exists('/proc/scsi/scsi'):
                print _('\tHere follows your system\'s SCSI devices:')
                scsi_file = open('/proc/scsi/scsi', 'r')
                for line in scsi_file.readlines():
                    print "\t", line
            while 1:
                tmpdr = ask_value('CD-writer device', current)
                if tmpdr == '':
                    break
                else:
                    config.set(section, 'device', tmpdr)
                    break
        if 'speed' in options:
            print
            current = config.get(section, 'speed')
            print _('At which speed do you want to burn?')
            print _('\tRemember: higher speed may lead to buffer underrun.')
            while 1:
                spd = ask_value('speed', current)
                if spd == '':
                    break
                else:
                    config.set(section, 'speed', spd)
                    break
        if 'driver' in options:
            print
            current = config.get(section, 'driver')
            print _('Does your CD-writer use a specific driver?')
            print _('\tPossible values are: ')
            values = [
                "tcdd2600", "plextor", "plextor-scan",
                "generic-mmc", "generic-mmc-raw",
                "ricoh-mp6200", "yamaha-cdr10x", "teac-cdr55",
                "sony-cdu920", "sony-cdu948", "taiyo-yuden", "toshiba",
                ]
            print textwrap.fill(
                ", ".join(values),
                initial_indent="\t\t", subsequent_indent="\t\t",
                break_long_words=False)

            while 1:
                drvr = ask_value('driver', current)
                if drvr == '':
                    break
                else:
                    config.set(section, 'driver', drvr)
                    break
        if 'burnfree' in options:
            print
            current = config.get(section, 'burnfree')
            print _(
                'Do you want to turn the support for'
                ' Buffer Underrun Free writing on?')
            print _(
                '\tThis only works for drives that support'
                ' Buffer Underrun Free technology')
            while 1:
                brnfr = ask_value('yes/no', current)
                if brnfr == '':
                    break
                if brnfr in yes:
                    config.set(section, 'burnfree', brnfr)
                    break
                if brnfr in no:
                    config.set(section, 'burnfree', brnfr)
                    break
    if 'CD-reader' in cs:
        section = 'CD-reader'
        print
        if ask_ok(_('Do you have a second unit as a CD-reader? ')):
            options = config.options(section)
            if 'device' in options:
                print
                current = config.get(section, 'device')
                print _('Which is the device of your CD-reader?')
                print _(
                    '\tYou have to use this syntax:'
                    ' SCSIBUS,TARGET,LUN. E.g.: 1,0,0')
                if os.path.exists('/proc/scsi/scsi'):
                    print _('\tHere follows your system\'s SCSI devices:')
                    scsi_file = open('/proc/scsi/scsi', 'r')
                    for line in scsi_file.readlines():
                        print "\t", line
                while 1:
                    tmpdr = ask_value('CD-reader device', current)
                    if tmpdr == '':
                        break
                    else:
                        config.set(section, 'device', tmpdr)
                        break
            if 'driver' in options:
                print
                current = config.get(section, 'driver')
                print _('Does your CD-reader use a specific driver?')
                print _('\tPossible values are: ')
                values = [
                    "tcdd2600", "plextor", "plextor-scan",
                    "generic-mmc", "generic-mmc-raw",
                    "ricoh-mp6200", "yamaha-cdr10x", "teac-cdr55",
                    "sony-cdu920", "sony-cdu948", "taiyo-yuden", "toshiba",
                    ]
                print textwrap.fill(
                    ", ".join(values),
                    initial_indent="\t\t", subsequent_indent="\t\t",
                    break_long_words=False)
                while 1:
                    drvr = ask_value('driver', current)
                    if drvr == '':
                        break
                    else:
    #                   config.set(section, 'driver', drvr)
                        break
    if 'Media' in cs:
        section = 'Media'
        options = config.options(section)
        if 'size' in options:
            print
            current = config.get(section, 'size')
            print _('Which is the most common capacity of your target CDs?')
            while 1:
                tmpdr = ask_value('CD size', current)
                if tmpdr == '':
                    break
                else:
                    config.set(section, 'size', tmpdr)
                    break
        if 'media-check' in options:
            print
            current = config.get(section, 'media-check')
            print _('Do you want burn to auto-check target CD capacity?')
            print _('\tThis function uses cdrdao.')
            while 1:
                brnfr = ask_value('yes/no', current)
                if brnfr == '':
                    break
                if brnfr in yes:
                    config.set(section, 'media-check', brnfr)
                    break
                if brnfr in no:
                    config.set(section, 'media-check', brnfr)
                    break

    if not config.write(conf_new):
        print
        print
        print _('Congratulations!!!')
        print _('Now you have your new configuration file:')
        print target_conf_file_path
        print _('Please rename it and place it as ~/.burnrc or /etc/burn.conf')
    else:
        print _('Unable to write configuration file...')


if __name__ == '__main__':
    exit_status = main()
    sys.exit(exit_status)


# Local variables:
# mode: python
# coding: utf-8
# End:
# vim: filetype=python fileencoding=utf-8 :
