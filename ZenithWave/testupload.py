from flask import Flask, render_template, request, send_file
from moviepy.editor import VideoFileClip

app = Flask(__name__)

# Homepage
@app.route('/')
def index():
    return render_template('testindex.html')

# Handle video upload and editing
@app.route('/edit-video', methods=['POST'])
def edit_video():
    # Check if a file was uploaded
    if 'video' not in request.files:
        return 'No file uploaded', 400

    video_file = request.files['video']

    # Check if the file is a video
    if video_file.filename == '':
        return 'No file selected', 400

    # Save the uploaded video
    video_path = 'uploads/' + video_file.filename
    video_file.save(video_path)

    # Edit the video (example: cut first 10 seconds)
    edited_video_path = edit_video(video_path)

    # Return the edited video file
    return send_file(edited_video_path, as_attachment=True)

# Function to edit the video
def edit_video(video_path):
    # Open the video file
    video = VideoFileClip(video_path)

    # Example editing: cut the first 10 seconds
    edited_video = video.subclip(10)

    # Save the edited video
    edited_video_path = 'edited_videos/' + 'edited_' + video_path.split('/')[-1]
    edited_video.write_videofile(edited_video_path)

    return edited_video_path

if __name__ == '__main__':
    app.run(debug=True)
