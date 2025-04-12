# <img src='https://a.ltrbxd.com/logos/letterboxd-decal-dots-pos-rgb-500px.png' height='34' /> Letterboxd Animations

Make animations out of your Letterboxd profile. Currently this will take all films that you've given a rating to in your diary, sort it by time, and then render the distribution as it evolves. There's a number of settings in the script that you can tweak to generate the video.

https://user-images.githubusercontent.com/8919256/236648196-ee632a7f-213f-4ab1-94bb-ddde9a6b59d9.mp4

## Run Instructions
I needed to import `imageio` to generate the MP4 file using the following two commands on Windows:
```
python3 -m pip install imageio
python3 -m pip install imageio[ffmpeg]
```

Then log in to your Letterboxd account and go to https://letterboxd.com/settings/data/. Export your data, and then copy the full contents of the `.zip` into the `export` folder. Then run `python3 .\create_gif.py`.

Alternatively if you're trying to create a monthly summary screenshot, open `python3 .\build_diary.py` and modify the `with_photos` line to whatever month you're trying to generate (note that this may fail if you watch more movies in a month than can render on one page in Letterboxd). Once this is done you can run `python3 .\build_diary.py` which will create an `index.html` file of whatever month you've specified. It will automatically lay it out to take advantage of the size of the window.

```
source ./venv/bin/activate
python build_diary.py
python create_gif.py
python graph.py
```

## Thanks

Thanks to Letterboxd for being a great service, and for the use of the [font](https://s.ltrbxd.com/fonts/Graphik-Regular-Web.woff) used for replicating the UI. All rights go to Letterboxd.
