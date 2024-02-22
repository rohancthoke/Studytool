from flask import Flask, request, jsonify
import os
import time
from pytube import YouTube
from txtai.pipeline import Summary
import whisper

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Symmerize Study Tool</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                margin: 0;
                padding: 0;
            }

            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }

            h1 {
                text-align: center;
                margin-bottom: 20px;
                color: #495057;
            }

            p {
                margin-bottom: 20px;
            }

            form {
                text-align: center;
            }

            label {
                font-weight: bold;
            }

            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin-top: 5px;
                margin-bottom: 20px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                box-sizing: border-box;
            }

            button {
                background-color: #007bff;
                color: #fff;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }

            button:hover {
                background-color: #0056b3;
            }

            #loadingMessage {
                display: none;
                text-align: center;
                margin-top: 20px;
            }

            .loader {
                border: 8px solid #f3f3f3;
                border-radius: 50%;
                border-top: 8px solid #3498db;
                width: 40px;
                height: 40px;
                animation: spin 2s linear infinite;
                margin: 0 auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            #transcribedText,
            #summarizedText {
                margin-left: auto;
                margin-right: auto;
                max-width: 600px;
                margin-top: 40px;
                padding: 15px;
                background-color: #d1ecf1;
                border-radius: 5px;
            }

            footer {
                background-color: #343a40;
                color: #ffffff;
                text-align: center;
                padding: 15px 0;
                margin-top: 50px;
                position : fixed;
                bottom :0;
                left:0;
                width:100%;
            }
        </style>
    </head>

    <body>
    <h1 class="text-center">StudyTool: an AI based study aid</h1>
            <p class="text-center">Welcome to the study tool summarization application.</p>


        <div class="container">
            
            <form>
                <div class="mb-3">
                    <label for="videoInput" class="form-label">Enter Video URL:</label>
                    <input type="text" class="form-control" id="videoInput" placeholder="https://www.youtube.com/example">
                </div>
                <div id="loadingMessage">
                    <div class="loader"></div>
                </div>
                <button type="button" class="btn btn-primary" onclick="summarizeVideo()">Summarize Video</button>
            </form>

            
        </div>
        <div id="transcribedText">
        <h2 class="text-center">Transcribed Text:</h2>
            <p class="text-justify"></p></div>
            <div id="summarizedText">
            <h2 class="text-center">Summarized Text:</h2>
            <p class="text-justify"></p>
            </div>

            <footer>
                <p>Symmerize Study Tool | Contact Us: customerservice@gmail.com</p>
            </footer>

        <script>
            function summarizeVideo() {
                var videoURL = document.getElementById("videoInput").value;

                // Show loading message and hide other content
                document.getElementById("loadingMessage").style.display = "block";
                document.getElementById("transcribedText").innerHTML = "";
                document.getElementById("summarizedText").innerHTML = "";

                fetch('/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        youtube_url: videoURL
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        document.getElementById("summarizedText").innerHTML = `<h2>${data.summary_title}</h2>` + data.summary;
                        document.getElementById("transcribedText").innerHTML = `<h2>Transcribed Text:</h2><p>${data.transcribed_text}</p>`;
                    } else {
                        alert("Failed to summarize video: " + data.error);
                    }

                    // Hide loading message after processing
                    document.getElementById("loadingMessage").style.display = "none";
                })
                .catch(error => {
                    console.error(error);
                    alert("An error occurred while summarizing the video.");

                    // Hide loading message in case of error
                    document.getElementById("loadingMessage").style.display = "none";
                });
            }
        </script>

    </body>

    </html>
    """

def text_summary(text, maxlength=None):
    # Create summary instance
    summary = Summary()
    result = summary(text, maxlength=maxlength)
    return result

def download_and_transcribe_youtube_video(youtube_url, output_path, output_filename="custom_video_name.mp4"):
    try:
        yt = YouTube(youtube_url)
        ys = yt.streams.filter(only_audio=True).first()

        # Download video directly as MP4
        video_output_path = os.path.join(output_path, output_filename)
        ys.download(output_path, filename=output_filename)

        # Transcribe MP4 using Whisper
        start_time = time.time()
        model = whisper.load_model('base')
        out = model.transcribe(video_output_path)
        transcribed_text = out['text']
        end_time = time.time()
        print("Transcription time:", end_time - start_time, "seconds")

        return transcribed_text  # Return the transcribed text for summarization

    except Exception as e:
        print(f"Error: {e}")
        return None

def segment_text(text, segment_length=1000):
    # Split the text into segments based on the segment length
    segments = [text[i:i+segment_length] for i in range(0, len(text), segment_length)]
    return segments

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    youtube_url = data['youtube_url']
    output_path = "./yDownload"  # Change this to your desired output path

    transcribed_text = download_and_transcribe_youtube_video(youtube_url, output_path)

    if transcribed_text:
        # Segment the transcribed text
        segments = segment_text(transcribed_text)

        # Summarize each segment individually with bullet points
        summaries = []
        for i, segment in enumerate(segments, start=1):
            summary = text_summary(segment, maxlength=None)  # Adjust the maximum length as needed
            summary_with_bullet = f"{i}. {summary}"
            summaries.append(summary_with_bullet)

        # Combine individual summaries into a point-wise summary
        point_wise_summary = "\n".join(summaries)
        return jsonify({'success': True, 'summary_title': 'Summary', 'summary': point_wise_summary, 'transcribed_text': transcribed_text})
    else:
        return jsonify({'success': False, 'error': 'Failed to transcribe video'})

if __name__ == "__main__":
    app.run(debug=True)
