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

import argparse
import logging
import sys

from distami.core import Distami, Logging
from distami import utils
from distami.exceptions import DistamiException
from boto.utils import get_instance_metadata

__all__ = ('run', )
log = logging.getLogger(__name__)


def _fail(message="Unknown failure", code=1):
    log.error(message)
    sys.exit(code)


def run():
    parser = argparse.ArgumentParser(description='Distributes an AMI by making it public.')
    parser.add_argument('ami_id', metavar='AMI_ID', help='the source AMI ID to distribute. E.g. ami-1234abcd')
    parser.add_argument('--region', metavar='REGION', help='the region the AMI is in (default is current region of EC2 instance this is running on). E.g. us-east-1')
    parser.add_argument('--verbose', '-v', action='count', help='verbose output (-vvv for more)')
    args = parser.parse_args()
    
    Logging().configure(args.verbose)

    log.debug("CLI parse args: %s", args)

    if args.region:
        ami_region = args.region
    else:
        # If no region was specified, assume this is running on an EC2 instance
        # and work out what region it is in
        log.debug("Figure out which region I am running in...")
        instance_metadata = get_instance_metadata(timeout=5)
        log.debug('md: %s', instance_metadata)
        if not instance_metadata:
            _fail('This script is either not running in on an EC2 instance, or the meta-data service is down')
        
        ami_region = instance_metadata['placement']['availability-zone'][:-1]
        log.debug("Running in region: %s", ami_region)

    try:
        distami = Distami(args.ami_id, ami_region)
        distami.make_ami_public()
        distami.make_snapshot_public()
        
        for region in utils.get_regions_to_copy_to(ami_region):
            copied_ami_id = distami.copy_to_region(region)
            ami_cp = Distami(copied_ami_id, region)
            ami_cp.make_ami_public()
            ami_cp.make_snapshot_public()
            _fail('Lets just do 1 for now')
        
    except DistamiException as e:
        _fail(e.message)
    
    sys.exit(0)
    
