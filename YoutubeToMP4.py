from pytube import YouTube

path_to_save = "C:/Users/justi/Documents/Graduate Classes/Cloud Computing/Project/Youtube Videos"

links = \
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        "https://www.youtube.com/watch?v=ZD9gQiwqR2A&ab_channel=beINSPORTSUSA",
        "https://www.youtube.com/watch?v=ZcyCul68A7Q&ab_channel=BBCEarth",
        "https://www.youtube.com/watch?v=YFCpCajop9k&ab_channel=LoLEsports",

    ]

# https://pytube.io/en/latest/user/quickstart.html

for link in links:
    yt = YouTube(link)

    mp4 = yt.streams.filter(file_extension='mp4').get_by_resolution("720p").download(output_path=path_to_save)

