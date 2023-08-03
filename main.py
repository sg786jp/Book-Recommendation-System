import os
import mysql.connector
import numpy as np
from flask import Flask, render_template, request, redirect, session
import pickle

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database Conn
conn = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="user_data")
cursor = conn.cursor()

# Importing PIckle files
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))


@app.route('/')
def login():
    return render_template("Login.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/home')
def home():
    if 'id' in session:
        return render_template('Home.html')
    return redirect('/')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password")
    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
                   .format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['id'] = users[0][0]
        return redirect('/home')
    else:
        return redirect('/')


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute("""INSERT INTO `users` (`id`, `username`, `email`, `password`) 
                      VALUES (NULL, '{}', '{}', '{}')""".format(name, email, password))

    conn.commit()

    return redirect('/home')


@app.route('/Top_Books')
def top_books():
    return render_template('Top_Books.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))


@app.route('/Recommend')
def recommend_ui():
    if 'id' in session:
        return render_template('Recommend.html')
    return redirect('/')


@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('Recommend.html', data=data)


@app.route('/About')
def About():
    if 'id' in session:
        return render_template('About.html')
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
