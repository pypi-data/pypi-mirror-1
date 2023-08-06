#!/usr/bin/env python
#
# Copyright 2009 Matthew Wilkes
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

import os

import unittest

import gae


class FunctionalTestCase(unittest.TestCase):
    def setUp(self):
        if not hasattr(self, "path"):
            raise AttributeError("The path to the configuration yaml was not"
                                 " supplied.")
        if not os.path.exists(self.path):
            raise AttributeError("The path to the configuration yaml does not"
                                 " exist.")
        elif self.path.endswith(".yaml") or self.path.endswith(".yml"):
            self.path = os.path.dirname(self.path)

        unittest.TestCase.setUp(self)
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)
        gae.testingRunWithEphemeralStorage(self.path)
