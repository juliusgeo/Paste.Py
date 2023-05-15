import os

from quart import Quart, render_template, request, redirect, jsonify
import random
import string
import time
import sqlite3
import bleach

conn = sqlite3.connect('snippets.db')

app = Quart(__name__)
snippets = {}

# "precomputed" durations in seconds. 5 minutes = 5 * 60 etc.
DURATION_OPTIONS = {
    'Never Expire': -1,
    '5 minutes': 300,
    '10 minutes': 600,
    '30 minutes': 1800,
    '1 hour': 3600,
    '2 hours': 7200,
    '5 hours': 18000,
    '12 hours': 43200,
    '24 hours': 86400,
    '1 week': 604800
}

allowed_extensions = [
    'txt', 'json', 'xml', 'yaml', 'yml', 'csv', 'conf', 'cfg', 'ini', 'log',
    'bat', 'cmd', 'sh', 'bash', 'ps1', 'psm1', 'psd1', 'r', 'py', 'pl', 'rb', 'java',
    'class', 'm', 'swift', 'go', 'scala', 'kt', 'kts', 'rs', 'lua', 'tcl', 'groovy',
    'gradle', 'php', 'php3', 'php4', 'php5', 'php7', 'phtml', 'html', 'htm', 'xhtml', 'jhtml',
    'md', 'markdown', 'rst', 'css', 'scss', 'sass', 'less', 'js', 'jsx', 'ts', 'tsx',
    'c', 'h', 'cpp', 'hpp', 'cxx', 'hxx', 'cc', 'hh', 'cs', 'vb',
    'sql', 'asm', 's', 'pas', 'f', 'for', 'f90', 'f95', 'f03', 'f08', 'f15', 'f18',
    'd', 'ada', 'nim', 'y', 'l', 'clj', 'cljs', 'cljc', 'edn', 'coffee', 'litcoffee', 'dart',
    'elm', 'haskell', 'hs', 'lhs', 'purs', 'perl', 'raku', 'rakumod', 'rakutest', '6pl', '6pm', 'nqp',
    'p6', 'p6l', 'p6m', 'pl6', 'pm6', 'php', 'php3', 'php4', 'php5', 'php7', 'phtml',
    'jl', 'matlab', 'm', 'octave', 'scilab', 'sce', 'sci', 'sage', 'wl', 'wls', 'nb'
]

def allowed_file(filename):
    filename, file_extension = os.path.splitext(filename)

    if file_extension in allowed_extensions:
        return True
    else:
        return False

def generate_url():
    # Generates a random URL consisting of lowercase letters and digits
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
async def home():
    return await render_template('index.html', duration_options=DURATION_OPTIONS, allowed_extensions=allowed_extensions)


@app.route('/save', methods=['POST'])
async def save_snippet():
    form = await request.form
    snippet = form['snippet']
    snippet = bleach.clean(snippet)  # sanitize user input
    snippet_name = form['snippetName']
    duration = int(form.get('duration', 0))
    url = generate_url()
    if duration == -1:
        expiration_time = -1
    else:
        expiration_time = time.time() + duration

    if not snippet_name.strip():
        error_message = 'The Snippet\'s name must not be empty!'
        return jsonify({'error': error_message})
    elif not snippet.strip():
        error_message = 'The Snippet\'s content must not be empty!'
        return jsonify({'error': error_message})

    try:
        conn.execute("INSERT INTO snippets (url, snippet, snippet_name, expires_at) VALUES (?, ?, ?, ?)",
                     (url, snippet, snippet_name, expiration_time))
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"{e}\nCould not find \"snippets.db\"")
        return jsonify(
            {'error': 'Internal Error: Database not found. Possible causes: Database is deleted or renamed.'})

    return redirect(f'/snippet/{url}')


@app.route('/snippet/<url>')
async def get_snippet(url):
  cursor = conn.execute("SELECT snippet, snippet_name, expires_at FROM snippets WHERE url = ?", (url,))
  row = cursor.fetchone()
  if row is not None:
    snippet_data = {'snippet': row[0], 'snippet_name': row[1], 'expires_at': row[2]}
    if snippet_data['expires_at'] != -1 and time.time() > snippet_data['expires_at']:
      conn.execute("DELETE FROM snippets WHERE url = ?", (url,))
      conn.commit()
      return "Snippet has expired!"
    snippet = snippet_data['snippet']
    snippet_name = snippet_data['snippet_name']
    return await render_template('snippet.html', snippet=snippet, snippet_name=snippet_name)
  else:
    return "Snippet not found!"

if __name__ == '__main__':
    conn.execute('''  
    CREATE TABLE IF NOT EXISTS snippets  
    (url TEXT PRIMARY KEY,  
    snippet TEXT NOT NULL,  
    snippet_name TEXT,  
    expires_at REAL NOT NULL);  
    ''')

    app.run(debug=False)
