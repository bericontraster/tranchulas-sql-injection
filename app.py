import sqlite3
import time
import os
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'org.db')

EMPLOYEES = [
    (1, 'Alice Johnson', 'CEO', 'Management'),
    (2, 'Bob Smith', 'CTO', 'Technology'),
    (3, 'Carol White', 'CFO', 'Finance'),
    (4, 'Dave Brown', 'HR Manager', 'Human Resources')
]

USERS = [
    {'username': 'alice', 'password': 'password1', 'name': 'Alice Johnson'},
    {'username': 'bob', 'password': 'password2', 'name': 'Bob Smith'}
]

# setup database
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, role TEXT, department TEXT)')
    c.executemany('INSERT INTO employees VALUES (?, ?, ?, ?)', EMPLOYEES)
    conn.commit()
    conn.close()

# helper to load templates
def render_template(name, **context):
    path = os.path.join('templates', name)
    with open(path, 'r') as f:
        content = f.read()
    for k, v in context.items():
        content = content.replace('{' + k + '}', str(v))
    return content.encode()

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path.startswith('/static/'):
        return serve_static(environ, start_response, path)
    if path == '/sql-lab':
        return sql_lab(environ, start_response)
    if path == '/nosql-lab':
        return nosql_lab(environ, start_response)
    else:
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [render_template('index.html')]

def serve_static(environ, start_response, path):
    filepath = path.lstrip('/')
    if not os.path.exists(filepath):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not found']
    with open(filepath, 'rb') as f:
        data = f.read()
    start_response('200 OK', [('Content-Type', 'text/css')])
    return [data]

def sql_lab(environ, start_response):
    qs = parse_qs(environ.get('QUERY_STRING', ''))
    id_value = qs.get('id', [''])[0]
    result_html = ''
    if id_value:
        conn = sqlite3.connect(DB_PATH)
        def sleep(x):
            time.sleep(float(x))
            return 0
        conn.create_function('sleep', 1, sleep)
        c = conn.cursor()
        query = f"SELECT id, name, role, department FROM employees WHERE id = {id_value}"
        try:
            rows = c.execute(query).fetchall()
            if rows:
                result_html = '<ul>' + ''.join(f'<li>{row[1]} - {row[2]} ({row[3]})</li>' for row in rows) + '</ul>'
            else:
                result_html = '<p>No employee found.</p>'
        except sqlite3.Error as e:
            result_html = f'<p>Error: {e}</p>'
        conn.close()
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [render_template('sql_lab.html', id=id_value, result=result_html)]

def nosql_lab(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        length = int(environ.get('CONTENT_LENGTH', '0'))
        body = environ['wsgi.input'].read(length).decode()
        params = parse_qs(body)
        username_raw = params.get('username', [''])[0]
        password_raw = params.get('password', [''])[0]
        try:
            username = json.loads(username_raw)
        except json.JSONDecodeError:
            username = username_raw
        try:
            password = json.loads(password_raw)
        except json.JSONDecodeError:
            password = password_raw
        query = {'username': username, 'password': password}
        user = find_user(query)
        if user:
            result_html = f'<p>Welcome {user["name"]}!</p>'
        else:
            result_html = '<p>Invalid credentials.</p>'
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [render_template('nosql_lab.html', username=username_raw, password=password_raw, result=result_html)]
    else:
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [render_template('nosql_lab.html', username='', password='', result='')]

def match_condition(value, condition):
    if isinstance(condition, dict):
        if '$ne' in condition:
            return value != condition['$ne']
        if '$eq' in condition:
            return value == condition['$eq']
        return False
    else:
        return value == condition

def find_user(query):
    for user in USERS:
        match = True
        for k, v in query.items():
            if k not in user or not match_condition(user[k], v):
                match = False
                break
        if match:
            return user
    return None

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with make_server('', port, application) as httpd:
        print(f'Serving on port {port}...')
        httpd.serve_forever()
