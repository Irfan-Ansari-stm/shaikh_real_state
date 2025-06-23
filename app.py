from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Upload folder for property images
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLite configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'properties.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Property model
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100))

# Admin Login
@app.route('/god', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'shaikh' and request.form['password'] == 'shoiabshaikh#123@123':
            session['admin'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# Home Page - only featured or recent properties
@app.route('/')
def index():
    properties = Property.query.limit(4).all()
    for prop in properties:
        prop.formatted_price = "{:,}".format(prop.price)
    return render_template('index.html', properties=properties)

# All Properties - user can access via nav
@app.route('/all-properties')
def all_properties():
    properties = Property.query.all()
    for prop in properties:
        prop.formatted_price = "{:,}".format(prop.price)
    return render_template('all_properties.html', properties=properties)

# View Single Property
@app.route('/property/<int:property_id>')
def view_property(property_id):
    prop = Property.query.get_or_404(property_id)
    prop.formatted_price = "{:,}".format(prop.price)
    return render_template('property.html', prop=prop)

# Add Property
@app.route('/add', methods=['GET', 'POST'])
def add_property():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        price = int(request.form['price'])

        # Handle image upload
        image_file = request.files['image']
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        else:
            filename = None

        new_prop = Property(title=title, location=location, price=price, image=filename)
        db.session.add(new_prop)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_property.html')

# Edit Property
@app.route('/edit/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    prop = Property.query.get_or_404(property_id)

    if request.method == 'POST':
        prop.title = request.form['title']
        prop.location = request.form['location']
        prop.price = int(request.form['price'])

        # Optional image update
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            prop.image = filename

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_property.html', prop=prop)

# Delete Property
@app.route('/delete/<int:property_id>')
def delete_property(property_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    prop = Property.query.get_or_404(property_id)
    db.session.delete(prop)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/onepage')
def onepage():
    properties = Property.query.all()
    return render_template('onepage.html', properties=properties)



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/properties')
def all_propertiess():
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)

@app.route('/list', methods=['GET', 'POST'])
def list_property():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        price = int(request.form['price'])

        prop = Property(title=title, location=location, price=price)
        db.session.add(prop)
        db.session.commit()
        return redirect(url_for('all_properties'))

    return render_template('list_property.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# Initialize DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
