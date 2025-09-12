# How to use CollabLens

## What this Is

Collablens is a project made for people to communicate in a kind environment and ensure everyone has a voice.

You can watch our project video here: [video link](https://drive.google.com/file/d/17aMr5uZ_blr3LTjrCcuqDmoWlwHvRZ58/view?usp=drive_link)\
Or you can read the transcription: [transcription](https://docs.google.com/document/d/16n6tC3MFPMs_r9h6Pslbm-PrAul3JJKANkW7L5c4mFc/edit?usp=drive_link)

## Configuring the project

This project provides a lot of code, but you don't need to worry about it. What you  need to do is that you need to change some parameters if you want to run on an IP address. The current program allows running on your local machine.

### Step 1

Open `pages/data/connection.json` and change the IP parameter to the address you want.

### Step 2

Search all files for the IP previously listed in the `json` file and replace it with the new address.

### Step 3

Ensure that all files have been checked, including all `html` and `js` files, then continue to the next section.

## How to run the files

Depending on your python configuration, you may use the `py`, `python`, `python3`, or any other command. From now on, it will be referenced as `py`.

However, note that this uses Python 3.11.0 and Pip version 25.2. (You can check your Python version using `py --version` and pip version using `py -m pip --version`). If you need to install this version of python, go to [Python's website](https://www.python.org/downloads/release/python-3110/) and scroll to the bottom to find the downloads. From there, you can open the executable/package or whatever it is to install python. Make sure you find the correct command, which should be one of the aforementioned commands.

### Installing dependencies

You also may have `pip` as a separate commmand. If you do, that is good. However, for the sake of this tutorial I will be using `py -m pip` instead.

To begin, we need to install all python libraries. These include:

- `openai`
- `json`
- `asyncio`
- `better_profanity`
- `speech_recognition`
- `vosk`
- `threading`
- `pyaudio`
- `wave`
- `base64`
- `subprocess`
- `websockets`
- `ffmpeg`
- `secrets`

There are also a few custom libraries in the `lib` folder. To install the libraries listed above, use `py -m pip {LIBRARY_NAME}`.

This also requires FFmpeg installed on your computer for sound conversion. I highly suggest reading this tutorial by WikiHow to install FFmpeg: <https://www.wikihow.com/Convert-Media-with-FFmpeg>.

#### Installing Vosk

You should have already installed the `vosk` package with `pip`, as shown above. However, you will need to go to [Vosk's website](https://alphacephei.com/vosk/models) to download one of their models. I suggest downloading `vosk-model-en-us-0.22-lgraph`, which is a decently sized English model at 128 MB. If you really want to splurge, you can download larger models that include a 2.3 GB one, or even a mini model at 40 MB. Whatever you choose, you must include the `model` folder in the same directory as `app.py`.

The file may download as a ZIP file, so you may need to extract the files. When you open the model, there should be multiple folders including `am`, `conf`, `graph`, and `ivector`. There may or may not be a README file too. Once you validate this, you should be good.

### Running the files

You can use any coding IDE to run `app.py`, or you can run it in your terminal. If you are running it in your terminal, use the `cd {YOUR_DIRECTORY}` command to go to where `app.py` is located (you can use `ls` to list the files in your current directory), and then you can use the command `py app.py`.

After the initialization succeeds (it should say something like "running server on localhost:8001"), you can run another set of commands in a new terminal window to start the http server: `cd {YOUR_DIRECTORY}/pages` (use the file separator on your machine, like `/` for Mac and `\` for Windows), and `py -m http.server -b {IP_ADDRESS_HERE} 8000`. If you are running on localhost, you can omit the `-b` and `{IP_ADDRESS_HERE}` section.

For example, I would run `py app.py`, then open a new window and type `cd pages` and `py -m http.server -b 192.168.0.0 8000` (this is a fake IP by the way, and I am assuming my terminal window is already in my directory).

#### Stopping

You can use the keyboard shortcut `^C` (control C) or `⌘C` (command C) or whatever python keyboard interrupt key you use to stop the python program and/or the HTTP server. Just keep in mind that some people may not want you to host servers on their network, so watch out.

## Additional Info

If you are reading this, congratulations! (I'm just kidding.) But this section is actually very useful. First of all, if you are not running on `localhost`, the microphone will not work on Chrome due to its strict regulation on insecure websites. I am not sure about other browsers, but they may block it too. If it is blocked, it will show an error message.

Also, some actions like audio processing and AI processing may take time, so please be patient.

When you have an HTTP server running, if you chose to use localhost it will only be accessible on your own computer. If you chose IP, it will only be accessible on the same LAN (local area network) you are connected to.
