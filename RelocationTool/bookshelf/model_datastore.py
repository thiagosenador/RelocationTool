# Copyright 2015 Google Inc.
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

from flask import current_app
from gcloud import datastore


builtin_list = list


def init_app(app):
    pass


def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]


# [START list]
def list(entity):
    ds = get_client()
    query = ds.query(kind=entity, namespace='Portkey')
    it = query.fetch()
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    return entities
# [END list]


def read(id):
    ds = get_client()
    key = ds.key('Book', int(id))
    results = ds.get(key)
    return from_datastore(results)


# [START update]
def update(entityName, data, id=None):
    ds = get_client()
    if id:
        key = ds.key(entityName, int(id), namespace='Portkey')
    else:
        key = ds.key(entityName, namespace='Portkey')

    entity = datastore.Entity(key=key)

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)

create = update
# [END update]


def delete(id):
    ds = get_client()
    key = ds.key('Book', int(id))
    ds.delete(key)
