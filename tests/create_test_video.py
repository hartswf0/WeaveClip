import cv2
import numpy as np
import os

def create_test_video(output_path, duration=5, fps=30):
    """Create a test video with moving shapes."""
    # Set video properties
    width = 640
    height = 480
    size = (width, height)
    
    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)
    
    # Create frames
    for i in range(duration * fps):
        # Create a frame with dark background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame.fill(40)  # Dark gray background
        
        # Draw moving circle
        x = int(width/2 + np.sin(i/fps * 2) * 100)
        y = int(height/2 + np.cos(i/fps * 2) * 100)
        cv2.circle(frame, (x, y), 30, (0, 120, 255), -1)  # Orange circle
        
        # Draw moving rectangle
        rx = int(width/2 + np.cos(i/fps * 3) * 150)
        ry = int(height/2 + np.sin(i/fps * 3) * 100)
        cv2.rectangle(frame, (rx-20, ry-20), (rx+20, ry+20), (74, 144, 255), -1)  # Blue rectangle
        
        # Add frame number
        cv2.putText(frame, f'Frame {i}/{duration*fps}', 
                   (10, height-20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (200, 200, 200), 2)
        
        # Write frame
        out.write(frame)
    
    # Release video writer
    out.release()

if __name__ == '__main__':
    # Create sample_clips directory if it doesn't exist
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_clips')
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create test videos
    videos = [
        ('clip1_shapes.mp4', 5),
        ('clip2_motion.mp4', 3),
        ('clip3_animation.mp4', 4)
    ]
    
    for filename, duration in videos:
        output_path = os.path.join(sample_dir, filename)
        print(f'Creating {filename}...')
        create_test_video(output_path, duration=duration)
        print(f'Created {filename}')
