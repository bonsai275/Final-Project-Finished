from platform import release
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BOOLEAN, create_engine, ForeignKey, Column, String, Integer, CHAR, table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3
import random
from sqlalchemy import BOOLEAN
import re

Base = declarative_base()

class Songs(Base):
    __tablename__ = 'Songs'
    id = Column("id", Integer, primary_key=True)
    title = Column("title", String)
    artist = Column("artist", String)
    album = Column("album", String)
    genre = Column("genre", String)
    length = Column("length", String)
    year = Column("year", Integer)
    url = Column("url", String)
    has_genre = Column("has_genre", BOOLEAN, default=False)

    def __init__ (self, id, title, artist, album, genre, length, year, has_genre):
        self.id = id
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.length = length
        self.year = year
        self.has_genre = has_genre

    def __repr__(self):
        return "<Song('%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.id, self.title, self.artist, self.album, self.genre, self.length, self.year)

   
engine = create_engine("sqlite:///Songs.db", echo=True)
Base.metadata.create_all(bind = engine)
Session = sessionmaker(bind=engine)
session = Session()

def scrape_songs(url):
    """
    Scrapes songs from a given URL and adds them to the database.
    
    Args:
        url (str): The URL to scrape songs from.
    """
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Find all song elements
    songsOdd = soup.find_all('tr', class_ = 'odd')
    songsEven = soup.find_all('tr', class_ = 'even')
    print(songsOdd)
    for song in songsOdd:
        titleData = song.find_all('td')
        print("Scraping song..." + '\n')
        # The song title is in a td with class 'views-field views-field-title'
        title = titleData[1].text.strip()
        artist = titleData[2].text.strip()

        # Check if the song already exists in the database
        existing_song = session.query(Songs).filter(Songs.title == title, Songs.artist == artist).first()
        if existing_song:
            print("Song already exists in the database."+ '\n')
            continue

        # Create a new Song object and commit it to the database
        new_song = Songs(None, title, artist, None, None, None, None)
        session.add(new_song)
    for song in songsEven:
        titleData = song.find_all('td')
        print("Scraping song...")
        # The song title is in a td with class 'views-field views-field-title'
        title = titleData[1].text.strip()
        artist = titleData[2].text.strip()

        # Check if the song already exists in the database
        existing_song = session.query(Songs).filter(Songs.title == title, Songs.artist == artist).first()
        if existing_song:
            print("Song already exists in the database." + '\n')
            continue

        # Create a new Song object and commit it to the database
        new_song = Songs(None, title, artist, None, None, None, None)
        session.add(new_song)
    session.commit()

