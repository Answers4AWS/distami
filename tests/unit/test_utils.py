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

import unittest

from distami import utils 

class UtilTests(unittest.TestCase):
    def test_get_regions_to_copy_to(self):
        all_public_regions = ['ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'us-east-1', 'us-west-1', 'us-west-2', 'sa-east-1', 'eu-west-1']
        regions = utils.get_regions_to_copy_to('not-a-real-region')
        self.assertItemsEqual(regions, all_public_regions)
        
        
        