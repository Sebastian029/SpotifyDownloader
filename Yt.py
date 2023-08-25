from pytube import Search


class Downloader:
    @staticmethod
    def download(songs_list):

        if songs_list is None:
            return

        for index, song in enumerate(songs_list[0], 1):
            path = f'./Music/{songs_list[1].text}'

            print(str(index) + "/" + str(songs_list[2]) + ": " + song)
            yt_video = Search(song).results[0]
            var = yt_video.streams.get_audio_only()
            var.download(output_path=path)
        print("Download is complete")
