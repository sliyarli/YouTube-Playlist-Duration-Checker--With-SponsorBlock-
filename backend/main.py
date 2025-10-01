from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import yt_dlp
import aiohttp
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SponsorBlock categories
CATEGORIES = [
    "sponsor",
    "intro",
    "outro",
    "selfpromo",
    "interaction",
    "preview",
    "music_offtopic",
    "tangent",
    "joke",
    "filler",
    "nonmusic",
]

# Format seconds to HH:MM:SS
def format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

# Fetch SponsorBlock skips for one video
async def fetch_sponsorblock_skip(session: aiohttp.ClientSession, video_id: str) -> int:
    url = f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}&categories={json.dumps(CATEGORIES)}"
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()
    except:
        return 0
    return int(sum((seg["segment"][1] - seg["segment"][0]) for seg in data))

# Batch processing helper
async def process_batch(session, video_ids, durations, batch_size=50):
    total_orig, total_sb = 0, 0

    # Split video_ids into chunks
    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i : i + batch_size]
        batch_durations = durations[i : i + batch_size]

        tasks = [fetch_sponsorblock_skip(session, vid) for vid in batch_ids]
        skips = await asyncio.gather(*tasks)

        for dur, skip in zip(batch_durations, skips):
            total_orig += dur
            total_sb += max(0, dur - skip)

    return total_orig, total_sb

# Main API endpoint
@app.get("/playlist_length")
async def playlist_length(url: str):
    ydl_opts = {"extract_flat": True, "skip_download": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            raise HTTPException(status_code=400, detail="Failed to fetch playlist info")

    entries = info.get("entries", [])
    if not entries:
        raise HTTPException(status_code=400, detail="Playlist is empty")

    video_ids = [v["id"] for v in entries]
    durations = [int(v.get("duration", 0)) for v in entries]

    async with aiohttp.ClientSession() as session:
        total_original, total_sponsorblock = await process_batch(session, video_ids, durations, batch_size=50)

    return {
        "original_duration": format_time(total_original),
        "sponsorblock_removed": format_time(total_sponsorblock),
        "videos_count": len(video_ids),
    }
