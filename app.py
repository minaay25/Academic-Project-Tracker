import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
# Secret key for session management
app.secret_key = "academic_project_tracker_secret" 

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Dashboard (Home) Route [US1]
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db_connection()
    # Data Isolation: Only fetch projects belonging to the logged-in user
    projects = db.execute(
        'SELECT * FROM projects WHERE user_id = ? ORDER BY deadline ASC', 
        (session['user_id'],)
    ).fetchall()
    
    # Calculate remaining days for each project [US1 Business Logic]
    project_list = []
    today = datetime.now().date()
    
    for p in projects:
        p_dict = dict(p)
        deadline_date = datetime.strptime(p['deadline'], '%Y-%m-%d').date()
        delta = (deadline_date - today).days
        
        if delta < 0:
            p_dict['status'] = 'Overdue'
        else:
            p_dict['status'] = f"{delta} Days Remaining"
            
        project_list.append(p_dict)

    return render_template('dashboard.html', projects=project_list)

# Create Project Route [US1]
@app.route('/create_project', methods=('GET', 'POST'))
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        deadline = request.form['deadline']
        budget = request.form.get('budget', 0)
        
        db = get_db_connection()
        db.execute(
            'INSERT INTO projects (user_id, title, description, start_date, deadline, budget) VALUES (?, ?, ?, ?, ?, ?)',
            (session['user_id'], title, description, start_date, deadline, budget)
        )
        db.commit()
        return redirect(url_for('home'))
        
    return render_template('create_project.html')

# Register Route
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
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('login'))

        flash(error)

    return render_template('register.html')

# Login Route
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))

        flash(error)

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
# Project Detail Route [US2]
@app.route('/project/<int:project_id>', methods=('GET', 'POST'))
def project_detail(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db_connection()
    project = db.execute('SELECT * FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id'])).fetchone()
    
    if project is None:
        return redirect(url_for('home'))

    # Add new task
    if request.method == 'POST':
        description = request.form['description']
        if description:
            db.execute('INSERT INTO tasks (project_id, description) VALUES (?, ?)', (project_id, description))
            db.commit()
            return redirect(url_for('project_detail', project_id=project_id))

    tasks = db.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,)).fetchall()
    
    # Calculate Progress Percentage [US2 Business Logic]
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t['is_completed'])
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render_template('project_detail.html', project=project, tasks=tasks, progress=progress)

# Toggle Task Status Route [US2]
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
if __name__ == '__main__':
    app.run(debug=True)