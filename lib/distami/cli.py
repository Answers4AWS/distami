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

from multiprocessing import Pool


__all__ = ('run', )
log = logging.getLogger(__name__)


def _fail(message="Unknown failure", code=1):
    log.error(message)
    sys.exit(code)


def copy(ami_region_pair):
    ''' Copies distami to the given region '''
    
    distami = ami_region_pair[0]
    to_region = ami_region_pair[1]
    copied_ami_id = distami.copy_to_region(to_region)
    ami_cp = Distami(copied_ami_id, to_region)
    ami_cp.make_ami_public()
    ami_cp.make_snapshot_public()
    

def run():
    parser = argparse.ArgumentParser(description='Distributes an AMI by making it public.')
    parser.add_argument('ami_id', metavar='AMI_ID', 
                        help='the source AMI ID to distribute. E.g. ami-1234abcd')
    parser.add_argument('--region', metavar='REGION', 
                        help='the region the AMI is in (default is current region of EC2 instance this is running on). E.g. us-east-1')
    parser.add_argument('--to', metavar='REGIONS', 
                        help='comma-separated list of regions to copy the AMI to. The default is all regions. E.g. us-east-1,us-west-1,us-west-2')
    parser.add_argument('-p', '--parallel', action='store_true', default=False, 
                        help='Perform each copy to another region in parallel. The default is in serial which can take a long time')
    parser.add_argument('--verbose', '-v', action='count', 
                        help='enable verbose output (-vvv for more)')
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
        log.debug('Instance meta-data: %s', instance_metadata)
        if not instance_metadata:
            _fail('Could not determine region. This script is either not running on an EC2 instance, or the meta-data service is down')
        
        ami_region = instance_metadata['placement']['availability-zone'][:-1]
        log.debug("Running in region: %s", ami_region)

    try:
        distami = Distami(args.ami_id, ami_region)
        distami.make_ami_public()
        distami.make_snapshot_public()
        
        if args.to and args.to != 'all':
            # TODO It is probably worth sanity checking this for typos
            to_regions = args.to.split(',')
        else:
            to_regions = utils.get_regions_to_copy_to(ami_region)
        
        if args.parallel:
            # Get input to copy function 
            f = lambda x,y: [x, y]
            pairs = map(f, [distami] * len(to_regions), to_regions)
            log.debug(pairs)

            # Copy to regions in parallel
            log.info('Copying in parallel. Hold on to your hats...')
            pool = Pool(processes=8)
            pool.map(copy, pairs)
            pool.close()
            pool.join()
        else:
            # Copy to regions one at a time
            for region in to_regions:
                copy([distami, region])
        
    except DistamiException as e:
        _fail(e.message)
    
    log.info('AMI successfully distributed!')
    sys.exit(0)
    
