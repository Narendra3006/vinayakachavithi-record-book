from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# === Ensure DB exists ===
def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('CREATE TABLE credit (id INTEGER PRIMARY KEY, name TEXT, amount INTEGER)')
        c.execute('CREATE TABLE debit (id INTEGER PRIMARY KEY, item TEXT, amount INTEGER)')
        conn.commit()
        conn.close()

init_db()

# === Home Page ===
@app.route('/')
def home():
    return render_template('index.html')

# === Dashboard (Public View) ===
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    credit_data = c.execute('SELECT * FROM credit').fetchall()
    debit_data = c.execute('SELECT * FROM debit').fetchall()
    conn.close()
    total_credit = sum([row[2] for row in credit_data])
    total_debit = sum([row[2] for row in debit_data])
    balance = total_credit - total_debit
    return render_template('dashboard.html', credit_data=credit_data, debit_data=debit_data,
                           total_credit=total_credit, total_debit=total_debit, balance=balance)

# === Admin Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'youthgpl':
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

# === Admin Logout ===
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('dashboard'))

# === Add Credit ===
@app.route('/add_credit', methods=['POST'])
def add_credit():
    if 'admin' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    amount = request.form['amount']
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO credit (name, amount) VALUES (?, ?)', (name, amount))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# === Add Debit ===
@app.route('/add_debit', methods=['POST'])
def add_debit():
    if 'admin' not in session:
        return redirect(url_for('login'))
    item = request.form['item']
    amount = request.form['amount']
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO debit (item, amount) VALUES (?, ?)', (item, amount))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# === Delete Credit ===
@app.route('/delete_credit/<int:id>')
def delete_credit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM credit WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# === Delete Debit ===
@app.route('/delete_debit/<int:id>')
def delete_debit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM debit WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# === Edit Credit ===
@app.route('/edit_credit/<int:id>', methods=['GET', 'POST'])
def edit_credit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        conn.execute('UPDATE credit SET name = ?, amount = ? WHERE id = ?', (name, amount, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    credit = conn.execute('SELECT * FROM credit WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_credit.html', credit=credit)

# === Edit Debit ===
@app.route('/edit_debit/<int:id>', methods=['GET', 'POST'])
def edit_debit(id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    if request.method == 'POST':
        item = request.form['item']
        amount = request.form['amount']
        conn.execute('UPDATE debit SET item = ?, amount = ? WHERE id = ?', (item, amount, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    debit = conn.execute('SELECT * FROM debit WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_debit.html', debit=debit)

if __name__ == '__main__':
    app.run(debug=True)
