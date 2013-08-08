# Copyright 2013 Answers for AWS LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import boto
from boto import ec2

from distami.exceptions import * 


__all__ = ('Distami', 'Logging')
log = logging.getLogger(__name__)


class Distami(object):
    def __init__(self, ami_id, ami_region):
        self._ami_id = ami_id
        self._ami_region = ami_region
        
        log.info("Looking for AMI %s in region %s", self._ami_id, self._ami_region)
        conn = ec2.connect_to_region(self._ami_region)
        try:
            images = conn.get_all_images(self._ami_id)
        except boto.exception.EC2ResponseError:
            msg = 'Could not find AMI %s in region %s' % (self._ami_id, self._ami_region)
            raise DistamiException(msg)
        
        log.debug("Found AMIs: %s", images)
        if len(images) != 1:
            msg = "Somehow more than 1 AMI was detected - this is a weird error"
            raise DistamiException(msg)
            
        self._image = images[0]
        self._launch_perms = self._image.get_launch_permissions()
        log.info("Launch perms: %s", self._launch_perms)
        
    def make_ami_public(self):
        pass
    
    def make_ami_private(self):
        # TODO - reverse of public
        pass
    
    def make_snapshot_public(self):
        pass
    
    def make_snapshot_private(self):
        # TODO - reverse of public
        pass

    def copy_to_region(self, region):
        pass
        
     
class Logging(object):
    # Logging formats
    _log_simple_format = '%(asctime)s [%(levelname)s] %(message)s'
    _log_detailed_format = '%(asctime)s [%(levelname)s] [%(name)s(%(lineno)s):%(funcName)s] %(message)s'
    
    def configure(self, verbosity = None):
        ''' Configure the logging format and verbosity '''
        
        # Configure our logging output
        if verbosity >= 3:
            logging.basicConfig(level=logging.DEBUG, format=self._log_detailed_format, datefmt='%F %T')
        elif verbosity >= 1:
            logging.basicConfig(level=logging.INFO, format=self._log_simple_format, datefmt='%F %T')
        else:
            logging.basicConfig(format=self._log_simple_format, datefmt='%F %T')
    
        # Configure Boto's logging output
        if verbosity >= 4:
            logging.getLogger('boto').setLevel(logging.DEBUG)
        elif verbosity >= 2:
            logging.getLogger('boto').setLevel(logging.INFO)
        else:
            logging.getLogger('boto').setLevel(logging.CRITICAL)    
    
