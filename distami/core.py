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
from distami import utils 

__all__ = ('Distami', 'Logging')
log = logging.getLogger(__name__)


class Distami(object):
    def __init__(self, ami_id, ami_region):
        self._ami_id = ami_id
        self._ami_region = ami_region
        
        log.info("Looking for AMI %s in region %s", self._ami_id, self._ami_region)
        try:
            self._conn = ec2.connect_to_region(self._ami_region)
        except boto.exception.NoAuthHandlerFound, e:
            log.error('Could not connect to region %s' % self._ami_region)
            log.critical('No AWS credentials found. To configure Boto, please read: http://boto.readthedocs.org/en/latest/boto_config_tut.html')
            raise DistamiException('No AWS credentials found.')            
        self._image = utils.wait_for_ami_to_be_available(self._conn, self._ami_id)
        log.debug('AMI details: %s', vars(self._image))
        
        # Get current launch permissions
        self._launch_perms = self._image.get_launch_permissions()
        log.debug("Current launch permissions: %s", self._launch_perms)
        
        # Figure out the underlying snapshot
        bdm = self._image.block_device_mapping['/dev/sda1']
        log.debug('Block device mapping for /dev/sda1: %s', vars(bdm))
        self._snapshot_id = bdm.snapshot_id

        log.info("Found AMI %s with snapshot %s", self._ami_id, self._snapshot_id)

    
    def make_ami_public(self):
        ''' Adds the 'all' group permission to the AMI, making it publicly accessible '''
        
        log.info('Making AMI %s public', self._ami_id)

        if 'groups' in self._launch_perms and any("all" in groups for groups in self._launch_perms['groups']):
            log.debug('AMI already public, nothing to do')
            return True
        
        res = self._image.set_launch_permissions(group_names='all')
        self._launch_perms = self._image.get_launch_permissions()
        return res
    
    
    def make_ami_non_public(self):
        ''' Removes the 'all' group permission from the AMI '''

        log.info('Making AMI %s non-public', self._ami_id)

        if 'groups' in self._launch_perms and any("all" in groups for groups in self._launch_perms['groups']):
            res = self._image.remove_launch_permissions(group_names='all')
            self._launch_perms = self._image.get_launch_permissions()
            return res
        
        log.debug('AMI is already not public')
        return True
    
    def share_ami_with_accounts(self, account_ids):
        ''' Shares an AMI with the supplied list of AWS Account IDs '''
        
        log.info('Sharing AMI %s with AWS Accounts %s', self._ami_id, account_ids)

        res = self._image.set_launch_permissions(user_ids=account_ids)
        self._launch_perms = self._image.get_launch_permissions()
        return res
       
    def make_snapshot_public(self):
        ''' Makes a snapshot public '''
        
        snapshot = utils.get_snapshot(self._conn, self._snapshot_id)
        log.debug('Snapshot details: %s', vars(snapshot))

        log.info('Making snapshot %s public', self._snapshot_id)
        return snapshot.share(groups=['all'])
    
    
    def make_snapshot_non_public(self):
        ''' Removes the 'all' group permission from the snapshot '''
        
        snapshot = utils.get_snapshot(self._conn, self._snapshot_id)
        log.debug('Snapshot details: %s', vars(snapshot))
        
        log.info('Making snapshot %s non-public', self._snapshot_id)
        return snapshot.unshare(groups=['all'])


    def share_snapshot_with_accounts(self, account_ids):
        ''' Shares a snapshot with the supplied list of AWS Account IDs '''
        
        snapshot = utils.get_snapshot(self._conn, self._snapshot_id)
        log.debug('Snapshot details: %s', vars(snapshot))

        log.info('Sharing snapshot %s with AWS Accounts %s', self._snapshot_id, account_ids)
        return snapshot.share(user_ids=account_ids)
    
    
    def copy_to_region(self, region):
        ''' Copies this AMI to another region '''
        
        dest_conn = ec2.connect_to_region(region)
        log.info('Copying AMI to %s', region)
        cp_ami = dest_conn.copy_image(self._ami_region, self._ami_id, self._image.name, self._image.description)
        copied_ami_id = cp_ami.image_id
        
        # Wait for AMI to finish copying before returning
        copied_image = utils.wait_for_ami_to_be_available(dest_conn, copied_ami_id)
        
        # Copy AMI tags to new AMI
        log.info('Copying tags to %s in %s', copied_ami_id, region)
        dest_conn.create_tags(copied_ami_id, self._image.tags)
        
        # Also copy snapshot tags to new snapshot
        copied_snapshot_id = copied_image.block_device_mapping['/dev/sda1'].snapshot_id
        snapshot = utils.get_snapshot(self._conn, self._snapshot_id)
        log.info('Copying tags to %s in %s', copied_snapshot_id, region)
        dest_conn.create_tags(copied_snapshot_id, snapshot.tags)

        log.info('Copy to %s complete', region)
        return copied_ami_id



class Logging(object):
    # Logging formats
    _log_simple_format = '%(asctime)s [%(levelname)s] %(message)s'
    _log_detailed_format = '%(asctime)s [%(levelname)s] [%(name)s(%(lineno)s):%(funcName)s] %(message)s'
    
    def configure(self, verbosity = None):
        ''' Configure the logging format and verbosity '''
        
        # Configure our logging output
        if verbosity >= 2:
            logging.basicConfig(level=logging.DEBUG, format=self._log_detailed_format, datefmt='%F %T')
        elif verbosity >= 1:
            logging.basicConfig(level=logging.INFO, format=self._log_detailed_format, datefmt='%F %T')
        else:
            logging.basicConfig(level=logging.INFO, format=self._log_simple_format, datefmt='%F %T')
    
        # Configure Boto's logging output
        if verbosity >= 4:
            logging.getLogger('boto').setLevel(logging.DEBUG)
        elif verbosity >= 3:
            logging.getLogger('boto').setLevel(logging.INFO)
        else:
            logging.getLogger('boto').setLevel(logging.CRITICAL)    
    
