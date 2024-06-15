from scraper import scraper as sp
from datetime import datetime, timezone

from flask import Flask, render_template, request, send_file, jsonify
import requests
from io import BytesIO
import urllib.parse
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.environ.get('TOKEN')
chat_id = os.environ.get('CHATID')

def send_notify(message:str):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url).json()
    except:
        print("err")


app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"message": "Hello World!"})


@app.route('/posts/<string:username>')
def posts(username):
    send_notify(f"Post : {username}")
    data = sp.scrape_user_posts(sp.scrape_user_id(username))
    user_posts = []
    posts_count = data[1]
    
    if data != "error":
        if data != "time_out":
            for item in data[0]:
                # shortcode = data.get("shortcode")
                shared_date = item.get("taken_at")
                converted_date = datetime.fromtimestamp(shared_date, timezone.utc)
                src_attached = []
        
                if item.get("src_attached"):
                    for i in item.get("src_attached"):
                        src_attached.append(f"/get?url={urllib.parse.quote(i)}")

                print(src_attached)
                user_post = {
                    "video_url" : item.get("video_url"),
                    "src" : f"/get?url={urllib.parse.quote(item.get('src'))}",
                    "views" : item.get("views"),
                    "likes" : item.get("likes"),
                    "formatted_date" : converted_date.strftime("%d/%m/%Y"),
                    "captions" : item.get("captions"),
                    "src_attached" : src_attached
                }
                user_posts.append(user_post)

            return render_template('index.html', data=user_posts, username = username, posts_count = posts_count)
        else:
            return jsonify({"message": "Too many requests. Try after an hour."})
    else:
        return jsonify({"message": "Something went wrong"})


@app.route('/get')
def image_proxy():
    url = request.args.get('url')
    response = requests.get(url)
    return send_file(BytesIO(response.content), mimetype=response.headers['Content-Type'])


@app.route('/user/<string:username>')
def user(username):
    send_notify(f"User : {username}")
    user = sp.user_info(username)
    return user


@app.route('/user/v2/<string:username>')
def user_info_v2(username):
    send_notify(f"User v2 : {username}")
    user = sp.user_info_v2(username)
    return user


@app.route('/highlight/<string:username>')
def highlight(username):
    send_notify(f"Highlight : {username}")
    data = sp.get_highlights(username)
    _highlight = True
    if data != "error": 
        if data == []:
            _highlight = False
        return render_template('highlight.html', data=data, username = username, highlight = _highlight)
    else:
        return jsonify({"message": "Something went wrong. Please try again after a while."})
    

@app.route('/highlightStory/<string:id>')
def highlightStory(id):
    send_notify(f"HiglightStory : {id}")
    data = sp.get_highlightStory(id)
    _story = True
    if data != "error": 
        if data == []:
            _story = False
        return render_template('viewhighlights.html', data=data, story = _story)
    else:
        return jsonify({"message": "Something went wrong. Please try again after a while."})


@app.route('/story/<string:username>')
def story(username):
    send_notify(f"Story : {username}")
    data = sp.story(username)
    _story = True
    if data != "error": 
        if data == []:
            _story = False
        return render_template('story.html', data=data, username = username, story = _story)
    else:
        return jsonify({"message": "Something went wrong. Please try again after a while."})
    

@app.route('/story/v2/<string:username>')
def storyV2(username):
    send_notify(f"Story v2 : {username}")
    data = sp.storyV2(username)
    _story = True
    if data != "error": 
        if data == []:
            _story = False
        return render_template('story.html', data=data, username = username, story = _story)
    else:
        return jsonify({"message": "Something went wrong. Please try again after a while."})


@app.route("/uid/<string:username>")
def user_id(username):
    send_notify(f"Uid : {username}")
    uid = sp.scrape_user_id(username)
    return jsonify({username : uid})


@app.route("/uid/v2/<string:username>")
def user_id_v2(username):
    send_notify(f"Uid v2 : {username}")
    uid = sp.user_id_v2(username)
    return uid


@app.route("/username/<string:uid>")
def get_username(uid):
    send_notify(f"Username : {uid}")
    username = sp.get_username(uid)
    return username


@app.errorhandler(404)
def not_found(e):
  return jsonify({"message": f"{e}"}) 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
