# Copyright 2009 David Reynolds
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

import distutils.core

distutils.core.setup(
    name="simplestore",
    version="0.3",
    packages=["simplestore", "simplestore.model", "simplestore.tests"],
    author="David Reynolds",
    author_email="david@alwaysmovefast.com",
    url="http://code.google.com/p/simplestore/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="A datastore layer built on top of MySQL in Python."
)
