class Song:
    def __init__(self, song_id: str, title: str, artist: str):
        self.song_id = song_id
        self.title = title
        self.artist = artist

    def __repr__(self):
        return f"<Song id={self.song_id} title={self.title} artist={self.artist}>"
    