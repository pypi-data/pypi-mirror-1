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

"""Make record library for command line tools."""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '0.5'


import os
import xmlrpclib

import cli_common_lib
import roster_client_lib


def MakeRecord(record_type, options, record_args_dict, allow_duplicate=False,
               quiet=False, raise_errors=False):
  """Connects to server and makes a DNS record.

  Inputs:
    record_type: record type
    options: options object from optparse
    record_args_dict: dictionary varying according to record record_type
    allow_duplicate: allow duplicate entries without causing error
    quiet: whether or not function should be quiet
    raise_errors: raise errors rather than printing
  """
  for item in record_args_dict:
    if( record_args_dict[item] is None ):
      cli_common_lib.DnsError('Must specify --%s-%s' % (record_type,
                                                    item.replace('_', '-')), 1)
  if( not options.credfile.startswith('/') ):
    options.credfile = '%s/%s' % (os.getcwd(), options.credfile)
  cli_common_lib.CheckCredentials(options)
  views = roster_client_lib.RunFunction('ListViews', options.username,
                                        credfile=options.credfile,
                                        server_name=options.server,
                                        raise_errors=raise_errors)[
                                            'core_return']
  zones = roster_client_lib.RunFunction('ListZones', options.username,
                                        credfile=options.credfile,
                                        server_name=options.server,
                                        raise_errors=raise_errors)[
                                            'core_return']
  search_target = options.target
  if( record_type == u'ptr' ):
      search_target = roster_client_lib.RunFunction(
          'GetPTRTarget', options.username, credfile=options.credfile,
          server_name=options.server, args=[options.target, options.view_name],
          raise_errors=raise_errors)['core_return'][0]
  records = roster_client_lib.RunFunction(
      'ListRecords', options.username, credfile=options.credfile,
      server_name=options.server, kwargs={'record_type': record_type,
                                          'target': search_target,
                                          'zone_name': options.zone_name,
                                          'view_name': options.view_name},
      raise_errors=raise_errors)['core_return']

  ## Check if view exists
  if( not views.has_key(options.view_name) and options.view_name != 'any' ):
    cli_common_lib.DnsError('View does not exist!', 2)
  ## Check if zone exists
  if( not zones.has_key(options.zone_name) ):
    cli_common_lib.DnsError('Zone does not exist!', 3)
  ## Check for duplicate record
  if( records != [] and not allow_duplicate ):
    for record in records:
      for record_arg in record_args_dict:
        if( record[record_arg] != record_args_dict[record_arg] ):
          break
      else:
        cli_common_lib.DnsError('Duplicate record!', 4)
  if( record_type == u'aaaa' ):
    roster_client_lib.RunFunction(
        u'MakeAAAARecord', options.username, credfile=options.credfile,
        args=[options.target, options.zone_name, record_args_dict],
        kwargs={'view_name': options.view_name, 'ttl': options.ttl},
        server_name=options.server, raise_errors=raise_errors)
    if( options.view_name is None ):
      options.view_name = u'any'
    if( options.ttl is None ):
      options.ttl = u'DEFAULT'
    if( not quiet ):
      arg_list = []
      for argument in record_args_dict:
        arg_list.append('%s:' % argument)
        if( record_args_dict[argument] is None ):
          arg_list.append('DEFAULT')
        else:
          arg_list.append(str(record_args_dict[argument]))
      print 'ADDED AAAA: %s zone_name: %s view_name: %s ttl: %s' % (
          options.target, options.zone_name, options.view_name,
          options.ttl)
      print '    %s' % ' '.join(arg_list)
  elif( record_type == u'ptr' ):
    roster_client_lib.RunFunction(
        u'MakePTRRecord', options.username, credfile=options.credfile,
        args=[options.target, record_args_dict],
        kwargs={'view_name': options.view_name, 'ttl': options.ttl},
        server_name=options.server, raise_errors=raise_errors)
    if( options.view_name is None ):
      options.view_name = u'any'
    if( options.ttl is None ):
      options.ttl = u'DEFAULT'
    if( not quiet ):
      arg_list = []
      for argument in record_args_dict:
        arg_list.append('%s:' % argument)
        if( record_args_dict[argument] is None ):
          arg_list.append('DEFAULT')
        else:
          arg_list.append(str(record_args_dict[argument]))
      print 'ADDED PTR: %s zone_name: %s view_name: %s ttl: %s' % (
          options.target, options.zone_name, options.view_name,
          options.ttl)
      print '    %s' % ' '.join(arg_list)
  else:
    roster_client_lib.RunFunction(
        u'MakeRecord', options.username, credfile=options.credfile,
        args=[record_type, options.target, options.zone_name,
        record_args_dict],
        kwargs={'view_name': options.view_name, 'ttl': options.ttl},
        server_name=options.server, raise_errors=raise_errors)['core_return']
    if( options.view_name is None ):
      options.view_name = u'any'
    if( options.ttl is None ):
      options.ttl = u'DEFAULT'
    if( not quiet ):
      arg_list = []
      for argument in record_args_dict:
        arg_list.append('%s:' % argument)
        if( record_args_dict[argument] is None ):
          arg_list.append('DEFAULT')
        else:
          arg_list.append(str(record_args_dict[argument]))
      print 'ADDED %s: %s zone_name: %s view_name: %s ttl: %s' % (
          record_type.upper(), options.target, options.zone_name,
          options.view_name, options.ttl)
      print '    %s' % ' '.join(arg_list)

