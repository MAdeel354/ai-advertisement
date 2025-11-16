import React, { useState, useEffect } from 'react'
import './App.css'
import JobDashboard from './components/JobDashboard'

function App() {
  const [currentView, setCurrentView] = useState('generator') // 'generator' or 'dashboard'
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedLogo, setGeneratedLogo] = useState(null)
  const [generatedVideo, setGeneratedVideo] = useState(null)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [usingFallback, setUsingFallback] = useState(false)
  const [currentJobId, setCurrentJobId] = useState(null)
  const [ws, setWs] = useState(null)

  // Check if backend is available
  const checkBackendAvailability = async () => {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout

      const response = await fetch('http://localhost:8000/api/health', {
        signal: controller.signal,
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })

      clearTimeout(timeoutId)
      return response.ok
    } catch (error) {
      // Network error, timeout, or CORS issue
      return false
    }
  }

  // Call backend API with timeout and retry
  const callBackendAPI = async (requestData, retries = 2) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout for generation

        const response = await fetch('http://localhost:8000/api/generate-ad', {
          signal: controller.signal,
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Failed to generate advertisement')
        }

        const data = await response.json()
        return { success: true, data }

      } catch (error) {
        console.warn(`Backend API attempt ${attempt} failed:`, error.message)

        // If it's the last attempt, throw the error
        if (attempt === retries) {
          throw error
        }

        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
      }
    }
  }

  // Fallback to demo files
  const useFallbackFiles = () => {
    console.log('Using fallback demo files')
    console.log('Setting fallback video to: ./video.mp4')
    setUsingFallback(true)
    setGeneratedLogo('/logo.png')
    setGeneratedVideo('./video.mp4')
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) return

    setIsGenerating(true)
    setError(null)
    setSuccessMessage(null)
    setUsingFallback(false)

    try {
      // First, check if backend is available
      const isBackendAvailable = await checkBackendAvailability()

      if (!isBackendAvailable) {
        console.log('Backend not available, using fallback files')
        useFallbackFiles()
        setError('Backend server not running. Using demo files.')
        return
      }

      // Use async API for better UX
      const requestData = {
        prompt: prompt.trim(),
        generate_video: true,
        user_id: 'default'
      }

      const response = await fetch('http://localhost:8000/api/generate-ad-async', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      })

      if (!response.ok) {
        throw new Error('Failed to start generation job')
      }

      const result = await response.json()

      if (result.success) {
        setCurrentJobId(result.job_id)
        setSuccessMessage('To view recent jobs click dashboard')
        setError(null)

        // Switch to dashboard view after a short delay
        setTimeout(() => {
          setCurrentView('dashboard')
        }, 2000)
      } else {
        throw new Error(result.message || 'Failed to start job')
      }

    } catch (error) {
      console.error('Backend API failed:', error)

      // Determine error type
      if (error.name === 'AbortError') {
        setError('Request timeout. Backend is taking too long to respond. Using demo files.')
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        setError('Cannot connect to backend server. Using demo files.')
      } else {
        setError(`Backend error: ${error.message}. Using demo files.`)
      }

      // Fall back to demo files
      useFallbackFiles()
    } finally {
      setIsGenerating(false)
    }
  }

  const handleReset = () => {
    setPrompt('')
    setGeneratedLogo(null)
    setGeneratedVideo(null)
    setError(null)
    setSuccessMessage(null)
    setUsingFallback(false)
    setCurrentJobId(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-nav">
          <h1>🎬 Ad Generator</h1>
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${currentView === 'generator' ? 'active' : ''}`}
              onClick={() => setCurrentView('generator')}
            >
              🎨 Generator
            </button>
            <button
              className={`nav-tab ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              📊 Dashboard
            </button>
          </nav>
        </div>
        <p>Create stunning advertisements with AI</p>
      </header>

      <main className="main-content">
        {currentView === 'dashboard' ? (
          <JobDashboard />
        ) : (
          !generatedLogo && !generatedVideo ? (
          <div className="input-section">
            <form onSubmit={handleGenerate} className="prompt-form">
              <div className="input-group">
                <label htmlFor="prompt">Describe your advertisement:</label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., eco-friendly water bottle, luxury watch, coffee shop, fitness app..."
                  rows={4}
                  className="prompt-input"
                />
              </div>

              <button
                type="submit"
                className="generate-btn"
                disabled={!prompt.trim() || isGenerating}
              >
                {isGenerating ? (
                  <>
                    <span className="spinner"></span>
                    {usingFallback ? 'Loading Demo...' : 'Generating...'}
                  </>
                ) : (
                  'Generate Advertisement'
                )}
              </button>

              {successMessage && (
                <div className="success-message" style={{background: '#d1fae5', color: '#065f46', padding: '12px', borderRadius: '8px', marginTop: '16px'}}>
                  <p>✅ {successMessage}</p>
                </div>
              )}
              {error && (
                <div className="error-message">
                  <p>⚠️ {error}</p>
                </div>
              )}
            </form>

            <div className="examples">
              <h3>Example Prompts:</h3>
              <div className="example-cards">
                <div className="example-card" onClick={() => setPrompt('eco-friendly water bottle')}>
                  🌱 Eco-friendly water bottle
                </div>
                <div className="example-card" onClick={() => setPrompt('luxury watch brand')}>
                  ⌚ Luxury watch brand
                </div>
                <div className="example-card" onClick={() => setPrompt('artisan coffee shop')}>
                  ☕ Artisan coffee shop
                </div>
                <div className="example-card" onClick={() => setPrompt('fitness tracking app')}>
                  💪 Fitness tracking app
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="results-section">
            <div className="results-header">
              <h2>Generated Advertisement</h2>
              <p>Prompt: "{prompt}"</p>
              {usingFallback && (
                <span className="fallback-badge">📁 Demo Content</span>
              )}
              <button onClick={handleReset} className="new-ad-btn">
                Create New Ad
              </button>
            </div>

            <div className="results-grid">
              <div className="result-item">
                <h3>🖼️ Logo</h3>
                <div className="media-container">
                  <img
                    src={generatedLogo}
                    alt="Generated logo"
                    onError={(e) => {
                      e.target.src = '/output.png'
                    }}
                  />
                </div>
                <button className="download-btn" onClick={() => {
                  const link = document.createElement('a')
                  link.href = generatedLogo
                  link.download = 'logo.png'
                  link.click()
                }}>
                  Download Logo
                </button>
              </div>

              <div className="result-item">
                <h3>🎥 Advertisement Video</h3>
                <div className="media-container">
                  <video
                    key={generatedVideo}
                    controls
                    loop
                    muted
                    playsInline
                    preload="metadata"
                    width="100%"
                    style={{maxHeight: '400px'}}
                    onError={(e) => {
                      console.error('Video failed to load:', generatedVideo)
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                    onLoadedData={() => {
                      console.log('Video loaded successfully:', generatedVideo)
                    }}
                    onCanPlay={() => {
                      console.log('Video can play:', generatedVideo)
                    }}
                  >
                    <source src={generatedVideo} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                  <div className="video-error" style={{display: 'none'}}>
                    <p>Video not found</p>
                    <small>Make sure the video file exists</small>
                  </div>
                </div>
                <button className="download-btn" onClick={() => {
                  const link = document.createElement('a')
                  link.href = generatedVideo
                  link.download = './video.mp4'
                  link.click()
                }}>
                  Download Video
                </button>
              </div>
            </div>

            <div className="action-buttons">
              <button className="regenerate-btn" onClick={handleGenerate}>
                🔄 Regenerate with Same Prompt
              </button>
              <button className="edit-prompt-btn" onClick={() => {
                setGeneratedLogo(null)
                setGeneratedVideo(null)
                setUsingFallback(false)
              }}>
                ✏️ Edit Prompt
              </button>
            </div>
          </div>
        )
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by AI • Create professional advertisements in seconds</p>
      </footer>
    </div>
  )
}

export default App