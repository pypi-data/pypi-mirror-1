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

"""Object proxies are used for thread-local objects.
In the context of simplestore, each Python thread will
have its own MySQL connection."""

import threading

from simplestore.object_proxy import ObjectProxy

def test1():
    proxy = ObjectProxy('proxy')
    proxy.set(dict(foo='hello world'))
    assert 'foo' in proxy.keys()
    assert 'ObjectProxy' == proxy.__class__.__name__

class Foo(object):

    def __init__(self, name):
        self.name = name

def test2():
    proxy = ObjectProxy('foo')
    proxy.set(Foo('David'))
    assert 'David' == proxy.name
    assert 'ObjectProxy' == proxy.__class__.__name__

def test_threading():
    proxy = ObjectProxy('foo')

    class T(threading.Thread):

        def __init__(self, name):
            threading.Thread.__init__(self)
            self.name = name

        def run(self):
            proxy.set(Foo(self.name))
            self.proxy_object_id = id(proxy._obj())
            assert self.name == proxy.name
            assert 'ObjectProxy' == proxy.__class__.__name__

    t1 = T('David')
    t2 = T('Test')

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # this asserts that the two objects being proxied are unique to each thread.
    assert t1.proxy_object_id != t2.proxy_object_id
