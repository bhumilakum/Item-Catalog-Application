from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import datetime
import os
import sys
from werkzeug.utils import secure_filename

app = Flask(__name__)

# fetching client ID from JSON file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# connect to the database
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

# create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# set the path for image upload
UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# function to set allowed extention of image file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Making a JSON Endpoint (GET request)
@app.route('/catalog.json')
@app.route('/catalog.JSON')
def categoryItemJSON():
    category = session.query(Category).options(
        joinedload(Category.items)).all()
    return jsonify(Category=[(c.serialize, [i.serialize for i in c.items])
                             for c in category])


@app.route('/')
def categoryItem():
    """main page of application (home page)
    arguments: none
    returns: all categories with the latest added items
    """
    category = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.created)).limit(5)
    return render_template('category_list.html',
                           category=category, items=items)


@app.route('/login')
def showLogin():
    """login page providing user login with facebook and google accounts
    arguments: none
    returns: links to login with google account or with facebook account
    """
    if 'username' in login_session:
        flash("You are already logged in as %s" % login_session['username'])
        return redirect('/')

    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


def createUser(login_session):
    """User Helper Functions (to create new user)
    arguments: current login session data (username, email, picture)
    returns: current user id
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """User Helper Functions (to get user information)
    arguments: current user ID
    returns: current user information
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """User Helper Functions (to retrive userID)
    arguments: current user email
    returns: current user ID
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """google sign in method
    arguments: user informartion
    returns: allow login permissions
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
            -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are successfully logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Google account disconnect method
    arguments: current user information
    returns: disconnect current user and delete current login session
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke \
                    token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook account login method
    arguments: current user information
    returns: allow login permissions
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=\
            fb_exchange_token&client_id=%s&client_secret=%s&\
            fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    """
        Due to the formatting for the result from the server
        token exchange we have to split the token first on commas and
        select the first index which gives us the key : value
        for the server access token then we split it on colons to pull
        out the actual token value and replace the remaining quotes with
        nothing so that it can be used directly in the graph
        api calls
    """
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&\
            fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&\
            redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are successfully logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Facebook account disconnect method
        arguments: current user information
        returns: dissconnect current user, delete current user login session
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/logout')
def logout():
    """Dissconnect method based on providers (google or facebook)
        arguments: current user information
        returns: dissconnect current user, delete current user login session
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('categoryItem'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('categoryItem'))


@app.route('/catalog/<string:category_name>/items')
def showItems(category_name):
    """display items of specific category
    arguments: category name
    returns: items list of given category
    """
    # fetching all categories and specific category name of items to display
    category = session.query(Category).all()
    getCategoryName = session.query(Category).filter_by(name=category_name)\
        .first()
    if getCategoryName is not None:
        items = session.query(Item).filter_by(
            category_id=getCategoryName.id).order_by(desc(Item.created))
        return render_template('item_list.html',
                               category=category,
                               items=items,
                               category_name=category_name)
    else:
        items = session.query(Item).order_by(desc(Item.created)).limit(5)
        flash("Item not found!")
        return render_template('category_list.html',
                               category=category, items=items)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItemData(category_name, item_name):
    """display specific item description
    arguments: category name and item name
    returns: item description with edit and delete item links
    """
    getCategoryName = session.query(
        Category).filter_by(name=category_name).first()
    getItemName = session.query(Item).filter_by(
        category_id=getCategoryName.id, name=item_name).first()
    if (getCategoryName is None) or (getItemName is None):
        flash("Item not found")
        return redirect(url_for('categoryItem'))
    else:
        return render_template('item_description.html',
                               category=getCategoryName, item=getItemName)


@app.route('/catalog/items/add', methods=['GET', 'POST'])
def addItem():
    """form for adding new item of specific category with image
    arguments: form data
    returns: add item into database
    """
    # checking if user is logged in or not
    if 'username' not in login_session:
        flash("You can't access this page, please login first.")
        return redirect('/login')
    if request.method == 'POST':
        # save form data into database
        category_name = session.query(Category).filter_by(
            id=request.form['category']).first()
        if 'item_name' not in request.form or request.form['item_name'] == '':
            flash('Please enter item name.')
            return redirect(request.url)
        if 'description' not in request.form or \
                request.form['description'] == '':
            flash("Please enter item's short description.")
            return redirect(request.url)
        if 'price' not in request.form or request.form['price'] == '':
            flash('Please enter item price.')
            return redirect(request.url)
        if 'image' not in request.files:
            flash('No selected file.')
            return redirect(request.url)
        image_file = request.files['image']
        if image_file.filename == '':
            flash('No selected file.')
            return redirect(request.url)
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                         filename))
            newItem = Item(name=request.form['item_name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           created=datetime.datetime.now(),
                           category_id=request.form['category'],
                           image=filename,
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash("New item [%s] of category [%s] has been added successfully."
                  % (request.form['item_name'], category_name.name))
            return redirect(url_for('categoryItem'))
        else:
            flash("Please enter valid image file!")
            category = session.query(Category).all()
            return render_template("item_add.html",
                                   category=category, data=request.form)
    else:
        # render form to add new item data
        category = session.query(Category).all()
        return render_template("item_add.html", category=category)


@app.route('/catalog/<string:item_name>/edit', methods=['POST', 'GET'])
def editItem(item_name):
    """form for editing an existing item of specific category with image
    arguments: item data (item name)
    returns: edit an item data into the database
    """
    # checking if user is logged in or not
    if 'username' not in login_session:
        flash("You can't access this page, please login first.")
        return redirect('/login')
    itemToEdit = session.query(Item).filter_by(name=item_name).first()
    if (itemToEdit is None) or itemToEdit.user_id != login_session['user_id']:
        flash("You are not authorized to edit this item.")
        return redirect(url_for('categoryItem'))
    if request.method == 'POST':
        # edit existing item data into database
        if 'item_name' not in request.form or request.form['item_name'] == '':
            flash('Please enter item name.')
            return redirect(request.url)
        if 'description' not in request.form or \
                request.form['description'] == '':
            flash("Please enter item's short description.")
            return redirect(request.url)
        if 'price' not in request.form or request.form['price'] == '':
            flash('Please enter item price.')
            return redirect(request.url)
        if 'image' not in request.files:
            filename = itemToEdit.image
        else:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                             filename))
            else:
                flash("Please enter valid image file!")
                category = session.query(Category).all()
                return render_template("item_edit.html",
                                       item=itemToEdit, category=category)

        itemToEdit.name = request.form['item_name']
        itemToEdit.description = request.form['description']
        itemToEdit.price = request.form['price']
        itemToEdit.created = datetime.datetime.now()
        itemToEdit.category_id = request.form['category']
        itemToEdit.image = filename
        itemToEdit.user_id = login_session['user_id']
        session.add(itemToEdit)
        session.commit()
        flash("Item [%s] of category [%s] has been edited successfully."
              % (itemToEdit.name, itemToEdit.category.name))
        return redirect(url_for('showItemData',
                                category_name=itemToEdit.category.name,
                                item_name=itemToEdit.name))
    else:
        # render form to edit item data
        category = session.query(Category).all()
        return render_template('item_edit.html',
                               item=itemToEdit, category=category)


"""Delete an item with confirmation page
    arguments: item data (item name)
    returns: delete an item data from the database
"""


@app.route('/catalog/<string:item_name>/delete', methods=['POST', 'GET'])
def deleteItem(item_name):
    # checking if user is logged in or not
    if 'username' not in login_session:
        flash("You can't access this page, please login first.")
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(name=item_name).first()
    if (itemToDelete is None or
            itemToDelete.user_id != login_session['user_id']):
        flash("You are not authorized to delete this item.")
        return redirect(url_for('categoryItem'))
    if request.method == 'POST':
        # delete an item from the database
        category_name = itemToDelete.category.name
        session.delete(itemToDelete)
        session.commit()
        flash("Item [%s] of category [%s] has been deleted successfully."
              % (item_name, category_name))
        return redirect(url_for('showItems', category_name=category_name))
    else:
        # render page for asking conformation to delete an item
        return render_template('item_delete.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
