from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import yt_dlp
import aiohttp
import json

app = FastAPI()

# Enable CORS to allow frontend requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SponsorBlock categories to skip
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

# Convert seconds to HH:MM:SS format
def format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"


# Fetch total skip duration for a single video from SponsorBlock API
async def fetch_sponsorblock_skip(session: aiohttp.ClientSession, video_id: str) -> int:
    url = f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}&categories={json.dumps(CATEGORIES)}"
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()
    except:
        return 0  # Return 0 if API fails or times out

    # Sum durations of all skip segments
    total_skip = sum((seg["segment"][1] - seg["segment"][0]) for seg in data)
    return int(total_skip)


# API endpoint to calculate playlist duration
@app.get("/playlist_length")
async def playlist_length(url: str):
    # yt-dlp options to extract metadata only, no download
    ydl_opts = {"extract_flat": True, "skip_download": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            raise HTTPException(
                status_code=400, detail="Failed to fetch playlist information"
            )

    entries = info.get("entries", [])
    if not entries:
        raise HTTPException(status_code=400, detail="Playlist is empty")

    # Collect video IDs and durations
    video_ids = [v["id"] for v in entries]
    durations = [int(v.get("duration", 0)) for v in entries]

    total_original, total_sponsorblock = 0, 0

    # Fetch SponsorBlock skip segments concurrently for all videos
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_sponsorblock_skip(session, vid) for vid in video_ids]
        skips = await asyncio.gather(*tasks)

    # Sum total durations with and without SponsorBlock skips
    for dur, skip in zip(durations, skips):
        total_original += dur
        total_sponsorblock += max(0, dur - skip)

    # Return response in HH:MM:SS format
    return {
        "original_duration": format_time(total_original),
        "sponsorblock_removed": format_time(total_sponsorblock),
        "videos_count": len(video_ids),
    }
