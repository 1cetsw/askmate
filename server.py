from flask import Flask, render_template, redirect, request, url_for, session, flash
import data_manager
import datetime
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt as bcrypt
from connection import connect_login
app = Flask(__name__)
app.secret_key = 'lubie0placki'



latest_opened_question_id = 0


@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index():
    latest_questions = data_manager.get_latest_questions(5)
    return render_template('index.html', questions=latest_questions)



@app.route("/list")
def route_to_all_questions():
    sorted_questions = data_manager.sort_questions_by_time()
    if 'loggedin' in session:
        return render_template('all_questions.html', questions=sorted_questions)
    return render_template('please_login.html')

@app.route('/search', methods=['POST'])
def search():
    search_phrase = request.form.get('search_phrase')
    questions = data_manager.search_in_questions(search_phrase)
    answers = data_manager.search_in_answers(search_phrase)
    if 'loggedin' in session:
        return render_template('search.html', search_phrase=search_phrase, questions=questions, answers=answers)
    return render_template('please_login.html')

@app.route('/question/<question_id>')
def display_question(question_id):
    global latest_opened_question_id
    latest_opened_question_id = question_id
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_all_answers_by_id_ordered_by_vote_number(question_id)
    comments = data_manager.get_all_comments()
    if 'loggedin' in session:
        return render_template('display_question.html', question=question, answers=answers, comments=comments)
    return render_template('please_login.html')


@app.route('/questions/<question_id>/vote-up', methods=['POST'])
def question_vote_up(question_id):
    data_manager.vote_up_for_questions(question_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/questions/<question_id>/vote-down', methods=['POST'])
def question_vote_down(question_id):
    data_manager.vote_down_for_questions(question_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answers/<question_id>/<answer_id>/vote-up', methods=['POST'])
def answer_vote_up(question_id, answer_id):
    data_manager.vote_up_for_answers(answer_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/questions/<question_id>/<answer_id>/vote-down', methods=['POST'])
def answer_vote_down(question_id, answer_id):
    data_manager.vote_down_for_answers(answer_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if 'loggedin' in session:
        if request.method == "GET":
            return render_template('new_question.html')
    return render_template('please_login.html')

    new_question_all_data = data_manager.add_new_question()
    new_question_all_data.update(
        {
            'title': request.form.get('question'),
            'message': request.form.get('message'),
            'image': request.form.get('image')
        }
    )
    data_manager.write_to_questions(new_question_all_data)
    if 'loggedin' in session:
        return redirect(url_for('display_question', question_id=new_question_all_data['id']))
    return render_template('please_login.html')

@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == "GET":
        question = data_manager.get_question_by_id(question_id)
        return render_template('edit_question.html', question=question)

    edited_question_data = {
            'title': request.form.get('question'),
            'message': request.form.get('message'),
            'image': request.form.get('image')
            }
    data_manager.edit_question(question_id, edited_question_data)
    if 'loggedin' in session:
        return redirect(url_for('display_question', question_id=question_id))
    return render_template('please_login.html')

@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == "GET":
        question = data_manager.get_question_by_id(question_id)
        return render_template('add_comment_to_question.html', question=question)

    new_comment_to_question = {
        'message': request.form.get('comment'),
        'type': 'question',
        'question_id': question_id
        }
    data_manager.write_to_comments(new_comment_to_question)
    global latest_opened_question_id
    if 'loggedin' in session:
        return redirect(url_for('display_question', question_id=latest_opened_question_id))
    return render_template('please_login.html')

@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question_by_id(question_id)
    if 'loggedin' in session:
        return redirect(url_for('route_to_all_questions'))
    return render_template('please_login.html')

@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def add_new_answer(question_id):
    if request.method == "GET":
        return render_template("new_answer.html", question_id=question_id)

    new_answer = request.form["new_answer"]
    data_manager.add_new_answer(new_answer, question_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    if request.method == "GET":
        answer = data_manager.get_answer_by_id(answer_id)
        return render_template('edit_answer.html', answer=answer)

    question_id = data_manager.get_answer_by_id(answer_id)['question_id']
    edited_answer_data = {
            'message': request.form.get('message'),
            'image': request.form.get('image')
            }
    data_manager.edit_answer(answer_id, edited_answer_data)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<answer_id>/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id, question_id):
    if request.method == "GET":
        answer = data_manager.get_answer_by_id(answer_id)
        question = data_manager.get_question_by_id(question_id)
        return render_template('add_comment_to_answer.html', answer=answer, question=question)

    new_comment_to_answer = {
        'message': request.form.get('comment'),
        'type': 'answer',
        'answer_id': answer_id
        }
    data_manager.write_to_comments(new_comment_to_answer)
    global latest_opened_question_id
    return redirect(url_for('display_question', question_id=latest_opened_question_id))


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    data_manager.delete_answer_by_id(answer_id)
    global latest_opened_question_id
    return redirect(url_for('display_question', question_id=latest_opened_question_id))


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == "GET":
        comment = data_manager.get_comment_by_id(comment_id)
        return render_template('edit_comment.html', comment=comment)

    comment = data_manager.get_comment_by_id(comment_id)
    if comment['question_id']:
        question_id = comment['question_id']
    else:
        question_id = data_manager.get_answer_by_id(comment['answer_id'])['question_id']
    edited_comment_data = {
        'message': request.form.get('message'),
        'edited_count': comment['edited_count'] + 1 if type(comment['edited_count']) is int else 1}
    data_manager.edit_comment(comment_id, edited_comment_data)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<comment_id>/delete')
def delete_comment(comment_id):
    data_manager.delete_comment_by_id(comment_id)
    global latest_opened_question_id
    return redirect(url_for('display_question', question_id=latest_opened_question_id))

@app.route('/ester_egg')
def ester_egg():
    if 'loggedin' in session:
        return render_template('ester_egg.html')
    return render_template('please_login.html')

# LOGGED ENGINE _______________________________________________________________________________--
# conn = connect_login()
#
# def home():
#     if 'loggedin' in session:
#         return render_template('index.html', username=session['username'])
#     return redirect(url_for('login'))
#
#
# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         print(password)
#         cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
#         account = cursor.fetchone()
#
#         if account:
#             password_rs = account['password']
#             print(password_rs)
#             if check_password_hash(password_rs, password):
#                 session['loggedin'] = True
#                 session['id'] = account['id']
#                 session['username'] = account['username']
#                 return redirect(url_for('index'))
#             else:
#                 flash('Incorrect username/password')
#         else:
#             flash('Incorrect username/password')
#
#     return render_template('login.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
#
#         fullname = request.form['fullname']
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#
#         _hashed_password = generate_password_hash(password)
#
#
#         cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
#         account = cursor.fetchone()
#         print(account)
#
#         if account:
#             flash('Account already exists!')
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             flash('Invalid email address!')
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             flash('Username must contain only characters and numbers!')
#         elif not username or not password or not email:
#             flash('Please fill out the form!')
#         else:
#
#             cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
#                            (fullname, username, _hashed_password, email))
#             conn.commit()
#             flash('You have successfully registered!')
#     elif request.method == 'POST':
#
#         flash('Please fill out the form!')
#
#     return render_template('register.html')
#
#
# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('index'))
#
#
# @app.route('/profile')
# def profile():
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#
#     if 'loggedin' in session:
#         cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
#         account = cursor.fetchone()
#         return render_template('profile.html', account=account)
#     return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
