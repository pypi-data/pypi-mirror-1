#!/usr/bin/python

# Copyright (c) 2009, Purdue University
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
# 
# Neither the name of the Purdue University nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Common library for DNS management command line tools."""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '0.5'


import sys
import getpass
import roster_client_lib


def DnsError(message, exit_status=0):
  """Prints standardized client error message to screen.

  Inputs:
    message: string of message to be displayed on screen
    exit_status: integer of retrun code, assumed not exit if 0
  """
  print "CLIENT ERROR: %s" % message
  if( exit_status ):
    sys.exit(exit_status)

def ServerError(message, exit_status=0):
  """Prints standardized server error message to screen.

  Inputs:
    message: string of message to be displayed on screen
    exit_status: integer of retrun code, assumed not exit if 0
  """
  print "SERVER ERROR: %s" % message
  if( exit_status ):
    sys.exit(exit_status)

def DnsWarning(message):
  """Prints standardized warning message to screen.

  Inputs:
    message: string of message to be displayed on screen
  """
  print "WARNING: %s" % message

def PrintColumns(print_list, first_line_header=False):
  """Prints a table with aligned columns.

  Inputs:
    print_list: list of lists of columns
    file: string of filename
  """
  ## Construct zeros for lengths
  lengths = []
  if( print_list ):
    for column in print_list[0]:
      lengths.append(0)
  ## Get sizes of strings
  total_length = 0
  for row in print_list:
    for column_index, column in enumerate(row):
      if( len(str(column)) > lengths[column_index] ):
        lengths[column_index] = len(str(column))
        total_length += len(str(column)) - 1
  ## Construct string
  print_string_list = []
  for row in print_list:
    string_list = []
    string_args_list = []
    for column_index, column in enumerate(print_list[0]):
      string_list.append('%*s')
      string_args_list.extend([lengths[column_index] * -1, row[column_index]])
    print_line = ' '.join(string_list) % tuple(string_args_list)
    print_string_list.append('%s\n' % print_line.strip())
    if( first_line_header and (print_list.index(row) == 0) ):
      hyphen_list = []
      for character in range(len(print_line.strip())):
        hyphen_list.append('-')
      print_string_list.append('%s\n' % ''.join(hyphen_list))
  return ''.join(print_string_list)

def PrintRecords(records_dictionary, ip_address_list=[]):
  """Prints records dictionary in a nice usable format.

  Inputs:
    records_dictionary: dictionary of records
    ip_address_list: list of ip_addresses to use
  """
  if( ip_address_list == [] ):
    for view in records_dictionary:
      ip_address_list.extend(records_dictionary[view].keys())
    ip_address_list = list(set(ip_address_list))

  print_list = []
  for view in records_dictionary:
    for ip_address in ip_address_list:
      if( ip_address in records_dictionary[view] ):
        for record in records_dictionary[view][ip_address]:
          direction = 'Reverse'
          if( record['forward'] ):
            direction = 'Forward'
          print_list.append([ip_address, direction, record['host'],
                                  record['zone'], view])
      else:
        print_list.append([ip_address, '--', '--', '--', '--'])
  return PrintColumns(print_list)

def PrintHosts(records_dictionary, ip_address_list, zones_info,
               view_name=None):
  """Prints hosts in an /etc/hosts format

  Inputs:
    records_dictionary: dictionary of records
    ip_address_list: list of ip_addresses
    view_name: string of view_name
    zones_info: zones info from list zones
  """
  print_dict = {}
  print_list = []
  for view in records_dictionary:
    for ip_address in ip_address_list:
      print_dict[ip_address] = {}
      if( ip_address in records_dictionary[view] and view == view_name ):
        print_dict[ip_address].update({'forward': False, 'reverse': False})
        for record in records_dictionary[view][ip_address]:
          if( record['forward'] ):
            print_dict[ip_address].update({'host': record['host'],
              'forward': True, 'zone_origin': zones_info[record['zone']][
                  view]['zone_origin']})
          else:
            print_dict[ip_address].update({'host': record['host'],
              'reverse': True, 'zone_origin': zones_info[record['zone']][
                  view]['zone_origin']})
  for ip_address in ip_address_list:
    if( print_dict[ip_address] == {} ):
      print_list.append(['#%s' % ip_address, '', '', ''])
    else:
      forward_zone_origin = print_dict[ip_address]['zone_origin'].rstrip('.')
      if( print_dict[ip_address]['forward'] and print_dict[ip_address][
          'reverse'] ):
        print_list.append([ip_address, print_dict[ip_address]['host'],
                           print_dict[ip_address]['host'].rsplit(
                               '.%s' % forward_zone_origin, 1)[0], ''])
      elif( print_dict[ip_address]['forward'] ):
        print_list.append([ip_address, print_dict[ip_address]['host'],
                           print_dict[ip_address]['host'].rsplit(
                               '.%s' % forward_zone_origin, 1)[0],
                           '# No reverse assignment'])
      else:
        print_list.append(['#%s' % ip_address, print_dict[ip_address]['host'],
                           '', '# No forward assignment'])
  return PrintColumns(print_list)

def CheckCredentials(options):
  """Checks if credential file is valid.

  Inputs:
    options: options object from optparse

  Outputs:
    string: string of valid credential
  """
  password = None
  got_credential = None
  count = 0
  while( count < 3 ):
    valid = roster_client_lib.IsAuthenticated(options.username,
                                              options.credfile,
                                              server_name=options.server)
    if( valid ):
      break
    password = options.password
    if( options.password is None ):
      try:
        password = getpass.getpass('Password for %s: ' % options.username)
      except KeyboardInterrupt:
        sys.exit(0)
    try:
      got_credential = roster_client_lib.GetCredentials(options.username,
                                                        password,
                                                        options.credfile,
                                                        options.server)
    except roster_client_lib.InvalidCredentials:
      if( options.password is None ):
        count = count + 1
      else:
        DnsError('Incorrect username/password.', 1)
  else:
    DnsError('Incorrect username/password.', 1)

  return got_credential

def DisallowFlags(disallow_list, parser, options):
  """Dissallows certain command line flags.

  Inputs:
    disallow_list: list of command line flags to block
    parser: parser object from optparse
    options: options object from optparse
  """
  defaults = parser.defaults
  flags = {}
  error = False
  for flag in parser.option_list[1:]:
    flags[flag.dest] = flag
    combo = 'options.%s' % flag.dest
    if( flag.dest in disallow_list ):
      if( eval(combo) != defaults[flag.dest] ):
        DnsError('The %s flag cannot be used.' % flag, 0)
        error = True
  if( error ):
    sys.exit(1)

