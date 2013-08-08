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

from boto import ec2

log = logging.getLogger(__name__)


def get_regions_to_copy_to(source_region):
    ''' Gets the list of regions to copy an AMI to '''
    
    regions = []
    for region in ec2.regions():
        if region.name == source_region:
            continue
        regions.append(region.name)
        
    return regions

