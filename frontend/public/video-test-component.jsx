import React, { useRef, useState } from 'react';

const VideoPlayer = ({ src, poster, className }) => {
  const videoRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleVideoLoad = () => {
    console.log('Video loaded successfully:', src);
    setIsLoading(false);
    setError(null);
  };

  const handleVideoError = (e) => {
    console.error('Video failed to load:', src, e);
    setError('Failed to load video');
    setIsLoading(false);
  };

  const handlePlay = () => {
    console.log('Playing video:', src);
  };

  return (
    <div className={`video-container ${className || ''}`}>
      {isLoading && (
        <div className="video-loading">
          <span>Loading video...</span>
        </div>
      )}

      {error && (
        <div className="video-error">
          <p>❌ {error}</p>
          <p>Trying to load: {src}</p>
        </div>
      )}

      <video
        ref={videoRef}
        key={src} // Force re-render when src changes
        width="100%"
        height="100%"
        controls
        loop
        muted
        playsInline
        preload="metadata"
        poster={poster}
        className={`video-player ${isLoading ? 'loading' : ''} ${error ? 'error' : ''}`}
        onLoadedData={handleVideoLoad}
        onError={handleVideoError}
        onPlay={handlePlay}
        style={{
          display: error ? 'none' : 'block',
          maxHeight: '400px'
        }}
      >
        <source src={src} type="video/mp4" />
        <source src={src.replace('.mp4', '.webm')} type="video/webm" />
        Your browser does not support the video tag.
      </video>

      <style jsx>{`
        .video-container {
          position: relative;
          width: 100%;
          background: #f3f4f6;
          border-radius: 8px;
          overflow: hidden;
        }

        .video-loading {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: #666;
          font-size: 14px;
          z-index: 1;
        }

        .video-error {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          color: #dc2626;
          z-index: 1;
        }

        .video-player {
          display: block;
          width: 100%;
          height: auto;
        }

        .video-player.loading {
          opacity: 0.3;
        }

        .video-player.error {
          display: none;
        }
      `}</style>
    </div>
  );
};

export default VideoPlayer;