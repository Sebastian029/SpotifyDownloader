import Yt
import Sel

email = input("Enter login: ")
passw = input("Enter password: ")


downloader = Sel.SongsFinder(email, passw)
while True:
    songs_list = downloader.get_songs()
    if songs_list == -1:
        break
    Yt.Downloader.download(songs_list)

print("END")
