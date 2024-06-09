from scraper import scraper as sp
from datetime import datetime, timezone

from flask import Flask, render_template, request, send_file
import requests
from io import BytesIO
import urllib.parse

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World!"


@app.route('/posts/<string:username>')
def posts(username):
    data = sp.scrape_user_posts(sp.scrape_user_id(username))
    user_posts = []
    for item in data:
        # shortcode = data.get("shortcode")
        shared_date = item.get("taken_at")
        converted_date = datetime.fromtimestamp(shared_date, timezone.utc)
        user_post = {
            "video_url" : item.get("video_url"),
            "src" : f"/image_proxy?url={urllib.parse.quote(item.get('src'))}",
            "views" : item.get("views"),
            "likes" : item.get("likes"),
            # plays_ = sp.scrape_post_info(shortcode)
            # plays = plays_.get("plays")
            
            "formatted_date" : converted_date.strftime("%d/%m/%Y"),
            "captions" : item.get("captions")
        }
        user_posts.append(user_post)

    return render_template('index.html', data=user_posts, username = username)


@app.route('/image_proxy')
def image_proxy():
    url = request.args.get('url')
    response = requests.get(url)
    return send_file(BytesIO(response.content), mimetype=response.headers['Content-Type'])

if __name__ == '__main__':
    app.run()
