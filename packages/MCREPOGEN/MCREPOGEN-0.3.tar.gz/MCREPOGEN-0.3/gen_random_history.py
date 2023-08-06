#!/usr/bin/env python
# Copyright 2009 Neil Martinsen-Burrell

# This file is part of mcrepogen
#
# mcrepogen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Create history of a random directory tree

MCREPOGEN creates random histories of directory trees using a Markov
Chain approach.
"""

import sys, re
from configobj import ConfigObj

from mcrepogen import transition
from mcrepogen.version_info import version_str
from mcrepogen.mutators import *
from mcrepogen.editors import *


def _objects_from_config(config):
    """Generate mutators and editors as specified in a configuration file.

    :param config: A file-like object in ConfigObj format that specifies
                   classes with section names and parameters in each section.

    """

    config_obj = ConfigObj(config)
    try:
        mutator_section = config_obj['mutators']
    except KeyError:
        mutator_section = None
    if mutator_section is None:
        mutators = None
    else:
        mutators = []
        for name in mutator_section.sections:
            parameters = mutator_section[name]
            class_name = parameters.pop('class')
            mutators.append(eval(class_name+'(parameters=parameters)'))

    try:
        editor_section = config_obj['editors']
    except KeyError:
        editor_section = None
    if editor_section is None:
        editors = None
    else:
        editors = []
        for name in editor_section:
            parameters = editor_section[name]
            class_name = parameters.pop('class')
            editors.append(eval(class_name+'(parameters=parameters)'))

    return mutators, editors
    
def _config_from_objects(mutators, editors):
    """Create a ConfigObj from the given objects, including all parameters"""

    def _class_to_string(class_object):
        class_string = str(class_object)
        z = re.search("'.*'", class_string)
        return class_string[z.start()+1:z.end()-1]

    c = ConfigObj(); c.indent_type = '  '
    c['mutators'] = {}
    for mutator in mutators:
        c['mutators'][str(mutator)] = mutator.parameters
        c['mutators'][str(mutator)]['class'] = _class_to_string(mutator.__class__)
    c['editors'] = {}
    for editor in editors:
        c['editors'][str(editor)] = editor.parameters
        c['editors'][str(editor)]['class'] = _class_to_string(editor.__class__)
    return c

def generate(output_file=None, revisions=100, 
             config_file=None, show_config=False):
    """Generate a random history

    :param output_file: file to send output to.  The default, None, means
                        that output should go to stdout
    :param revisions: number of revisions to generate
    :param config_file: file with configuration information.  By default
                        try the file `mcrepogen.conf` in the current 
                        directory and if it isn't present, use the
                        program defaults.
    :param show_config: Print out the configuration

    """

    if config_file is None:
        try:
            config = open('mcrepogen.conf', 'r')
        except IOError:
            config = None
    else:
        config = open(config_file, 'r')

    mutators, editors = _objects_from_config(config)
    if mutators is None:
        mutators = transition.get_default_mutators()
    if editors is None:
        editors = transition.get_default_editors()

    if show_config:
        config = _config_from_objects(mutators, editors)
        config.write(sys.stdout)
        return

    b,t = transition.evolve(revisions, mutators, editors)
    if output_file is None:
        out_stream = sys.stdout
    else:
        out_stream = file(output_file, 'w')
    b.serialize(out_stream)


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] [-r REVISIONS] [-o FILE] [-f CONFIG]", 
                          version="%prog "+ version_str)
    parser.add_option('-o', '--output', dest='output', default=None,
                      help='Write output to FILE', metavar='FILE')
    parser.add_option('-r', '--revisions', dest='revisions', default=100,
                      type='int',
                      help='Number of revisions to create')
    parser.add_option('-f', '--config-file', dest='config', default=None,
                      help='Configuration file', metavar='CONFIG')
    parser.add_option('--show-config', dest='show_config', 
                      default=False, action='store_true',
                      help="Don't run, just print out the used configuration")

    (options, args) = parser.parse_args()
    generate(options.output, options.revisions,
             options.config, options.show_config)


if __name__ == "__main__":
    main()
