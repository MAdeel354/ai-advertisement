import React, { useState, useEffect, useCallback } from 'react'
import './JobDashboard.css'

const JobDashboard = () => {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedJob, setSelectedJob] = useState(null)
  const [ws, setWs] = useState(null)

  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs?user_id=default&limit=50')
      if (!response.ok) {
        throw new Error('Failed to fetch jobs')
      }

      const data = await response.json()
      if (data.success) {
        setJobs(data.jobs || [])
      }
    } catch (error) {
      console.error('Error fetching jobs:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const setupWebSocket = useCallback(() => {
    try {
      const websocket = new WebSocket('ws://localhost:8000/ws')

      websocket.onopen = () => {
        console.log('WebSocket connected')
        setWs(websocket)
      }

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('WebSocket message:', data)

        // Refresh jobs when we get job updates
        if (data.type === 'job_started' || data.type === 'job_completed' || data.type === 'job_failed' || data.type === 'job_cancelled') {
          fetchJobs()
        }
      }

      websocket.onclose = () => {
        console.log('WebSocket disconnected')
        setWs(null)
        // Try to reconnect after 3 seconds
        setTimeout(setupWebSocket, 3000)
      }

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.log('WebSocket not available, using polling instead')
      // Fall back to polling every 5 seconds
      const interval = setInterval(fetchJobs, 5000)
      return () => clearInterval(interval)
    }
  }, [fetchJobs])

  // Fetch jobs on component mount
  useEffect(() => {
    fetchJobs()
    setupWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [fetchJobs, setupWebSocket])

  // Poll for processing jobs more frequently
  useEffect(() => {
    const hasProcessingJobs = jobs.some(job => job.status === 'processing' || job.status === 'pending')
    
    if (hasProcessingJobs) {
      // Poll every 2 seconds if there are processing jobs to update progress
      const interval = setInterval(() => {
        fetchJobs()
      }, 2000)
      
      return () => clearInterval(interval)
    } else {
      // Poll every 5 seconds if no processing jobs (for new jobs)
      const interval = setInterval(() => {
        fetchJobs()
      }, 5000)
      
      return () => clearInterval(interval)
    }
  }, [jobs, fetchJobs])

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981'
      case 'processing':
        return '#3b82f6'
      case 'pending':
        return '#f59e0b'
      case 'failed':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'processing':
        return '⚡'
      case 'pending':
        return '⏳'
      case 'failed':
        return '❌'
      default:
        return '📋'
    }
  }

  const cancelJob = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/job/${jobId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchJobs() // Refresh the jobs list
      }
    } catch (error) {
      console.error('Error cancelling job:', error)
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getProgressWidth = (progress) => {
    return `${Math.min(100, Math.max(0, progress))}%`
  }

  if (loading) {
    return (
      <div className="job-dashboard loading">
        <div className="loading-spinner"></div>
        <p>Loading your generation history...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="job-dashboard error">
        <p>❌ Error loading jobs: {error}</p>
        <button onClick={fetchJobs} className="retry-btn">Try Again</button>
      </div>
    )
  }

  return (
    <div className="job-dashboard">
      <div className="dashboard-header">
        <h2>📊 Generation History</h2>
        <div className="dashboard-stats">
          <span>Total Jobs: {jobs.length}</span>
          <span>Completed: {jobs.filter(j => j.status === 'completed').length}</span>
          <span>Processing: {jobs.filter(j => j.status === 'processing').length}</span>
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎨</div>
          <h3>No generation jobs yet</h3>
          <p>Start creating your first advertisement to see it here!</p>
        </div>
      ) : (
        <div className="jobs-container">
          {jobs.map((job) => (
            <div key={job.job_id} className="job-card" onClick={() => setSelectedJob(job)}>
              <div className="job-header">
                <div className="job-info">
                  <span className="job-id">{job.job_id}</span>
                  <span
                    className="job-status"
                    style={{ color: getStatusColor(job.status) }}
                  >
                    {getStatusIcon(job.status)} {job.status}
                  </span>
                </div>
                <div className="job-meta">
                  <span className="job-time">{formatTime(job.created_at)}</span>
                  {job.job_type === 'both' && (
                    <span className="job-type">🎬 Logo + Video</span>
                  )}
                  {job.job_type === 'logo' && (
                    <span className="job-type">🖼️ Logo Only</span>
                  )}
                </div>
              </div>

              <div className="job-prompt">
                <strong>Prompt:</strong> {job.prompt}
              </div>

              {job.status === 'processing' && (
                <div className="job-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: getProgressWidth(job.progress) }}
                    ></div>
                  </div>
                  <span className="progress-text">{job.progress}%</span>
                </div>
              )}

              {(job.logo_url || job.video_url) && (
                <div className="job-results">
                  {job.logo_url && (
                    <div className="result-item">
                      <span>🖼️ Logo Generated</span>
                    </div>
                  )}
                  {job.video_url && (
                    <div className="result-item">
                      <span>🎥 Video Generated</span>
                      <a
                        href={`http://localhost:8000${job.video_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          marginLeft: '8px',
                          fontSize: '12px',
                          color: '#3b82f6',
                          textDecoration: 'underline'
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        View
                      </a>
                    </div>
                  )}
                </div>
              )}

              {job.error_message && (
                <div className="job-error">
                  <span>⚠️ {job.error_message}</span>
                </div>
              )}

              <div className="job-actions">
                {job.status === 'processing' && (
                  <button
                    className="cancel-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      cancelJob(job.job_id)
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Job Details Modal */}
      {selectedJob && (
        <div className="job-modal" onClick={() => setSelectedJob(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Job Details: {selectedJob.job_id}</h3>
              <button className="close-btn" onClick={() => setSelectedJob(null)}>×</button>
            </div>

            <div className="modal-body">
              <div className="detail-row">
                <strong>Status:</strong>
                <span style={{ color: getStatusColor(selectedJob.status) }}>
                  {getStatusIcon(selectedJob.status)} {selectedJob.status}
                </span>
              </div>

              <div className="detail-row">
                <strong>Prompt:</strong> {selectedJob.prompt}
              </div>

              <div className="detail-row">
                <strong>Created:</strong> {formatTime(selectedJob.created_at)}
              </div>

              {selectedJob.started_at && (
                <div className="detail-row">
                  <strong>Started:</strong> {formatTime(selectedJob.started_at)}
                </div>
              )}

              {selectedJob.completed_at && (
                <div className="detail-row">
                  <strong>Completed:</strong> {formatTime(selectedJob.completed_at)}
                </div>
              )}

              {selectedJob.logo_url && (
                <div className="detail-row">
                  <strong>Logo:</strong>
                  <a href={`http://localhost:8000${selectedJob.logo_url}`} target="_blank" rel="noopener noreferrer">
                    View Logo
                  </a>
                </div>
              )}

              {selectedJob.video_url && (
                <div className="detail-row">
                  <strong>Video:</strong>
                  <div style={{marginTop: '10px'}}>
                    {/* Video Player */}
                    {selectedJob.video_url.endsWith('.mp4') ? (
                      <div style={{marginBottom: '15px'}}>
                        <video
                          controls
                          style={{
                            width: '100%',
                            maxWidth: '600px',
                            height: 'auto',
                            borderRadius: '8px',
                            border: '1px solid #ddd'
                          }}
                          onError={(e) => {
                            console.error('Video loading error:', e);
                            e.target.style.display = 'none';
                          }}
                        >
                          <source src={`http://localhost:8000${selectedJob.video_url}`} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                        <p style={{fontSize: '12px', color: '#6b7280', marginTop: '5px'}}>
                          (Demo Video - Placeholder for AI Generated Content)
                        </p>
                      </div>
                    ) : (
                      <div style={{background: '#f3f4f6', padding: '10px', borderRadius: '6px', marginBottom: '15px'}}>
                        <p style={{margin: 0, fontSize: '14px', color: '#6b7280'}}>
                          Video format: {selectedJob.video_url.endsWith('.html') ? '(Demo HTML)' : '(Demo File)'}
                        </p>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div style={{display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap'}}>
                      <a
                        href={`http://localhost:8000${selectedJob.video_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          background: '#3b82f6',
                          color: 'white',
                          padding: '8px 16px',
                          borderRadius: '6px',
                          textDecoration: 'none',
                          fontSize: '14px'
                        }}
                      >
                        🎥 Open in New Tab
                      </a>
                      <a
                        href={`http://localhost:8000${selectedJob.video_url}`}
                        download=""
                        style={{
                          background: '#10b981',
                          color: 'white',
                          padding: '8px 16px',
                          borderRadius: '6px',
                          textDecoration: 'none',
                          fontSize: '14px'
                        }}
                      >
                        ⬇️ Download
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {selectedJob.error_message && (
                <div className="detail-row error">
                  <strong>Error:</strong> {selectedJob.error_message}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default JobDashboard