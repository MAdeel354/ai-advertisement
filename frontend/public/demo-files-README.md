# Demo Files for Fallback

Place your demo files here:

## Required Files:

1. **logo.png** - Demo logo image (720x720px recommended)
2. **ad.mp4** - Demo advertisement video (4 seconds recommended)

## How to Add Demo Files:

1. Create or obtain a sample logo image and save it as `logo.png`
2. Create or obtain a sample advertisement video and save it as `ad.mp4`
3. Place both files in this `public/` directory

## Purpose:

These files are used as fallback content when:
- The backend server is not running
- The API call fails or times out
- Network connectivity issues occur

The frontend will automatically try the backend API first, and if it fails, it will display these demo files with a "📁 Demo Content" badge.