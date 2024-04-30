from flask import Flask, render_template, request
from Database import makePlaylist, recentSongs

app = Flask(__name__)

@app.route('/')
def index():
    # Retrieve the recent songs from the database
    playlist = recentSongs()
    return render_template('index.html', playlist=playlist)

@app.route('/playlist/Random', methods=['POST'])
def randomPlaylist():
    # Generate a random playlist
    playlist = makePlaylist('')
    return render_template('playlist.html', genre='Random', playlist=playlist)

@app.route('/playlist/<genre>/', methods=['POST'])
def playlist(genre):
    # Generate a playlist based on the specified genre
    playlist = makePlaylist(genre)
    return render_template('playlist.html', genre=genre, playlist=playlist)

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
