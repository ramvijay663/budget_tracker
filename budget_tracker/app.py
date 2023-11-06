from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)


app.secret_key = 'ramki663' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'budget_tracker_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


app.config['STATIC_FOLDER'] = 'static'


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ramki:ramki663@localhost/user_db'
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(10), nullable=False)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and user['password'] == password:
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
            return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return 'Welcome, ' + session['username']
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/main')
def main():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('main.html', transactions=transactions)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    name = request.form.get('name')
    amount = float(request.form.get('amount'))
    date = date.fromisoformat(request.form.get('date'))
    type = 'income' if request.form.get('type') == 'on' else 'expense'

    new_transaction = Transaction(name=name, amount=amount, date=date, type=type)
    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for('main'))

@app.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
