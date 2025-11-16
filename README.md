# 🎬 AI Ad Generator

A full-stack web application that generates professional advertisements (logos and videos) using Google Gemini AI. Built with React and FastAPI, featuring real-time job tracking, progress monitoring, and a modern dashboard interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🎨 **AI Logo Generation** - Create professional logos using Gemini 2.5 Flash Image model
- 🎥 **AI Video Generation** - Generate advertisement videos using Veo 3.1 model
- ⚡ **Asynchronous Processing** - Non-blocking job processing with real-time updates
- 📊 **Interactive Dashboard** - Track job progress, view history, and monitor status
- 🔄 **Real-time Updates** - WebSocket support for instant job status notifications
- 📱 **Responsive Design** - Modern, mobile-friendly user interface
- 💾 **Job Persistence** - JSON-based job storage with full history tracking
- 🎯 **Progress Tracking** - Real-time progress updates (0-100%)

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Google Gemini AI** - Logo and video generation
- **Python 3.8+** - Core programming language
- **WebSockets** - Real-time communication
- **Loguru** - Advanced logging
- **Pillow** - Image processing

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **CSS3** - Modern styling with custom properties
- **WebSocket Client** - Real-time updates

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ad-generator.git
cd ad-generator
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

Create a `.env` file in the `backend` directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Important:** Replace `your_google_api_key_here` with your actual Google Gemini API key.

## 🎯 Usage

### Starting the Backend Server

```bash
cd backend
python main.py
```

The backend server will start on `http://localhost:8000`

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Starting the Frontend

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### Using the Application

1. **Generate an Advertisement:**
   - Enter a prompt describing your advertisement (e.g., "eco-friendly water bottle")
   - Click "Generate Advertisement"
   - The system will create a job and return a job ID immediately

2. **View Dashboard:**
   - Automatically redirected to the dashboard after job creation
   - View all your generation jobs with real-time progress updates
   - See completed jobs with logo and video previews

3. **Track Progress:**
   - Jobs show progress percentage (0-100%)
   - Status indicators: Pending → Processing → Completed/Failed
   - Real-time updates via WebSocket and polling

## 📡 API Documentation

### Endpoints

#### `POST /api/generate-ad-async`
Start an asynchronous generation job.

**Request:**
```json
{
  "prompt": "eco-friendly water bottle",
  "generate_video": true,
  "user_id": "default"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "job_abc123def456",
  "message": "Generation job started. Use job ID to track progress.",
  "prompt": "eco-friendly water bottle"
}
```

#### `GET /api/job/{job_id}`
Get status of a specific job.

**Response:**
```json
{
  "success": true,
  "job_id": "job_abc123def456",
  "status": "completed",
  "progress": 100,
  "logo_url": "/output/logo_abc123.png",
  "video_url": "/output/video_def456.mp4",
  "error_message": null
}
```

#### `GET /api/jobs`
Get all jobs for a user.

**Query Parameters:**
- `user_id` (default: "default")
- `limit` (default: 50)

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "job_id": "job_abc123",
      "prompt": "eco-friendly water bottle",
      "status": "completed",
      "progress": 100,
      "logo_url": "/output/logo_abc123.png",
      "video_url": "/output/video_def456.mp4",
      "created_at": "2025-11-17T00:12:00",
      "completed_at": "2025-11-17T00:12:17"
    }
  ]
}
```

#### `GET /api/dashboard`
Get dashboard data with summary statistics.

**Query Parameters:**
- `user_id` (default: "default")

**Response:**
```json
{
  "summary": {
    "total": 10,
    "completed": 8,
    "pending": 1,
    "processing": 1,
    "failed": 0
  },
  "jobs": [...]
}
```

#### `DELETE /api/job/{job_id}`
Cancel a running job.

#### `WebSocket /ws`
Real-time job updates.

**Message Types:**
- `job_started` - New job created
- `job_completed` - Job finished successfully
- `job_failed` - Job encountered an error
- `job_cancelled` - Job was cancelled

## 📁 Project Structure

```
ad-generator/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── job_storage.py      # JSON-based job storage
│   │   └── services/
│   │       ├── job_service.py      # Background job processing
│   │       ├── image_service.py    # Gemini logo generation
│   │       └── video_service.py   # Gemini video generation
│   ├── output/                     # Generated files (logos & videos)
│   ├── jobs.json                   # Job database (JSON)
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── JobDashboard.jsx   # Dashboard component
│   │   │   └── JobDashboard.css
│   │   ├── App.jsx                 # Main application
│   │   ├── App.css
│   │   └── main.jsx                # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── CODE_FLOW_DIAGRAM.md            # Detailed code flow documentation
└── README.md                        # This file
```

## 🔄 How It Works

1. **User submits a prompt** through the frontend form
2. **Backend creates a job** and returns a job ID immediately
3. **Background processing** starts:
   - Logo generation using Gemini 2.5 Flash Image
   - Video generation using Veo 3.1 (if requested)
4. **Progress updates** are saved to `jobs.json` at each stage
5. **Dashboard polls** for updates every 2-5 seconds
6. **WebSocket notifications** provide real-time updates
7. **Files are saved** to `backend/output/` directory
8. **Completed jobs** display logo and video previews

## 🎨 Features in Detail

### Asynchronous Job Processing
- Jobs are processed in the background using Python's `asyncio`
- Non-blocking API responses for better user experience
- Thread pool execution for blocking AI API calls

### Real-time Progress Tracking
- Progress updates at key stages:
  - 10% - Job started
  - 30% - Logo generation started
  - 60% - Logo completed
  - 70% - Video generation started
  - 90% - Video completed
  - 100% - Job completed

### Job Management
- JSON-based storage for simplicity
- Full job history with timestamps
- Status tracking: `pending` → `processing` → `completed`/`failed`
- Error handling and recovery

## 🐛 Troubleshooting

### Backend Issues

**Issue:** `GOOGLE_API_KEY not found in environment`
- **Solution:** Create a `.env` file in the `backend` directory with your API key

**Issue:** Port 8000 already in use
- **Solution:** Change the port in `main.py` or stop the process using port 8000

**Issue:** Module not found errors
- **Solution:** Ensure virtual environment is activated and dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```

### Frontend Issues

**Issue:** Cannot connect to backend
- **Solution:** Ensure backend is running on `http://localhost:8000`

**Issue:** CORS errors
- **Solution:** Backend CORS is configured for `localhost:3000`. Update `main.py` if using a different port

**Issue:** npm install fails
- **Solution:** Ensure Node.js 16+ is installed. Try clearing cache:
  ```bash
  npm cache clean --force
  npm install
  ```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features
- Test your changes before submitting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://deepmind.google/technologies/gemini/) for AI generation capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [React](https://react.dev/) for the UI library
- [Vite](https://vitejs.dev/) for the build tool

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ using AI**

