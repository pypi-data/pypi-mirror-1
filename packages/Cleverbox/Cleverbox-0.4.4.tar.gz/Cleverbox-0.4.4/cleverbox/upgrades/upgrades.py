# This file is part of the "Cleverbox" program.
#
# Cleverbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cleverbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cleverbox.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Tristan Rivoallan

from pkg_resources import parse_version

def do_upgrade_1(envname, env_version):
    if parse_version(env_version) < parse_version('0.4'):
        print "It is not possible to upgrade cleverbox instances created with Cleverbox prior to 0.4"
        print "It was not even a public release !"
        print "Your only choice left is to pay big money for Clever Age (http://www.clever-age.com) consultants to make a manual migration."

def do_upgrade_2(envname, env_version):
    import os

    print "Upgrading to cleverbox-0.4.2dev"

    f = open(os.path.join(envname, 'VERSION'), 'w')
    f.write('0.4.2dev')
    f.close()

    print "Done upgrading"

def do_upgrade_3(envname, env_version):
    import os

    print "Upgrading to cleverbox-0.4.3"

    f = open(os.path.join(envname, 'VERSION'), 'w')
    f.write('0.4.3')
    f.close()

    print "Done upgrading"

def do_upgrade_4(envname, env_version):
    import os

    print "Upgrading to cleverbox-0.4.4"

    f = open(os.path.join(envname, 'VERSION'), 'w')
    f.write('0.4.4')
    f.close()

    print "Done upgrading"
