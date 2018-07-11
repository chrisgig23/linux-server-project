from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, Users
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('/var/www/catalogApp/catalogApp/client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Sporting Goods Application"

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = create_engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login
@app.route('/login')
def showLogin():
    # Load Login HTML template
    state = ''.join(random.choice(
                string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalogApp/catalogApp/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Disconnect from google account
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                   json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = (
        'https://accounts.google.com/o/oauth2/revoke?token=%s'
        % login_session['access_token']
        )
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    # If disconnect is successful, delete all user items
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/logout')
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    # Load logout HTML template
    return render_template('logout.html')


# JSON APIs to view Sporting Goods Information
@app.route('/catalog/<int:category_id>/JSON')
def categoryJSON(category_id):
    # Returns JSON endpoint for category
    categoryItems = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(categoryItems=[c.serialize for c in categoryItems])


@app.route('/catalog/<int:category_id>/<int:item_id>/JSON')
def categoryItemJSON(category_id, item_id):
    # Returns JSON endpoint for categoryItem
    category_item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(category_item=category_item.serialize)


@app.route('/catalog/JSON')
def catalogJSON():
    # Returns JSON endpoint for catalog
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Loads catalog HTML template
    categories = session.query(Category).all()
    items = (
            session.query(CategoryItem)
            .order_by(CategoryItem.timeAdded.desc()).limit(10).all()
            )
    return render_template(
                        'catalog.html',
                        categories=categories,
                        items=items,
                        session=login_session)


# Display category and all items associated with that category
@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    # Loads page for a specific category
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    categoryItems = session.query(
                    CategoryItem).filter_by(category_id=category.id)

    # Check if user is logged in
    if 'username' not in login_session:
        return render_template(
                            'publiccategory.html',
                            categories=categories,
                            category=category,
                            items=categoryItems)
    else:
        return render_template(
                            'category.html',
                            categories=categories,
                            category=category,
                            items=categoryItems)


@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategory():
    # If user is logged in, load form for adding new category
    if 'username' not in login_session:
        # If user is not logged in, direct them to login page
        flash("You must be logged in to do that")
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
                                name=request.form['title'],
                                user_id=getUserId(login_session['email']))
        if session.query(Category).filter_by(name=newCategory.name).count():
            flash("That category already exists, new category not created")
            return redirect(url_for('showCatalog'))
        session.add(newCategory)
        session.commit()
        flash("New Category Successfully Added")
        return redirect(url_for(
                                'showCategory',
                                category_name=newCategory.name))
    else:
        return render_template('newcategory.html')


@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    if 'username' not in login_session:
        # If user is not logged in, direct them to login page
        flash("You must be logged in to do that")
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    creator = getUserInfo(category.user_id)
    if (creator.id != login_session['user_id']):
        # If user did not create the category, they cannot delete
        flash("You are not authorized to delete this category.")
        return redirect(url_for('showCatalog'))
    deletedCategory = session.query(
                        Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        # Delete all items linked to category, then delete category
        deletedItems = session.query(
                        CategoryItem).filter_by(name=category_name).all()
        for i in deletedItems:
            session.delete(i)
        session.delete(deletedCategory)
        session.commit()
        flash("Category successfully deleted")
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
                            'deleteCategory.html',
                            category_name=category_name,
                            category=deletedCategory)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    # Loads Item detail page
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if (('username' not in login_session) or
       (creator.id != login_session['user_id'])):
        return render_template('publicitem.html', category=category, item=item)
    else:
        return render_template(
                            'item.html',
                            category=category,
                            item=item,
                            creator=creator)


@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
    if 'username' not in login_session:
        flash("You must be logged in to do that")
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=category_name).one()
        newItem = CategoryItem(
                            name=request.form['title'],
                            description=request.form['description'],
                            category_id=category.id,
                            user_id=getUserId(login_session['email']))
        # Check if item exists, if so, do not add to DB
        if session.query(CategoryItem).filter_by(name=newItem.name).count():
            flash("That item already exists, new item not created")
            return redirect(url_for(
                            'showCategory',
                            category_name=category_name))
        session.add(newItem)
        session.commit()
        flash("New item successfully added")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        listOfCategories = session.query(Category).all()
        return render_template(
                            'newItem.html',
                            category_name=category_name,
                            listOfCategories=listOfCategories)


@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_name):
    # Edit item's name, description, and category
    if 'username' not in login_session:
        flash("You must be logged in to do that")
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    creator = getUserInfo(item.user_id)
    if (creator.id != login_session['user_id']):
        # If user did not create the item, they cannot edit
        flash("You are not authorized to edit this item.")
        return redirect(url_for('showCategory', category_name=category_name))
    editedItem = session.query(CategoryItem).filter_by(name=item_name).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.name = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']

        session.add(editedItem)
        session.commit()
        flash("Item successfully edited")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        listOfCategories = session.query(Category).all()
        return render_template(
                            'editItem.html',
                            category_name=category_name,
                            item_name=item_name,
                            item=editedItem,
                            listOfCategories=listOfCategories)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        flash("You must be logged in to do that")
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    deletedItem = session.query(CategoryItem).filter_by(name=item_name).one()
    creator = getUserInfo(deletedItem.user_id)
    if (creator.id != login_session['user_id']):
        # If user did not create the item, they cannot edit
        flash("You are not authorized to delete this item.")
        return redirect(url_for('showCategory', category_name=category_name))
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Item successfully deleted")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template(
                            'deleteItem.html',
                            category_name=category_name,
                            item_name=item_name,
                            item=deletedItem)


# If user does not exist, create new user
def createUser(login_session):
    newUser = Users(
                    name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    users = session.query(Users).filter_by(email=login_session['email']).one()
    return users.id

# Function takes in user id, and returns a user object
def getUserInfo(user_id):
    users = session.query(Users).filter_by(id=user_id).one()
    return users

# Function takes in user email, and returns user id
def getUserId(email):
    try:
        users = session.query(Users).filter_by(email=email).one()
        return users.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
