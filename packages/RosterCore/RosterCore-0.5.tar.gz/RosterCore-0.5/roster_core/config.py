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

"""Module to handle config file loading."""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD'
__version__ = '0.5'


import ConfigParser
import errors
import db_access


class ConfigError(errors.CoreError):
  pass


class Config(object):
  """Abstracts a config file for Roster Core and Server"""
  def __init__(self, file_name='/etc/roster_server.conf'):
    """Sets self.server, self.database, self.login and self.password from 
    a config file or passed vriables.

    Inputs:
      file_name:	name of config file to parse
      db_server: name of database server
      db_database: name of database on server
      db_login: login name used to access the database
      db_passwd: password used to login to the database

    Raises:
      ConfigError:	If file is missing, or if file is malformed or bad args.
    """
    cp = ConfigParser.SafeConfigParser()
    a = cp.read(file_name)
    self.config_file = {}
    self.config_file_path = file_name
    if( a == [] ):
      raise ConfigError('Could not read the file %s' % file_name)

    # Supported data types: str, int, boolean, float
    file_schema = {'database': {'server': 'str', 'login': 'str',
                   'passwd': 'str', 'database': 'str'},
                   'server': {'inf_renew_time': 'int', 'core_die_time': 'int',
                   'get_credentials_wait_increment': 'int',
                   'ldap_server': 'str', 'server_killswitch': 'boolean'},
                   'credentials': {'binddn': 'str', 'exp_time': 'int'}}

    for section in file_schema:
      self.config_file[section] = {}
      if( cp.has_section(section) ):
        variables = file_schema[section]
        file_variables = cp.options(section)
        for variable in file_variables:
          if( variable not in variables ):
            raise ConfigError('Variable "%s" in "%s" is not used' % (
                variable, file_name))
        for variable in variables:
          if( variable not in file_variables ):
            raise ConfigError('Variable "%s" is missing in config file: "%s", '
                              'in the "%s" section.' % (variable,
                                                        file_name, section))
          if( variables[variable] is 'str' ):
            self.config_file[section][variable] = (
                cp.get(section, variable))
          elif( variables[variable] is 'int' ):
            self.config_file[section][variable] = (
                cp.getint(section, variable))
          elif( variables[variable] is 'boolean' ):
            self.config_file[section][variable] = cp.getboolean(section,
                                                                variable)
          elif( variables[variable] is 'float' ):
            self.config_file[section][varaible] = cp.getfloat(section, varaible)
          else:
            raise ConfigError('DataType "%s" is not supported' % (
                varaibles[varaible]))

  def GetDb(self):
    """Creates a dbAccess instance.

    Outputs:
      dbAccess instance
    """
    return db_access.dbAccess(self.config_file['database']['server'],
                              self.config_file['database']['login'],
                              self.config_file['database']['passwd'],
                              self.config_file['database']['database'])


# vi: set ai aw sw=2:
