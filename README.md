# How to use CollabLens

## Configuring the project

This project provides a lot of code, but you don't need to worry about it. What you  need to do is that you need to change some parameters if you want to run on an IP address. The current program allows running on your local machine.

### Step 1

Open `pages/data/connection.json` and change the IP parameter to the address you want.

### Step 2

Search all files for the IP previously listed in the `json` file and replace it with the new address.

### Step 3

Ensure that all files have been checked including all `html` and `js` files, then continue to the bottom.

## How to run the files

Depending on your python configuration, you may use the `py`, `python`, `python3`, or any other command. From now on, it will be referenced as `py`.

However, note that this uses Python 3.11.0 and Pip version 25.2. If you need to install this version of python, go to [Python's website](https://www.python.org/downloads/release/python-3110/) and scroll to the bottom to find the downloads. From there, you can open the executable/package or whatever it is to install python. Make sure you find the correct command, which should be one of the aforementioned commands.

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
- `secrets`

There are also a few custom libraries in the `lib` folder. To install the libraries listed above, use `py -m pip {LIBRARY_NAME}`.

This also requires FFmpeg installed on your computer for sound conversion. I highly suggest reading this tutorial by WikiHow to install FFmpeg: <https://www.wikihow.com/Convert-Media-with-FFmpeg>.

### Running the files

You can use any coding IDE to run `app.py`, or you can run it in your terminal. If you are running it in your terminal, use the `cd {YOUR_DIRECTORY}` command to go to where `app.py` is located (you can use `ls` to list the files in your current directory), and then you can use the command `py app.py`.

After the initialization succeeds (it should say something like "running server on localhost:8001"), you can run another set of commands in a new terminal window to start the http server: `cd {YOUR_DIRECTORY}/pages` (use the file separator on your machine, like `/` for Mac and `\` for Windows), and `py -m http.server -b {IP_ADDRESS_HERE} {PORT_HERE}`.

For example, I would run `py app.py`, then open a new window and type `cd pages` and `py -m http.server -b 192.168.0.0 8000` (this is a fake IP by the way, and I am assuming my terminal window is already in my directory).
