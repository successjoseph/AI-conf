# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# Set up database connection
conn = sqlite3.connect('code_snippets.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
)
''')

# Create folder for templates
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create index.html file in the templates directory
with open('templates/index.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Code Snippet Manager</title>
</head>
<body>
    <h1>Code Snippets</h1>
    <a href="/add_snippet">Add New Snippet</a><br>
    <a href="/add_project">Add New Project</a><br>
    {% for snippet in snippets %}
        <p>{{ snippet.title }} - {{ snippet.content }}</p>
    {% endfor %}
</body>
</html>''')

# Create routes
@app.route('/')
def index():
    return render_template('index.html', snippets=cursor.execute("SELECT * FROM snippets").fetchall())

@app.route('/add_snippet', methods=['POST'])
def add_snippet():
    project_id = request.form['project']
    title = request.form['title']
    content = request.form['content']
    tags = request.form.getlist('tags')
    
    cursor.execute("INSERT INTO snippets (project_id, title, content, tags) VALUES (?, ?, ?, ?)",
                  (project_id, title, content, ', '.join(tags)))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/add_project', methods=['POST'])
def add_project():
    name = request.form['name']
    cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)