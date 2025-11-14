# Ad Generator Backend

FastAPI backend for AI-powered advertisement generation using Replicate.

## 📁 Simple Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── image_service.py  # Image generation logic
│   │   └── video_service.py  # Video generation logic
│   └── __init__.py
├── main.py               # FastAPI application
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## ✨ Features

- 🎨 AI image generation using SDXL via Replicate
- 🎥 AI video generation using Wan 2.1 via Replicate
- 🌐 RESTful API endpoints
- 🔒 CORS support for frontend integration
- 📁 Static file serving for generated media
- 🛡️ Error handling and validation

## 🚀 Setup Instructions

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Make sure `REPLICATE_API_TOKEN` is set in your `.env` file

3. **Start the server:**
   ```bash
   python main.py
   ```

4. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### POST /api/generate-ad
Generate advertisement (logo and optionally video).

**Request Body:**
```json
{
  "prompt": "eco-friendly water bottle",
  "generate_video": true
}
```

**Response:**
```json
{
  "success": true,
  "logo_url": "/output/logo_abc12345.png",
  "video_url": "/output/video_def67890.mp4",
  "message": "Advertisement generated successfully!",
  "prompt": "eco-friendly water bottle"
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "replicate_token_configured": true
}
```

### Static Files
- Generated images/videos are served from `/output/` directory

## 🎯 Frontend Integration

The frontend at `http://localhost:3000` will automatically connect to this backend at `http://localhost:8000`.

## 🚨 Error Handling

- **404**: Model not found on Replicate
- **500**: Server error during generation
- **400**: Invalid request parameters

## 📦 Dependencies

- **FastAPI**: Web framework
- **Replicate**: AI model API client
- **Pillow**: Image processing
- **FFmpeg-python**: Video processing
- **Python-dotenv**: Environment variable management