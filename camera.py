import cv2
import time
from datetime import datetime
import os
import requests
import numpy as np

def capture_stream(stream_url, interval=30, save_frames=True, show_live=True):
    """
    Capture frames from a live camera stream
    
    Args:
        stream_url: URL of the camera stream
        interval: Seconds between captures (default 30)
        save_frames: Whether to save captured frames (default True)
        show_live: Whether to display live feed (default True)
    """
    
    # Create folder for saved frames with timestamp for specific session
    if save_frames:
        base_folder = "captured_frames"
        session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_folder = os.path.join(base_folder, f"session_{session_timestamp}")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        print(f"Frames will be saved to: {output_folder}/")
    
    # Check if snapshot URL?
    is_snapshot = stream_url.endswith('.jpg') or 'snap' in stream_url.lower()
    
    if is_snapshot:
        print(f"Detected snapshot URL: {stream_url}")
        capture_snapshot_stream(stream_url, interval, save_frames, show_live, output_folder)
    else:
        # Regular continuous video stream
        print(f"Connecting to stream: {stream_url}")
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            print("Error: Could not open stream")
            return
        
        print(f"Capturing every {interval} seconds")
        
        last_capture_time = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to read frame")
                break
            
            current_time = time.time()
            
            # Check if interval has passed
            if current_time - last_capture_time >= interval:
                frame_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                
                if save_frames:
                    filename = f"{output_folder}/frame_{frame_count}_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Captured frame {frame_count} at {timestamp}")
                else:
                    print(f"Frame {frame_count} captured at {timestamp} (not saved)")
                
                last_capture_time = current_time
            
            # Display live feed if enabled
            if show_live:
                cv2.imshow('Live Camera Feed', frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nStopping capture...")
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nTotal frames captured: {frame_count}")

def capture_snapshot_stream(stream_url, interval, save_frames, show_live, output_folder):
    """
    Handle snapshot URLs that give one image per request
    """
    print(f"Capturing every {interval} seconds")
    print("Press Ctrl+C to quit\n")
    
    frame_count = 0
    
    try:
        while True:
            try:
                # Request image from stream URL
                response = requests.get(stream_url, timeout=10)
                
                if response.status_code == 200:
                    # Convert to image
                    arr = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frame_count += 1
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        
                        if save_frames:
                            filename = f"{output_folder}/frame_{frame_count}_{timestamp}.jpg"
                            cv2.imwrite(filename, frame)
                            print(f"Captured frame {frame_count} at {timestamp}")
                        else:
                            print(f"Frame {frame_count} captured at {timestamp} (not saved)")
                        
                        # Display Live Feed
                        if show_live:
                            cv2.imshow('Live Camera Feed', frame)
                            # Check for 'q' key press (need short wait for window to respond)
                            if cv2.waitKey(100) & 0xFF == ord('q'):
                                print("\nStopping capture...")
                                break
                    else:
                        print("Warning: Could not decode image")
                else:
                    print(f"Error: Got response code {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching image: {e}")
            
            # Wait for the specified interval before next capture
            print(f"Waiting {interval} seconds until next capture...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        cv2.destroyAllWindows()
        print(f"\nTotal frames captured: {frame_count}")

if __name__ == "__main__":
    # Example usage - replace with your camera stream URL
    STREAM_URL = "http://124.155.121.218:3000/webcapture.jpg?command=snap&channel=1?1759354033"

    capture_stream(
        stream_url=STREAM_URL,
        interval=30,           # Capture every 30 seconds
        save_frames=True,      # Save frames to disk
        show_live=True         # Display live feed
    )