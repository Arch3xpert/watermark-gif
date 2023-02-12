import os
import requests
from flask import Flask, request, Response
from watermark import File, Watermark, Position, apply_watermark

app = Flask(__name__)
botToken = os.getenv("BOT_TOKEN")
downloadsPath = os.getcwd()


def sendPhoto(chat_id, filePath):
    url = f"https://api.telegram.org/bot{botToken}/sendPhoto?chat_id={chat_id}"
    files = {"photo": open(filePath, "rb")}
    r = requests.post(url, files=files)
    return r


def sendAnimation(chat_id, filePath):
    url = f"https://api.telegram.org/bot{botToken}/sendAnimation?chat_id={chat_id}"
    files = {"animation": open(filePath, "rb")}
    r = requests.post(url, files=files)
    return r


def sendWaterMarkedFile(chat_id, filePath, mediaType):
    if mediaType == "video":
        sendAnimation(chat_id, filePath)
    elif mediaType == "image":
        sendPhoto(chat_id, filePath)


def sendMessage(chat_id, text, messageID):
    url = f"https://api.telegram.org/bot{botToken}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "reply_to_message_id": messageID}
    r = requests.post(url, json=payload)
    return r


def getDownloadURL(fileID):
    url = f"https://api.telegram.org/bot{botToken}/getFile?file_id={fileID}"
    r = requests.get(url)
    file_path = r.json()["result"]["file_path"]
    downloadURL = f"https://api.telegram.org/file/bot{botToken}/{file_path}"
    return downloadURL


@app.get("/")
def hello_world():
    return "Hello, World!"


@app.post("/telegram")
def telegram():
    msg = request.get_json()
    chat_id = msg["message"]["chat"]["id"]
    messageID = msg["message"]["message_id"]

    try:
        if str(chat_id) not in [str(_) for _ in list(os.getenv("CHAT_IDS").split())]:
            sendMessage(chat_id, "Sorry, you dont have permission to Access this Please Purchase it from @THAKUR0128\n\nUse the Command /help For more information About this bot And Use Command /purchase for Prices\n\nThanks", messageID)
            return Response("ok", status=200)
        elif (
            "text" in msg["message"]
            and "video" not in msg["message"]
            and "photo" not in msg["message"]
        ):
            inputText = msg["message"]["text"]
            sendMessage(
                chat_id,
                "You have not send any video or photo and sent this text: " + inputText,
                messageID,
            )

        elif "video" in msg["message"] or "photo" in msg["message"]:
            fileName = (
                msg["message"]["video"]["file_name"]
                if "video" in msg["message"]
                else "photo.jpeg"
            )
            fileID = (
                msg["message"]["video"]["file_id"]
                if "video" in msg["message"]
                else msg["message"]["photo"][-1]["file_id"]
            )
            downloadURL = getDownloadURL(fileID)
            response = requests.get(downloadURL)
            with open(downloadsPath + "/" + fileName, "wb") as f:
                f.write(response.content)
            inputFile = File(fileName)

            # Check if the watermark folder exists
            if not os.path.exists(downloadsPath + "/watermark"):
                os.makedirs(downloadsPath + "/watermark")

            with open("channels.txt", "r") as f:
                channels = f.read().splitlines()
                for channel in channels:
                    chat_id, logoPath = channel.split(" ")
                    chat_id = int(chat_id)
                    if chat_id < 0:
                        chat_id = "-100" + str(abs(chat_id))
                    chat_id = int(chat_id)
                    waterMarkClass = Watermark(
                        overlay="logos/" + logoPath, pos=Position.top_right
                    )
                    outputFile = apply_watermark(
                        file=inputFile,
                        wtm=waterMarkClass,
                        output_file=downloadsPath + "/watermark/" + fileName,
                    )
                    response = sendWaterMarkedFile(
                        chat_id,
                        outputFile,
                        inputFile.find_type(),
                    )
                    # Delete the video files
                    os.remove(downloadsPath + "/watermark/" + fileName)
            os.remove(downloadsPath + "/" + fileName)
        else:
            sendMessage(chat_id, "An Invalid Input", messageID)
    except:
        pass
    return Response("ok", status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
