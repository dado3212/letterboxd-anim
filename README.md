# <img src='https://a.ltrbxd.com/logos/letterboxd-decal-dots-pos-rgb-500px.png' height='34' /> Letterboxd Animations

Make animations out of your Letterboxd profile. Currently this will take all films that you've given a rating to in your diary, sort it by time, and then render the distribution as it evolves. There's a number of settings in the script that you can tweak to generate the video.

## Run Instructions
I needed to import `imageio` to generate the MP4 file using the following two commands on Windows:
```
python3 -m pip install imageio
python3 -m pip install imageio[ffmpeg]
```

Then log in to your Letterboxd account and go to https://letterboxd.com/settings/data/. Export your data, and then copy the full contents of the `.zip` into the `export` folder. Then run `python3 .\create_gif.py`.

## Thanks

Thanks to Letterboxd for being a great service, and for the use of the [font](https://s.ltrbxd.com/fonts/Graphik-Regular-Web.woff) used for replicating the UI. All rights go to Letterboxd.
