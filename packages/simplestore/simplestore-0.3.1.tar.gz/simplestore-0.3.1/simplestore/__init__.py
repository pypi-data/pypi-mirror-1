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

from simplestore.datastore import __entities_table__

entities_table = """
CREATE TABLE IF NOT EXISTS %s (
    added_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id CHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    fields MEDIUMBLOB,
    UNIQUE KEY (id),
    KEY (created_at)
) ENGINE=InnoDB;
""" % __entities_table__
