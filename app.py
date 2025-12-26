from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "notice_secret"

def get_db():
    return sqlite3.connect("notice.db")

# Create table
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS notices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    category TEXT,
    expiry DATE
)
""")
conn.close()

# DISPLAY PAGE (AUTO-REFRESH + EXPIRY CHECK)
@app.route('/')
def display():
    today = str(date.today())
    conn = get_db()
    notices = conn.execute(
        "SELECT * FROM notices WHERE expiry >= ?", (today,)
    ).fetchall()
    conn.close()
    return render_template("display.html", notices=notices)

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin'] = True
            return redirect('/admin')
    return render_template("login.html")

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

# ADMIN PANEL
@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()

    if request.method == 'POST':
        conn.execute(
            "INSERT INTO notices(title,content,category,expiry) VALUES(?,?,?,?)",
            (
                request.form['title'],
                request.form['content'],
                request.form['category'],
                request.form['expiry']
            )
        )
        conn.commit()

    notices = conn.execute("SELECT * FROM notices").fetchall()
    conn.close()
    return render_template("admin.html", notices=notices)

# DELETE NOTICE
@app.route('/delete/<int:id>')
def delete(id):
    if 'admin' not in session:
        return redirect('/login')
    conn = get_db()
    conn.execute("DELETE FROM notices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# EDIT NOTICE
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if 'admin' not in session:
        return redirect('/login')

    conn = get_db()

    if request.method == 'POST':
        conn.execute("""
            UPDATE notices 
            SET title=?, content=?, category=?, expiry=?
            WHERE id=?
        """, (
            request.form['title'],
            request.form['content'],
            request.form['category'],
            request.form['expiry'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect('/admin')

    notice = conn.execute("SELECT * FROM notices WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", notice=notice)

if __name__ == '__main__':
    app.run(debug=True)
