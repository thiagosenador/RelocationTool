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

import ctypes
import json

from flask import current_app
from gcloud import datastore
import json
import ctypes


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
def list(entity, orderColumn):
    ds = get_client()
    query = ds.query(kind=entity, order=[orderColumn], namespace='Portkey')
    it = query.fetch()
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    return entities
# [END list]

# [START list Users]
def listEntities(key, columnName, limit=100, cursor=None):
     ds = get_client()
     query = ds.query(kind=key, order=columnName, namespace='Portkey')
     it = query.fetch(limit=limit, start_cursor=cursor)
     entities, more_results, cursor = it.next_page()
     entities = builtin_list(map(from_datastore, entities))
     return entities, cursor.decode('utf-8') if len(entities) == limit else None
# [END list Users]

# [START list users for countries]
def GetUsersAfterRemovingExceptions(users, countryName, countryPopulation):
    exceptionCountries = []
    population = 0
    for user in users:
        json_string = json.dumps(user)
        jsonObject = json.loads(json_string)
        for key in jsonObject:
            value = jsonObject[key]        
            if key == 'Preferences':
                for key in value:    
                    val1 = value[key]
                    if key == 'ExceptCountries':                        
                        exceptionCountries = val1
                    if key == 'Population':
                        population = val1

        if countryName in exceptionCountries or int(population) < int(countryPopulation):
            users.remove(user)

def GetCountryInformation(preferences, entities):
    if len(entities) <= 0: return
    json_string = json.dumps(entities[0])
    jsonObject = json.loads(json_string)
    for key in jsonObject:
        value = jsonObject[key]
        if key == 'CountryName':
            countryName = value 
        if key == 'Preferences':
            for key in value:    
                preferences[key] = value[key]            
                val1 = value[key]
    return countryName

def listPref(countryCode):
    ds = get_client()
    queryCountry = ds.query(kind='Country', namespace='Portkey')
    queryCountry.add_filter('Code', '=', countryCode)

    #query.projection = ['Preferences.Climate']
    preferences = {}
    it = queryCountry.fetch()
    #for task in query.fetch():
    #    preferences.append(task['Preferences.Climate'])
    entities, more_results, cursor = it.next_page()

    countryName = GetCountryInformation(preferences, entities)
    if countryName is None: return

    queryUser = ds.query(kind='User', namespace='Portkey')
    queryUser.add_filter('Preferences.Climate', '=', preferences.get('Climate'))
    queryUser.add_filter('Preferences.InternationalEducation', '=', preferences.get('InternationalEducation'))
    #ctypes.windll.user32.MessageBoxW(0, str(preferences.get('Population')), "pref", 1)
    #queryUser.add_filter('Preferences.Population', '<', int(preferences.get('Population')))
    it = queryUser.fetch()
    users, more_results, cursor = it.next_page()

    GetUsersAfterRemovingExceptions(users, countryName, int(preferences.get('Population')))

    return users
# [END list users for countries]

# [START list User countries]
def GetUserPreferences(limit=100, cursor=None, userName=""):
     ds = get_client()
     query = ds.query(kind='User', namespace='Portkey')
     query.add_filter('UserName', '=', userName)
     it = query.fetch(limit=limit, start_cursor=cursor)
     entities, more_results, cursor = it.next_page()
     entities = builtin_list(map(from_datastore, entities))
     preferences = []
     json_string = json.dumps(entities[0])
     jsonObject = json.loads(json_string)
     key = ds.key('User', namespace='Portkey')
     entity = datastore.Entity(key=key)     
     for key in jsonObject:
            value = jsonObject[key]
            entity[key]=value
            if key == 'Preferences':
                for key in value:
                    #ctypes.windll.user32.MessageBoxW(0, key, "key", 1)
                    val1 = value[key]
                    #ctypes.windll.user32.MessageBoxW(0, str(val1), "val1", 1)
                    entity[key]=val1     

     #ctypes.windll.user32.MessageBoxW(0, entity['Population'], "Population0", 1)

     return entity, cursor.decode('utf-8') if len(entities) == limit else None
# [END list user preferences]

# [START list countries by preferences]
def GetUserCountriesByPreferences(limit=100, cursor=None, preferences=object):
    population = str(preferences['Population'])
    ds = get_client()
    query = ds.query(kind='Country', namespace='Portkey')
    query.add_filter('Preferences.Climate', '=', preferences['Climate'])
    query.add_filter('Preferences.InternationalEducation', '=', preferences['InternationalEducation'])
    
    it = query.fetch(limit=limit, start_cursor=cursor)
    countries, more_results, cursor = it.next_page()
    countries = builtin_list(map(from_datastore, countries))
        
    countriesToRemove = []

    exceptCountryExists = False
    populationExists = False
    # Remove country exceptions
    if 'ExceptCountries' in preferences:
        exceptCountryExists = True

    if 'Population' in preferences:
        populationExists = True

    for country in countries:
        json_string = json.dumps(country['Preferences'])
        jsonObject = json.loads(json_string)
        if (exceptCountryExists and (country['CountryName'] in preferences['ExceptCountries'])) or (populationExists and (int(jsonObject['Population']) > int(population))):
            countriesToRemove.append(country)


    for countryToRemove in countriesToRemove: 
        countries.remove(countryToRemove)

    return countries, cursor.decode('utf-8') if len(countries) == limit else None
# [END list countries by preferences]

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


# [START createUserPreference]
def createUserPreference(data):
    ds = get_client()
    key = ds.key('User', namespace='Portkey')
    entity = datastore.Entity(key=key)

    embedded_key = ds.key('User')
    embedded_entity = datastore.Entity(key=embedded_key)
    embedded_entity['InternationalEducation'] = data['education'] == 'true' if 'education' in data else False
    embedded_entity['Population'] = int(data['population']) if data['population'] != '' else int('10000000000000')
    embedded_entity['Climate'] = data['climate']
    embedded_entity['ExceptCountries'] = data['exceptions'] if 'exceptions' in data else ''

    entity['UserName']=data['userName']
    entity['Preferences']=embedded_entity

    ds.put(entity)
    return from_datastore(entity)
# [END createUserPreference]


def delete(id):
    ds = get_client()
    key = ds.key('Book', int(id))
    ds.delete(key)
