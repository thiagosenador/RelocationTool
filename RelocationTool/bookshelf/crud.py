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

import json

from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for


crud = Blueprint('crud', __name__)

# [START welcome]
@crud.route("/")
def welcome():
    return render_template("welcome.html")
# [END welcome]

# [START list]
@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    books, next_page_token = get_model().list('Book', cursor=token)

    return render_template("list.html",
        books=books,
        next_page_token=next_page_token)

# [END list]

# [START show countries in dropdown]
@crud.route("/RelocationCountry", methods=['GET', 'POST'])
def listCountries():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    countries, next_page_token = get_model().listUsers(key='Country', columnName=['CountryName'], cursor=token)

    return render_template("RelocationCountry.html",
        countries=countries,
        next_page_token=next_page_token)

# [END show countries in dropdown]

# [START show potential employers]
@crud.route("/RelocationCountry", methods=['GET', 'POST'])
def listPotentialEmployers():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    employers, next_page_token = get_model().listUsers(key='Country', columnName=['CountryName'], cursor=token)

    return render_template("RelocationCountry.html",
        countries=countries,
        next_page_token=next_page_token)

# [END show potential employers]

# [START list Users]
@crud.route("/ShowUserPreferences", methods=['GET', 'POST'])
def listUsers():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    users, next_page_token = get_model().listUsers(key='User', columnName=['UserName'], cursor=token)

    return render_template("ShowUserPreferences.html",
        users=users,
        next_page_token=next_page_token)

# [END list Users]

# [START Get User countries]
@crud.route("/ShowUserPreferences/<username>", methods=['GET', 'POST'])
def getUserPreferences(username):
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    users, next_page_token = get_model().listUsers(key='User', columnName=['UserName'], cursor=token)
    preferences, next_page_token = get_model().GetUserPreferences(cursor=token, userName=username)

    return render_template(
        "ShowUserPreferences.html",
        users=users, preferences=preferences, next_page_token=next_page_token)
# [END Get User countries]

@crud.route('/<id>')
def view(id):
    book = get_model().read(id)
    return render_template("view.html", book=book)


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        book = get_model().create('Book', data)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Add", book={})
# [END add]


# [START createUser]
@crud.route('/createuser', methods=['GET', 'POST'])
def createUser():
    climateOptions = get_model().list('ClimateOptions', 'ClimateName')
    countries = get_model().list('Country', 'CountryName')
    
    if request.method == 'GET':
        return render_template("createUser.html", options=climateOptions, countries=countries)
    
    data = request.form.to_dict()
    data['exceptions'] = request.form.getlist('exceptCountries')

    user = get_model().createUserPreference(data)

    return render_template("createUser.html", options=climateOptions, countries=countries)
# [END createUser]


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    book = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        book = get_model().update(data, id)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Edit", book=book)


@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))
