from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import cv2
import mediapipe as mp
import numpy as np
import time
import json
import random
import urllib.parse as urlparse
import google.generativeai as genai

# =====================
# Global Configuration
# =====================
# Configure your API key (store securely in production)
genai.configure(api_key="YOUR_API_KEY_HERE")

EXERCISE_TYPE = "Jumping Jacks"  # default exercise
CAMERA_ON = True                 # Global camera state
REPS_PER_SET = 15                # Number of reps per set

workout_stats = {
    'exercise': EXERCISE_TYPE,
    'reps': 0,
    'duration': 0,  # in seconds
    'calories': 0,
    'sets': 0,      # computed from reps
    'feedback': ""  # latest feedback text for TTS
}

EXERCISE_DATA = {
    "Jumping Jacks": {
        "description": "Jump to spread legs and raise arms overhead then return to start.",
        "progress": "0/15",
        "next": "15 reps"
    },
    "Squats": {
        "description": "Lower into a squat with knees bending then rise back up.",
        "progress": "0/20",
        "next": "20 reps"
    },
    "Push Ups": {
        "description": "Lower your body by bending elbows then push back up.",
        "progress": "0/15",
        "next": "15 reps"
    },
    "Weightlifting": {
        "description": "Perform biceps curls with proper form.",
        "progress": "0/12",
        "next": "12 reps"
    },
    "Deadlifts": {
        "description": "Bend at the hips and straighten up to lift the weight.",
        "progress": "0/10",
        "next": "10 reps"
    },
    "Yoga": {
        "description": "Hold a yoga pose (e.g. mountain pose) for balance.",
        "progress": "0/1",
        "next": "Hold for 10 sec"
    }
}

FALLBACK_VIDEOS = [
    "https://www.youtube.com/watch?v=Z6-IEcWlF9o",
    "https://www.youtube.com/watch?v=UBMk30rjy0o",
    "https://www.youtube.com/watch?v=ml6cT4AZdqI",
    "https://www.youtube.com/watch?v=50kH47ZztHs",
    "https://www.youtube.com/watch?v=UItWltVZZmE"
]

# =====================
# Voice Command Handler
# =====================
@csrf_exempt
def voice_command_handler(request):
    """
    Processes a POST request with a 'command' string to perform server-side actions.
    Handles camera toggling and simulates a "play song" action.
    """
    global CAMERA_ON

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get("command", "").lower()
            response = {"status": "success", "action": None}

            if "camera on" in command:
                if not CAMERA_ON:
                    CAMERA_ON = True
                response["action"] = "Camera turned on"
            elif "camera off" in command:
                if CAMERA_ON:
                    CAMERA_ON = False
                response["action"] = "Camera turned off"
            elif "play song" in command:
                response["action"] = "Triggered play song action"
            else:
                response["action"] = "Command not recognized by server"
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method"})


# =====================
# Pose Detection Helpers
# =====================
def calculate_angle(a, b, c):
    """
    Calculate angle (in degrees) between three MediaPipe landmarks.
    """
    import math
    a_coords = (a.x, a.y)
    b_coords = (b.x, b.y)
    c_coords = (c.x, c.y)
    ab = (a_coords[0] - b_coords[0], a_coords[1] - b_coords[1])
    cb = (c_coords[0] - b_coords[0], c_coords[1] - b_coords[1])
    dot = ab[0] * cb[0] + ab[1] * cb[1]
    mag_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    mag_cb = math.sqrt(cb[0]**2 + cb[1]**2)
    if mag_ab == 0 or mag_cb == 0:
        return 0.0
    angle_rad = math.acos(dot / (mag_ab * mag_cb))
    return angle_rad * (180.0 / math.pi)