def flush_database():
    """
    Drops all tables in the database and recreates them.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
  
def get_song(title, artist):
    """
    Retrieves a song from the database based on its title and artist.
    
    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.
    
    Returns:
        Song: The song object if found, None otherwise.
    """
    song = session.query(Songs).filter(Songs.title == title, Songs.artist == artist).first()
    return song

def display_song(song):
    """
    Displays the details of a song.
    
    Args:
        song (Song): The song object to display.
    """
    songs = session.query(Songs).all()
    print(f"Id: {song.id}")
    print(f"Title: {song.title}")
    print(f"Artist: {song.artist}")
    print(f"Album: {song.album}")
    print(f"Genre: {song.genre}")
    print(f"Length: {song.length}")
    print(f"Year: {song.year}")
    print(f"URL: {song.url}")
    print("--------------------")

def create_song_urls():
    """
    Creates YouTube search URLs for all songs in the database.
    """
    base_url = "https://www.youtube.com/results?search_query="
    # Query all songs from the database
    songs = session.query(Songs).all()

    # Initialize an empty list to store the URLs
    song_urls = []

    # Iterate over all songs
    for song in songs:
        # Append the song title to the base URL
        song.url = base_url + song.title.replace(' ', '+') + "+by+" + song.artist.replace(' ', '+')
        display_song(song)
    session.commit()

class WikipediaScraper():
    def wikiScrape(self, song):
        """
        Scrapes additional information about a song from its Wikipedia page.
        
        Args:
            song (Song): The song object to scrape information for.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
        }
        print(song.url)
        page = requests.get(song.url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        tables = soup.findAll('th')
        for element in tables:
            if element.text == 'Genre' and song.genre == None:
                try:
                    genre = element.find_next_sibling('td').text
                    song.genre = genre
                    print('Genre: ' + genre)
                except AttributeError:
                    print('Genre not found')
            if element.text == 'Released' and song.year == None:
                try:
                    year = element.find_next_sibling('td').text
                    song.year = year
                    print('Year: ' + year)
                except AttributeError:
                    print('Year not found')
            if element.text == 'Length' and song.length == None:
                try:
                    length = element.find_next_sibling('td').text
                    song.length = length
                    print('Length: ' + length)
                except AttributeError:
                    print('Length not found')
            if element.text == 'Album' and song.album == None:
                try:
                    album = element.find_next_sibling('td').text
                    song.album = album
                    print('Album: ' + album)
                except AttributeError:
                    print('Album not found')
            if song.genre != None and song.year != None and song.length != None and song.album != None:
                print('Song fully scraped')
                break
        session.commit()

def makePlaylist(genre):
    """
    Creates a playlist of songs based on a given genre.
    
    Args:
        genre (str): The genre of the songs to include in the playlist.
    
    Returns:
        list: The list of songs in the playlist.
    """
    songs = session.query(Songs).all()
    print('Making playlist...')
    playlist = []
    while len(playlist) <= 50:
        random_song = random.choice(songs)
        if random_song.genre != None and genre.casefold() in random_song.genre.casefold():
            playlist.append(random_song)
            display_song(random_song)
    return playlist

def recentSongs():
    """
    Retrieves the most recent songs added to the database.
    
    Returns:
        list: The list of most recent songs.
    """
    songs = session.query(Songs).all()
    playlist = []
    while len(playlist) <= 25:
        playlist.append(songs[(len(songs) - 1) - len(playlist)])
    return playlist

def main():
    """
    Displays all songs in the database.
    """
    songs = session.query(Songs).all()
    for song in songs:
        display_song(song)
        
if __name__ == "__main__":
    main()

def create_song_urls(self):
    """
    Creates Wikipedia URLs for all songs in the database.
    
    Returns:
        list: The list of song URLs.
    """
    base_url = "https://en.wikipedia.org/wiki/"
    # Query all songs from the database
    songs = session.query(Songs).all()

    # Initialize an empty list to store the URLs
    song_urls = []

    # Iterate over all songs
    for song in songs:
        # Append the song title to the base URL
        #song.url = base_url + song.title.replace(' ', '_')
        # Append the song URL to the list
        song_urls.append(song.url)

    # Return the list of song URLs
    return song_urls

def checkData():
    """
    Checks the completeness of song data in the database.
    """
    completeSongs = 0
    missingAlbum = 0
    missingYear = 0
    missingGenre = 0
    hasGenre = 0
    songs = session.query(Songs).all()
    for song in songs:
        #display_song(song)
        if song.year != None and song.genre != None and song.length != None and song.album != None:
            completeSongs += 1
        if song.album == None:
            missingAlbum += 1
        if song.year == None:
            missingYear += 1
        if song.genre != None:
            song.has_genre = 1
            hasGenre += 1
        if song.genre == None:
            missingGenre += 1
    print(f"Number of complete songs: {completeSongs}")
    print(f"Number of songs missing album: {missingAlbum}")
    print(f"Number of songs missing year: {missingYear}")
    print(f"Number of songs missing genre: {missingGenre}")
    print(f"Number of songs with genre: {hasGenre}")

    start_date = datetime.date(1977, 6, 4)
    end_date = datetime.date(2024, 2, 20)
    delta = datetime.timedelta(days=7)
    deltaInt = int(delta.days)
    current_date = start_date
    while current_date <= end_date:
        print(current_date)
        url = 'https://musicchartsarchive.com/singles-chart/' + current_date.strftime("%Y-%m-%d")
        scrape_songs(url)
        print_songs()
        current_date += delta
