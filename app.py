from quart import Quart, render_template, request, redirect
import random
import string
import time

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
    duration = int(form.get('duration', 0))
    url = generate_url()
    expiration_time = time.time() + duration
    snippets[url] = {
        'snippet': snippet,
        'expires_at': expiration_time
    }
    return redirect('/snippet/' + url)

@app.route('/snippet/<url>')
async def get_snippet(url):
    if url in snippets:
        snippet_data = snippets[url]
        if 'expires_at' in snippet_data and time.time() > snippet_data['expires_at']:
            del snippets[url]
            return "Snippet has expired!"
        snippet = snippet_data['snippet']
        return await render_template('snippet.html', snippet=snippet)
    else:
        return "Snippet not found!"

if __name__ == '__main__':
    app.run(debug=True)