def detect_jumping_jacks(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        return frame
    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark

    left_ankle = landmarks[L.LEFT_ANKLE.value]
    right_ankle = landmarks[L.RIGHT_ANKLE.value]
    left_shoulder = landmarks[L.LEFT_SHOULDER.value]
    right_shoulder = landmarks[L.RIGHT_SHOULDER.value]
    left_wrist = landmarks[L.LEFT_WRIST.value]
    right_wrist = landmarks[L.RIGHT_WRIST.value]
    nose = landmarks[L.NOSE.value]

    if (left_ankle.visibility < 0.5 or right_ankle.visibility < 0.5 or
        left_wrist.visibility < 0.5 or right_wrist.visibility < 0.5 or
        nose.visibility < 0.5):
        camera.feedback = "Landmarks not visible."
        cv2.putText(frame, camera.feedback, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    ankle_distance = abs(left_ankle.x - right_ankle.x)
    WIDE_THRESHOLD = 0.15
    TOGETHER_THRESHOLD = 0.05
    ankles_wide = ankle_distance > WIDE_THRESHOLD
    ankles_together = ankle_distance < TOGETHER_THRESHOLD
    arms_up = (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y)
    arms_down = (left_wrist.y > left_shoulder.y and right_wrist.y > right_shoulder.y)
    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
    head_movement = abs(nose.x - shoulder_mid_x)
    HEAD_STABILITY_THRESHOLD = 0.1
    head_stable = head_movement < HEAD_STABILITY_THRESHOLD

    if ankles_wide and arms_up and head_stable:
        current_position = "up"
    elif ankles_together and arms_down and head_stable:
        current_position = "down"
    else:
        current_position = "intermediate"

    if current_position == "up" and camera.stage != "up":
        camera.stage = "up"
    elif current_position == "down" and camera.stage == "up":
        camera.stage = "down"
        camera.counter += 1
        camera.feedback = f"Jumping Jack rep {camera.counter}"
        workout_stats['reps'] = camera.counter

    cv2.putText(frame, f"AnkleDist: {ankle_distance:.2f}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f"HeadMove: {head_movement:.2f}", (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f"Position: {current_position}", (10, 210),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f"Stage: {camera.stage}", (10, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, camera.feedback, (10, 270),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


def detect_squats(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        cv2.putText(frame, camera.feedback, (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return frame

    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark
    left_hip = landmarks[L.LEFT_HIP.value]
    left_knee = landmarks[L.LEFT_KNEE.value]
    left_ankle = landmarks[L.LEFT_ANKLE.value]
    right_hip = landmarks[L.RIGHT_HIP.value]
    right_knee = landmarks[L.RIGHT_KNEE.value]
    right_ankle = landmarks[L.RIGHT_ANKLE.value]
    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
    DOWN_ANGLE_THRESHOLD = 100
    UP_ANGLE_THRESHOLD = 160
    both_knees_down = (left_knee_angle < DOWN_ANGLE_THRESHOLD and right_knee_angle < DOWN_ANGLE_THRESHOLD)
    both_knees_up = (left_knee_angle > UP_ANGLE_THRESHOLD and right_knee_angle > UP_ANGLE_THRESHOLD)

    if both_knees_down:
        if camera.stage != "down":
            camera.stage = "down"
            camera.feedback = "Squat down detected"
        else:
            camera.feedback = "Stay down or go lower"
    elif both_knees_up:
        if camera.stage == "down":
            camera.stage = "up"
            camera.counter += 1
            camera.feedback = f"Squat rep {camera.counter} completed"
            workout_stats['reps'] = camera.counter
        else:
            camera.feedback = "Stand straight"
    else:
        camera.feedback = "Perform a full squat (go lower or stand fully)"

    cv2.putText(frame, f"Left Knee: {int(left_knee_angle)}°", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f"Right Knee: {int(right_knee_angle)}°", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f"Reps: {camera.counter}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, camera.feedback, (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


def detect_pushups(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        return frame

    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark
    shoulder = landmarks[L.LEFT_SHOULDER.value]
    elbow = landmarks[L.LEFT_ELBOW.value]
    wrist = landmarks[L.LEFT_WRIST.value]
    elbow_angle = calculate_angle(shoulder, elbow, wrist)

    if elbow_angle < 90 and camera.stage != "down":
        camera.stage = "down"
    elif elbow_angle > 160 and camera.stage == "down":
        camera.stage = "up"
        camera.counter += 1
        camera.feedback = f"Push-up rep {camera.counter}"
        workout_stats['reps'] = camera.counter

    cv2.putText(frame, f"Elbow Angle: {int(elbow_angle)}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, camera.feedback, (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


def detect_weightlifting(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        return frame

    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark
    shoulder = landmarks[L.LEFT_SHOULDER.value]
    elbow = landmarks[L.LEFT_ELBOW.value]
    wrist = landmarks[L.LEFT_WRIST.value]
    elbow_angle = calculate_angle(shoulder, elbow, wrist)

    if elbow_angle < 40 and camera.stage != "down":
        camera.stage = "down"
    elif elbow_angle > 160 and camera.stage == "down":
        camera.stage = "up"
        camera.counter += 1
        camera.feedback = f"Lift rep {camera.counter}"
        workout_stats['reps'] = camera.counter

    cv2.putText(frame, f"Elbow Angle: {int(elbow_angle)}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, camera.feedback, (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


def detect_deadlifts(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        return frame

    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark
    shoulder = landmarks[L.LEFT_SHOULDER.value]
    hip = landmarks[L.LEFT_HIP.value]
    knee = landmarks[L.LEFT_KNEE.value]
    hip_angle = calculate_angle(shoulder, hip, knee)

    if hip_angle < 90 and camera.stage != "down":
        camera.stage = "down"
    elif hip_angle > 160 and camera.stage == "down":
        camera.stage = "up"
        camera.counter += 1
        camera.feedback = f"Deadlift rep {camera.counter}"
        workout_stats['reps'] = camera.counter

    cv2.putText(frame, f"Hip Angle: {int(hip_angle)}", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, camera.feedback, (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


def detect_yoga(camera, frame, results):
    if not results.pose_landmarks:
        camera.feedback = "No pose detected. Please stand in the frame."
        camera.hold_start = None
        return frame

    landmarks = results.pose_landmarks.landmark
    L = mp.solutions.pose.PoseLandmark
    left_wrist = landmarks[L.LEFT_WRIST.value]
    right_wrist = landmarks[L.RIGHT_WRIST.value]
    nose = landmarks[L.NOSE.value]

    if left_wrist.y < nose.y and right_wrist.y < nose.y:
        if not hasattr(camera, 'hold_start') or camera.hold_start is None:
            camera.hold_start = time.time()
        elapsed_hold = time.time() - camera.hold_start
        camera.feedback = f"Holding pose for {int(elapsed_hold)} seconds"
        if elapsed_hold > 10:
            camera.counter += 1
            camera.feedback = f"Yoga hold {camera.counter} completed"
            workout_stats['reps'] = camera.counter
            camera.hold_start = None
    else:
        camera.hold_start = None
        camera.feedback = "Adjust pose"

    cv2.putText(frame, camera.feedback, (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    return frame


# =====================
# Mapping Exercise Names to Detection Functions
# =====================
DETECTION_FUNCTIONS = {
    "Jumping Jacks": detect_jumping_jacks,
    "Squats": detect_squats,
    "Push Ups": detect_pushups,
    "Weightlifting": detect_weightlifting,
    "Deadlifts": detect_deadlifts,
    "Yoga": detect_yoga,
}


# =====================
# Video Camera Class for Processing Frames
# =====================
class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        self.counter = 0
        self.stage = "up"
        self.start_time = time.time()
        self.feedback = ""
        self.current_exercise = EXERCISE_TYPE
        self.hold_start = None

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return None
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        if not CAMERA_ON:
            blank = np.zeros((h, w, 3), np.uint8)
            cv2.putText(blank, "Camera Off", (w // 4, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            ret, jpeg = cv2.imencode('.jpg', blank)
            return jpeg.tobytes()
        return frame


# =====================
# Frame Processing Function
# =====================
def process_exercise_frame(camera, frame):
    """
    Runs pose detection on a frame, updates rep and set counts, and stores feedback.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = camera.pose.process(rgb)
    if results.pose_landmarks:
        camera.mp_drawing.draw_landmarks(frame, results.pose_landmarks, camera.mp_pose.POSE_CONNECTIONS)
    elapsed = int(time.time() - camera.start_time)
    workout_stats['duration'] = elapsed
    cv2.putText(frame, f"Time: {elapsed}s", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Exercise: {camera.current_exercise}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Reps: {camera.counter}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    detection_fn = DETECTION_FUNCTIONS.get(camera.current_exercise)
    if detection_fn:
        frame = detection_fn(camera, frame, results)
    workout_stats['sets'] = camera.counter // REPS_PER_SET
    workout_stats['feedback'] = camera.feedback
    return frame


# =====================
# Generator for Streaming Video Frames
# =====================
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        if isinstance(frame, np.ndarray) and CAMERA_ON:
            frame = process_exercise_frame(camera, frame)
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# =====================
# Django Views
# =====================
def workout_session(request):
    """
    Main workout session view.
    """
    exercises = list(EXERCISE_DATA.keys())
    current = EXERCISE_DATA.get(EXERCISE_TYPE, {})
    context = {
        'exercises': exercises,
        'selected_exercise': EXERCISE_TYPE,
        'exercise_data': current,
    }
    return render(request, 'workout/main.html', context)


def workout_partial(request):
    """
    Renders a partial template with workout content.
    """
    exercises = list(EXERCISE_DATA.keys())
    current = EXERCISE_DATA.get(EXERCISE_TYPE, {})
    context = {
        'exercises': exercises,
        'selected_exercise': EXERCISE_TYPE,
        'exercise_data': current,
    }
    return render(request, 'partials/workout.html', context)


def video_feed(request):
    """
    Streams the video feed.
    """
    cam = VideoCamera()
    cam.current_exercise = EXERCISE_TYPE
    return StreamingHttpResponse(gen(cam),
                                   content_type='multipart/x-mixed-replace; boundary=frame')


@require_POST
def update_exercise(request):
    """
    Updates the exercise and resets workout stats.
    """
    global EXERCISE_TYPE, workout_stats
    new_ex = request.POST.get('exercise')
    if new_ex in EXERCISE_DATA:
        EXERCISE_TYPE = new_ex
        workout_stats = {
            'exercise': new_ex,
            'reps': 0,
            'duration': 0,
            'calories': 0,
            'sets': 0,
            'feedback': ""
        }
    exercises = list(EXERCISE_DATA.keys())
    current = EXERCISE_DATA.get(EXERCISE_TYPE, {})
    context = {
        'exercises': exercises,
        'selected_exercise': EXERCISE_TYPE,
        'exercise_data': current,
    }
    return render(request, 'home/main.html', context)


@require_POST
def toggle_camera(request):
    """
    Toggles the global camera state.
    """
    global CAMERA_ON
    CAMERA_ON = not CAMERA_ON
    return JsonResponse({'camera_on': CAMERA_ON})


def get_workout_stats(request):
    """
    Returns current workout stats (including reps, sets, and feedback).
    """
    return JsonResponse(workout_stats)


# =====================
# Music & YouTube Endpoints
# =====================
def extract_video_id(youtube_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    parsed = urlparse.urlparse(youtube_url)
    video_id = urlparse.parse_qs(parsed.query).get("v", [None])[0]
    if not video_id and "youtu.be" in youtube_url:
        video_id = youtube_url.rstrip('/').split('/')[-1]
    return video_id


@csrf_exempt
def get_music_recommendations(request):
    """
    Returns a list of predefined exercise songs.
    """
    if request.method == 'POST':
        try:
            songs = [
                {"title": "Eye of the Tiger", "artist": "Survivor", "video_id": "btPJPFnesV4"},
                {"title": "Stronger", "artist": "Kanye West", "video_id": "lExW80sXsHs"},
                {"title": "Till I Collapse", "artist": "Eminem", "video_id": "y6qLkzWNNlU"},
                {"title": "Don't Stop Me Now", "artist": "Queen", "video_id": "HgzGwKwLmgM"},
                {"title": "Lose Yourself", "artist": "Eminem", "video_id": "xFYQQPAOz7k"}
            ]
            return JsonResponse({"status": "success", "songs": songs})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method"})


@csrf_exempt
def connect_music_service(request):
    """
    Uses Generative AI to obtain a workout video URL or picks a fallback.
    """
    if request.method == 'POST':
        try:
            prompt = (
                "Provide a single YouTube video URL for a workout video. "
                "Return only the URL in JSON format like this: "
                "{\"youtube_url\": \"https://www.youtube.com/watch?v=VIDEO_ID\"}"
            )
            response = genai.generate_text(model="models/text-bison-001", prompt=prompt)
            response_text = response.result
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            youtube_url = None
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                try:
                    data_json = json.loads(json_str)
                    youtube_url = data_json.get("youtube_url")
                except json.JSONDecodeError:
                    pass
            if not youtube_url:
                youtube_url = random.choice(FALLBACK_VIDEOS)
            video_id = extract_video_id(youtube_url)
            if video_id:
                return JsonResponse({
                    "status": "success",
                    "video_id": video_id,
                    "title": "Workout Video"
                })
            else:
                fallback_url = random.choice(FALLBACK_VIDEOS)
                video_id = extract_video_id(fallback_url)
                return JsonResponse({
                    "status": "success",
                    "video_id": video_id,
                    "title": "Default Workout Video"
                })
        except Exception as e:
            fallback_url = random.choice(FALLBACK_VIDEOS)
            video_id = extract_video_id(fallback_url)
            return JsonResponse({
                "status": "success",
                "video_id": video_id,
                "title": "Default Workout Video"
            })
    return JsonResponse({"status": "error", "message": "Invalid request method"})


@csrf_exempt
def search_youtube_music(request):
    """
    Demo endpoint to search YouTube music based on query.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            demo_videos = {
                "high energy": "btPJPFnesV4",
                "hiit": "VZ2DSbq76vI",
                "cardio": "Ouwor6dJAvI",
                "strength": "lExW80sXsHs",
                "yoga": "V5uS0Um9eZ8"
            }
            for key, video_id in demo_videos.items():
                if key in query.lower():
                    return JsonResponse({
                        "status": "success",
                        "video_id": video_id,
                        "title": f"Music for {query}"
                    })
            fallback_id = random.choice(FALLBACK_VIDEOS)
            return JsonResponse({
                "status": "success",
                "video_id": extract_video_id(fallback_id),
                "title": f"Default Music for {query}"
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
