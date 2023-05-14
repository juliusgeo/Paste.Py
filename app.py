from quart import Quart, render_template, request, redirect, jsonify
import random
import string
import time
import sqlite3
import bleach

conn = sqlite3.connect('snippets.db')

app = Quart(__name__)
snippets = {}

DURATION_OPTIONS = {
    '5 minutes': 5 * 60,
    '10 minutes': 10 * 60,
    '30 minutes': 30 * 60,
    '1 hour': 60 * 60,
    '2 hours': 2 * 60 * 60,
    '5 hours': 5 * 60 * 60,
    '12 hours': 12 * 60 * 60,
    '24 hours': 24 * 60 * 60,
    '1 week': 7 * 24 * 60 * 60
}

def generate_url():
    # Generates a random URL consisting of lowercase letters and digits
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
async def home():
    return await render_template('index.html', duration_options=DURATION_OPTIONS)


@app.route('/save', methods=['POST'])
async def save_snippet():
    form = await request.form
    snippet = form['snippet']
    snippet = bleach.clean(snippet)  # sanitize user input
    snippet_name = form['snippetName']
    duration = int(form.get('duration', 0))
    url = generate_url()
    expiration_time = time.time() + duration

    if not snippet_name.strip():
        error_message = 'The Snippet\'s name must not be empty!'
        return jsonify({'error': error_message})
    elif not snippet.strip():
        error_message = 'The Snippet\'s content must not be empty!'
        return jsonify({'error': error_message})

    conn.execute("INSERT INTO snippets (url, snippet, snippet_name, expires_at) VALUES (?, ?, ?, ?)",
                 (url, snippet, snippet_name, expiration_time))
    conn.commit()
    return redirect(f'/snippet/{url}')



@app.route('/snippet/<url>')
async def get_snippet(url):
    cursor = conn.execute("SELECT snippet, snippet_name, expires_at FROM snippets WHERE url = ?", (url,))
    row = cursor.fetchone()
    if row is not None:
        snippet_data = {'snippet': row[0], 'snippet_name': row[1], 'expires_at': row[2]}
        if time.time() > snippet_data['expires_at']:
            conn.execute("DELETE FROM snippets WHERE url = ?", (url,))
            conn.commit()
            return "Snippet has expired!"
        snippet = snippet_data['snippet']
        snippet_name = snippet_data['snippet_name']
        return await render_template('snippet2.html', snippet=snippet, snippet_name=snippet_name)
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

    app.run(debug=True)