def RemoveRecord(record_type, options, record_args_dict, quiet=False,
                 raise_errors=False):
  """Connects to server and removes a DNS record.

  Inputs:
    record_type: record type
    options: options object from optparse
    record_args_dict: dictionary varying according to record record_type
    quiet: whether or not function should be quiet
    raise_errors: raise errors rather than printing
  """
  for item in record_args_dict:
    if( record_args_dict[item] is None ):
      cli_common_lib.DnsError('Must specify --%s-%s' % (record_type,
                                                    item.replace('_', '-')), 1)
  if( not options.credfile.startswith('/') ):
    options.credfile = '%s/%s' % (os.getcwd(), options.credfile)
  cli_common_lib.CheckCredentials(options)
  views = roster_client_lib.RunFunction(
      'ListViews', options.username, credfile=options.credfile,
      server_name=options.server)['core_return']
  zones = roster_client_lib.RunFunction(
      'ListZones', options.username, credfile=options.credfile,
      server_name=options.server, raise_errors=raise_errors)['core_return']
  ## Check if view exists
  if( not views.has_key(options.view_name) ):
    cli_common_lib.DnsError('View does not exist!', 2)
  ## Check if zone exists
  if( not zones.has_key(options.zone_name) ):
    cli_common_lib.DnsError('Zone does not exist!', 3)
  roster_client_lib.RunFunction(
      u'RemoveRecord', options.username, credfile=options.credfile,
      args=[record_type, options.target, options.zone_name, record_args_dict,
            options.view_name], kwargs={'ttl': options.ttl},
      server_name=options.server, raise_errors=raise_errors)
  if( options.view_name is None ):
    options.view_name = u'any'
  if( options.ttl is None ):
    options.ttl = u'DEFAULT'
  if( not quiet ):
    arg_list = []
    for argument in record_args_dict:
      arg_list.append('%s:' % argument)
      if( record_args_dict[argument] is None ):
        arg_list.append('DEFAULT')
      else:
        arg_list.append(str(record_args_dict[argument]))
    print 'REMOVED %s: %s zone_name: %s view_name: %s ttl: %s' % (
        record_type.upper(), options.target, options.zone_name,
        options.view_name, options.ttl)
    print '    %s' % ' '.join(arg_list)

def ListRecords(record_type, options, record_args_dict):
  """Lists records given certain parameters

  Inputs:
    options: options object from optparse
    record_args_dict: record arguments dictionary

  Outputs:
    list or string depending on record type
  """
  search_target = options.target
  if( record_type == u'ptr' ):
      search_target = roster_client_lib.RunFunction(
          'GetPTRTarget', options.username, credfile=options.credfile,
          server_name=options.server, args=[options.target, options.view_name])[
              'core_return'][0]
  records = roster_client_lib.RunFunction(
      'ListRecords', options.username, credfile=options.credfile,
      server_name=options.server, kwargs={'record_type': record_type,
                                          'target': search_target,
                                          'zone_name': options.zone_name,
                                          'view_name': options.view_name})[
                                              'core_return']
  if( record_type is None ):
    records_type_dict = {}
    return_list = []
    print_list = []
    for record in records:
      if( record['record_type'] not in records_type_dict ):
        records_type_dict[record['record_type']] = []
      records_type_dict[record['record_type']].append(record)
    for record_type in records_type_dict:
      key_list = []
      have_keys = options.no_header
      for record in records_type_dict[record_type]:
        if( not have_keys ):
          for key in record:
            key_list.append(key)
          print_list = [key_list]
          have_keys = True
        print_list.append(record.values())
      return_list.append(cli_common_lib.PrintColumns(
          print_list, first_line_header=(not options.no_header)))
    return return_list
  else:
    have_keys = options.no_header
    key_list = []
    print_list = []
    for record in records:
      if( not have_keys ):
        for key in record:
          key_list.append(key)
        print_list = [key_list]
        have_keys = True
      print_list.append(record.values())
    return cli_common_lib.PrintColumns(
        print_list, first_line_header=(not options.no_header))

def RemoveForwardReverseRecord(options, hostname, ip_address,
                               reverse_ip_address, zone_origin, record_type):
  """Removes forward and reverse records given certain parameters.

  Inputs:
    options: options object from optparse
    hostname; string of hostname
    ip_address: string of ip address
    reverse_ip_address: reversed ip address
    zone_origin: string of zone origin
    record_type: string of record type
  """
  try:
    options.target = hostname.rplit('.%s' % zone_origin, 1)[0]
    RemoveRecord(record_type, options, {u'assignment_ip': ip_address})
    options.target = reverse_ip_address
    RemoveRecord(u'ptr', options, {u'assignment_host': options.target})
  except xmlrpclib.Fault, error:
    error_string = error.faultString.split(':')[1]
    if( error_string != 'No records found.' ):
      raise

def MakeForwardReverseRecord(options, hostname, ip_address, reverse_ip_address,
                             zone_origin, record_type):
  """Makes forward and reverse records given certain parameters.

  Inputs:
    options: options object from optparse
    hostname; string of hostname
    ip_address: string of ip address
    reverse_ip_address: reversed ip address
    zone_origin: string of zone origin
    record_type: string of record type
  """
  options.target = hostname.rsplit('.%s' % zone_origin, 1)[0]
  MakeRecord(record_type, options, {u'assignment_ip': ip_address})
  options.hostname = options.target
  options.target = reverse_ip_address
  MakeRecord(u'ptr', options, {u'assignment_host': '%s.%s.' % (
      options.hostname, zone_origin)})
