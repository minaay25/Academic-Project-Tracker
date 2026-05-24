import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
# İş mantığı fonksiyonlarımızı içeri aktarıyoruz
from business_logic import get_deadline_status, calculate_progress, calculate_remaining_budget

app = Flask(__name__)
app.secret_key = "academic_project_tracker_secret" 

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db_connection()
    projects = db.execute(
        'SELECT * FROM projects WHERE user_id = ? ORDER BY deadline ASC', 
        (session['user_id'],)
    ).fetchall()
    
    project_list = []
    today = datetime.now().date()
    
    for p in projects:
        p_dict = dict(p)
        # [US1] Mantığı business_logic.py'den geliyor
        p_dict['status'] = get_deadline_status(p['deadline'], today)
        project_list.append(p_dict)

    return render_template('dashboard.html', projects=project_list)

@app.route('/create_project', methods=('GET', 'POST'))
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        deadline = request.form['deadline']
        
        try:
            budget = float(request.form.get('budget', 0) or 0)
        except ValueError:
            budget = 0.0
        
        db = get_db_connection()
        db.execute(
            'INSERT INTO projects (user_id, title, description, start_date, deadline, budget) VALUES (?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, start_date, deadline, budget)
        )
        db.commit()
        return redirect(url_for('home'))
        
    return render_template('create_project.html')

@app.route('/project/<int:project_id>', methods=('GET', 'POST'))
def project_detail(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    project = db.execute('SELECT * FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id'])).fetchone()
    
    if project is None:
        return redirect(url_for('home'))

    if request.method == 'POST':
        description = request.form.get('description')
        if description:
            db.execute('INSERT INTO tasks (project_id, description) VALUES (?, ?)', (project_id, description))
            db.commit()
            return redirect(url_for('project_detail', project_id=project_id))

    tasks = db.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,)).fetchall()
    expenses = db.execute('SELECT * FROM expenses WHERE project_id = ?', (project_id,)).fetchall()
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t['is_completed'])
    
    # [US2] Mantığı business_logic.py'den geliyor
    progress = calculate_progress(total_tasks, completed_tasks)

    project_budget = float(project['budget'] or 0)
    total_expenses = sum(float(e['cost'] or 0) for e in expenses)
    
    # [US3] Mantığı business_logic.py'den geliyor
    remaining_budget = calculate_remaining_budget(project_budget, total_expenses)

    return render_template(
        'project_detail.html', 
        project=project, 
        project_budget=project_budget, 
        tasks=tasks, 
        progress=progress,
        expenses=expenses,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget
    )

@app.route('/add_expense/<int:project_id>', methods=['POST'])
def add_expense(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    item_name = request.form['item_name']
    
    try:
        cost = float(request.form['cost'] or 0)
    except ValueError:
        cost = 0.0
    
    if item_name:
        db = get_db_connection()
        db.execute('INSERT INTO expenses (project_id, item_name, cost) VALUES (?, ?, ?)', (project_id, item_name, cost))
        db.commit()
        
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    expense = db.execute('''
        SELECT e.id, e.project_id 
        FROM expenses e 
        JOIN projects p ON e.project_id = p.id 
        WHERE e.id = ? AND p.user_id = ?
    ''', (expense_id, session['user_id'])).fetchone()

    if expense:
        db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        db.commit()
        return redirect(url_for('project_detail', project_id=expense['project_id']))
        
    return redirect(url_for('home'))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    task = db.execute('''
        SELECT t.id, t.is_completed, t.project_id 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ? AND p.user_id = ?
    ''', (task_id, session['user_id'])).fetchone()

    if task:
        new_status = 0 if task['is_completed'] else 1
        db.execute('UPDATE tasks SET is_completed = ? WHERE id = ?', (new_status, task_id))
        db.commit()
        return redirect(url_for('project_detail', project_id=task['project_id']))
        
    return redirect(url_for('home'))

@app.route('/edit_project/<int:project_id>', methods=('GET', 'POST'))
def edit_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    project = db.execute('SELECT * FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id'])).fetchone()
    
    if project is None:
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        deadline = request.form['deadline']
        
        try:
            budget = float(request.form.get('budget', 0) or 0)
        except ValueError:
            budget = 0.0
        
        db.execute(
            'UPDATE projects SET title = ?, description = ?, start_date = ?, deadline = ?, budget = ? WHERE id = ?',
            (title, description, start_date, deadline, budget, project_id)
        )
        db.commit()
        return redirect(url_for('home'))
        
    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    project = db.execute('SELECT id FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id'])).fetchone()

    if project:
        db.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
        db.execute('DELETE FROM expenses WHERE project_id = ?', (project_id,))
        db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        db.commit()
        
    return redirect(url_for('home'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('login'))

        flash(error)
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        error = None
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user is None or user['password'] != password:
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))

        flash(error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)