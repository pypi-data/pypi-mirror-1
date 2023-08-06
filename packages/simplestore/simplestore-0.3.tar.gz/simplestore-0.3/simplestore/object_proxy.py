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

import threading

class ObjectProxy(object):

    def __init__(self, name):
        self.__dict__['__name__'] = name
        self.__dict__['__local__'] = threading.local()

    def __getattr__(self, name):
        return getattr(self._obj(), name)

    def __setattr__(self, name, value):
        setattr(self._obj(), name, value)

    def __delattr__(self, name):
        delattr(self._obj(), name)

    def _obj(self):
        try:
            return getattr(self.__local__, self.__name__)
        except AttributeError:
            raise AttributeError("No object (name: %s) has been registered "
                                 "for this thread." % self.__name__)

    def set(self, obj):
        setattr(self.__local__, self.__name__, obj)
