# YouTube Playlist Duration Checker - With SponsorBlock

[Live App](https://you-tube-playlist-duration-checker.vercel.app/)

---

## Overview

**YouTube Playlist Duration Checker** is a web application that allows you to calculate the total duration of any YouTube playlist while automatically excluding segments like sponsor messages, intros, outros, jokes, tangents, and more using **SponsorBlock**.  

The app provides both:

- **Original Duration**: Total length of all videos in the playlist.  
- **SponsorBlock Removed Duration**: Real viewing time after skipping all unwanted segments.  

It is designed to be fast, accurate, and user-friendly, giving you precise results for even large playlists.

---

## Features

- Supports all SponsorBlock categories: `sponsor`, `intro`, `outro`, `selfpromo`, `interaction`, `preview`, `music_offtopic`, `tangent`, `joke`, `filler`, `nonmusic`.
- Real-time calculation for playlists of any size.
- Modern and responsive UI with clear duration display.
- Fully online – just paste your playlist URL and get results instantly.
- Backend powered by **FastAPI** + **yt-dlp**, frontend in **HTML/CSS/JS**.

---

## How It Works

1. **Frontend**: Enter your YouTube playlist URL in the input box.
2. **Backend**:
   - Fetches playlist metadata using `yt-dlp` (no video download required).
   - Queries the **SponsorBlock API** to get all skip segments for each video.
   - Calculates the total original duration and SponsorBlock-adjusted duration.
3. **Result**: Displays the number of videos, total original duration, and total SponsorBlock-removed duration in a clean HH:MM:SS format.

---


## Technologies Used

- **Backend**: Python, FastAPI, yt-dlp, aiohttp  
- **Frontend**: HTML, CSS, JavaScript  
- **Hosting**: (example) Render (backend), Vercel/Netlify (frontend)  
- **SponsorBlock API** for skipping unwanted video segments  

---

## Usage

1. Go to the [Live App](https://you-tube-playlist-duration-checker.vercel.app/).  
2. Paste your YouTube playlist URL into the input field.  
3. Click **Check Duration**.  
4. View your playlist's original duration and SponsorBlock-adjusted duration instantly.

## Copying Someone Else’s Playlist

If you want to analyze a playlist that isn’t public, you can copy it to a new playlist you own:

Take the URL of the other person’s playlist, e.g.:

https://www.youtube.com/playlist?list=PLxxxxxx


Replace www with music in the URL:

https://music.youtube.com/playlist?list=PLxxxxxx


On YouTube Music, click the three dots on the playlist and select Add all to playlist to copy it to your own account.

Use the URL of your new playlist in the app.
