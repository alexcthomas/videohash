# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Videohash** is a Python package for near-duplicate video detection via perceptual hashing. It generates a 64-bit hash per video that remains stable across resizing, transcoding, watermarking, frame rate changes, and aspect ratio changes. Requires FFmpeg to be installed on the system.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests (with coverage)
pytest

# Run a single test
pytest tests/test_videohash.py::TestClassName::test_method_name

# Lint
flake8 videohash/

# Type check
mypy

# Format code
black .
```

## Architecture

The core is the `VideoHash` class in `videohash/videohash.py`. Each instance:

1. Creates an isolated working directory (unique `task_uid`) with subdirs: `video/`, `downloadedvideo/`, `frames/`, `tiles/`, `collage/`, `horizontally_concatenated_image/`
2. Downloads the video (via `downloader.py` → yt-dlp) or copies a local file
3. Extracts frames at `frame_interval` fps using FFmpeg (`framesextractor.py`)
4. Builds a square collage from frames (`collagemaker.py`) — wavelet-hashed to produce a 64-bit `whash_bitlist`
5. Builds a horizontal strip of frames, slices it into 64 tiles (`tilemaker.py`), and analyzes dominant color per tile → `dominant_color_bitlist`
6. Final hash = XOR of the two 64-bit lists

**Hash robustness** comes from combining two independent perceptual signals. Similarity threshold is 15% bit-flip tolerance (≤9 bits different out of 64).

### Key modules

| File | Role |
|---|---|
| `videohash/videohash.py` | Core `VideoHash` class; hash computation, comparison operators (`==`, `!=`, `-`), `is_similar()` |
| `videohash/framesextractor.py` | FFmpeg subprocess to extract frames; raises `FFmpegError` subclasses |
| `videohash/collagemaker.py` | Assembles frames into square collage (rounds to nearest perfect square grid) |
| `videohash/tilemaker.py` | Slices horizontal frame strip into 64 tiles for dominant color analysis |
| `videohash/downloader.py` | yt-dlp subprocess for URL downloads; supports worst-quality option |
| `videohash/videoduration.py` | Parses FFmpeg output to get video duration |
| `videohash/exceptions.py` | Full exception hierarchy rooted at `VideoHashError` |
| `videohash/utils.py` | Small helpers: file listing, path checks, temp dir creation |

### Public API (exported from `__init__.py`)

- `VideoHash(path=..., url=..., storage_path=..., download_worst=False, frame_interval=1)`
- `video_duration(path)` — standalone duration helper
- All exception classes

## Code Style

- Max line length: 127 characters (flake8)
- Formatter: black
- Type annotations used throughout; checked with mypy
- Ignore list for mypy: `numpy`, `imagehash`, `imagedominantcolor`, `image_slicer`
