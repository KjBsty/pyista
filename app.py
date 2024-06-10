from scraper import scraper as sp
from datetime import datetime, timezone

from flask import Flask, render_template, request, send_file, jsonify
import requests
from io import BytesIO
import urllib.parse

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"message": "Hello World!"})


@app.route('/posts/<string:username>')
def posts(username):
    data = sp.scrape_user_posts(sp.scrape_user_id(username))
    user_posts = []
    posts_count = data[1]
    
    if data != "error":
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
        return jsonify({"message": "Something went wrong"})


@app.route('/get')
def image_proxy():
    url = request.args.get('url')
    response = requests.get(url)
    return send_file(BytesIO(response.content), mimetype=response.headers['Content-Type'])


@app.route('/user/<string:username>')
def user(username):
    data = sp.user_info(username)
    return data


@app.route('/story/<string:username>')
def story(username):
    data = sp.story(username)
    stories = []
    _story = True
    print(data)
    if data != [] or data != "error": 
        for item in data:
            url = item["img_url"]
            story = {
                "img_url" : f"/get?url={urllib.parse.quote(url)}",
                "video_url" : item["video_url"],
                "taken_at" : item["taken_at"],
                "expires" : item["expires"]
            }
            stories.append(story)

        if stories == []:
            _story = False

        return render_template('story.html', data=stories, username = username, story = _story)
    else:
        return jsonify({"message": "Something went wrong. Please try again after a while."})


@app.errorhandler(404)
def not_found(e):
  return jsonify({"message": f"{e}"}) 

if __name__ == '__main__':
    app.run()
