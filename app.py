from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
import secrets
#import secrets
import os

dbuser=os.environ.get('DBUSER')
dbpass=os.environ.get('DBPASS')
dbhost=os.environ.get('DBHOST')
dbname=os.environ.get('DBNAME')

#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
conn="mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser,dbpass,dbhost,dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)

class xzhang270_nobelprizeinliterature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issued_year=db.Column(db.Integer)
    first_name=db.Column(db.String(255))
    last_name=db.Column(db.String(255))
    country=db.Column(db.String(255))
    language_used=db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | year: {1} | first name: {2} | last name: {3} | country: {4} | language: {5}".format(self.id, self.issued_year, self.first_name, self.last_name, self.country, self.language_used)

class NobelForm(FlaskForm):
    id = IntegerField('Winner ID: ', validators=[DataRequired()])
    issued_year = StringField('Year:', validators=[DataRequired()])
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    country= StringField('Country:', validators=[DataRequired()])
    language_used = StringField('Language:', validators=[DataRequired()])


@app.route('/')
def index():
    some_winners = xzhang270_nobelprizeinliterature.query.all()
    return render_template('index.html', winners=some_winners, pageTitle='Nobel Prize in Literature')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method=='POST':
        form=request.form
        search_value=form['search_string']
        search='%{}%'.format(search_value)
        results=xzhang270_nobelprizeinliterature.query.filter(or_(xzhang270_nobelprizeinliterature.issued_year.like(search),
                                                                  xzhang270_nobelprizeinliterature.first_name.like(search),
                                                                  xzhang270_nobelprizeinliterature.last_name.like(search),
                                                                  xzhang270_nobelprizeinliterature.country.like(search),
                                                                  xzhang270_nobelprizeinliterature.language_used.like(search))).all()
        return render_template('index.html', winners=results, pageTitle='Nobel Prize in Literature', legend='Search Results')
    else:
        return redirect('/')

@app.route('/add_winner', methods=['GET','POST'])
def add_winner():
    form = NobelForm()
    if form.validate_on_submit():
        winner=xzhang270_nobelprizeinliterature(issued_year=form.issued_year.data, first_name=form.first_name.data, last_name=form.last_name.data, country=form.country.data, language_used=form.language_used.data)
        db.session.add(winner)
        db.session.commit()
        return redirect('/')

    return render_template('add_winner.html', form=form, pageTitle='Add A New Winner')

@app.route('/delete_winner/<int:winner_id>', methods=['GET','POST'])
def delete_winner(winner_id):
    if request.method=='POST':
        winner=xzhang270_nobelprizeinliterature.query.get_or_404(winner_id)
        db.session.delete(winner)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

@app.route('/winner/<int:winner_id>', methods=['GET','POST'])
def get_winner(winner_id):
    winner=xzhang270_nobelprizeinliterature.query.get_or_404(winner_id)
    return render_template('winner.html', form=winner, pageTitle='Winner Details')

@app.route('/winner/<int:winner_id>/update', methods=['GET','POST'])
def update_winner(winner_id):
    winner=xzhang270_nobelprizeinliterature.query.get_or_404(winner_id)
    form=NobelForm()

    if form.validate_on_submit():
        winner.issued_year=form.issued_year.data
        winner.first_name=form.first_name.data
        winner.last_name=form.last_name.data
        winner.country=form.country.data
        winner.language_used=form.language_used.data
        db.session.commit()
        return redirect(url_for('get_winner', winner_id=winner.id))
    form.id.data=winner.id
    form.issued_year.data=winner.issued_year
    form.first_name.data=winner.first_name
    form.last_name.data=winner.last_name
    form.country.data=winner.country
    form.language_used.data=winner.language_used
    return render_template('update_winner.html', form=form, pageTitle='Update Winner', legend='Update A Winner')

if __name__ == '__main__':
    app.run(debug=True)
