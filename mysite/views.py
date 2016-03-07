from mysite import app
from mysite import db
from mysite.models import DrugDB
from sqlalchemy import or_
from flask import Flask, request, render_template
from mysite.forms import SearchForm
from mysite.page_functions import get_examples

app.test_request_context().push()

@app.route('/drugs/', methods=["GET", "POST"])
def search():
    search_term = None
    results = []
    form = SearchForm()
    if request.method == 'POST':
        search_term = form.search_term.data
        results = DrugDB.query.filter(or_(DrugDB.p_name.like('%'+search_term+'%'), DrugDB.s_name.like('%'+search_term+'%'))).all()
        form.search_term.data = ''
    return render_template('/drugs/index.html', form=form, search_term=search_term, results=results)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/drugs/<search_term>')
def result(search_term):
    return render_template('drugs/result.html', search_term=search_term)

@app.route('/resume/')
def resume():
    return render_template('resume.html')

@app.route('/')
def index():
    examples = get_examples()
    return render_template('index.html', examples=examples)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404