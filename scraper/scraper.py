import json
import requests
from datetime import datetime, timezone
from typing import Dict, Optional
import jmespath
import logger as log

INSTAGRAM_APP_ID = "936619743392459"

def parse_post(data: Dict) -> Dict:
    """Reduce post dataset to the most important fields"""
    # log.info(f"parsing post data {data['shortcode']}")
    result = jmespath.search(
        """{
        id: id,
        shortcode: shortcode,
        dimensions: dimensions,
        src: display_url,
        src_attached: edge_sidecar_to_children.edges[].node.display_url,
        has_audio: has_audio,
        video_url: video_url,
        views: video_view_count,
        plays: video_play_count,
        likes: edge_media_preview_like.count,
        location: location.name,
        taken_at: taken_at_timestamp,
        related: edge_web_media_to_related_media.edges[].node.shortcode,
        type: product_type,
        video_duration: video_duration,
        music: clips_music_attribution_info,
        is_video: is_video,
        tagged_users: edge_media_to_tagged_user.edges[].node.user.username,
        captions: edge_media_to_caption.edges[].node.text,
        related_profiles: edge_related_profiles.edges[].node.username,
        comments_count: edge_media_to_parent_comment.count,
        comments_disabled: comments_disabled,
        comments_next_page: edge_media_to_parent_comment.page_info.end_cursor,
        comments: edge_media_to_parent_comment.edges[].node.{
            id: id,
            text: text,
            created_at: created_at,
            owner: owner.username,
            owner_verified: owner.is_verified,
            viewer_has_liked: viewer_has_liked,
            likes: edge_liked_by.count
        }
    }""",
        data,
    )
    return result

def parse_post_info(data: Dict) -> Dict:
    """Reduce post dataset to the most important fields"""
    result = jmespath.search(
        """{
        id: id,
        shortcode: shortcode,
        dimensions: dimensions,
        src: display_url,
        src_attached: edge_sidecar_to_children.edges[].node.display_url,
        has_audio: has_audio,
        video_url: video_url,
        views: video_view_count,
        plays: video_play_count,
        likes: edge_media_preview_like.count,
        location: location.name,
        taken_at: taken_at_timestamp,
        related: edge_web_media_to_related_media.edges[].node.shortcode,
        type: product_type,
        video_duration: video_duration,
        music: clips_music_attribution_info,
        is_video: is_video,
        tagged_users: edge_media_to_tagged_user.edges[].node.user.username,
        captions: edge_media_to_caption.edges[].node.text,
        related_profiles: edge_related_profiles.edges[].node.username,
        comments_count: edge_media_to_parent_comment.count,
        comments_disabled: comments_disabled,
        comments_next_page: edge_media_to_parent_comment.page_info.end_cursor,
        comments: edge_media_to_parent_comment.edges[].node.{
            id: id,
            text: text,
            created_at: created_at,
            owner: owner.username,
            owner_verified: owner.is_verified,
            viewer_has_liked: viewer_has_liked,
            likes: edge_liked_by.count
        }
    }""",
        data,
    )
    return result


def scrape_post_info(url_or_shortcode: str) -> dict:
    """Scrape single Instagram post data"""
    if "http" in url_or_shortcode:
        shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
    else:
        shortcode = url_or_shortcode

    variables = {
        "shortcode": shortcode,
        "child_comment_count": 20,
        "fetch_comment_count": 100,
        "parent_comment_count": 24,
        "has_threaded_comments": True,
    }
    query_hash = "b3055c01b4b222b8a47dc12b090e4e64"
    url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={json.dumps(variables)}"
    headers = {"x-ig-app-id": INSTAGRAM_APP_ID}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return parse_post_info(data["data"]["shortcode_media"])
    else:
        return response.json()


def scrape_user_posts(user_id: str, page_size=50, max_pages: Optional[int] = None):
    if user_id != "An error occurred":

        """Scrape all posts of an instagram user of given numeric user id"""
        base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
        variables = {
            "id": user_id,
            "first": page_size,
            "after": None,
        }
        _page_number = 1
        all_posts = []
        post_count = 0
        while True:
            url = base_url + json.dumps(variables)
            result = requests.get(url, headers={"x-ig-app-id": INSTAGRAM_APP_ID})
            data = json.loads(result.content)
            if "message" in data and data["message"] == 'Please wait a few minutes before you try again.':
                # log.error(f"Rate limit exceeded. Waiting for a minute... | Data response: {data}")
                print(data["message"])
                time.sleep(60) 
                continue
            posts = data["data"]["user"]["edge_owner_to_timeline_media"]
            for post in posts["edges"]:
                all_posts.append(parse_post(post["node"]))  
            page_info = posts["page_info"]
            if _page_number == 1:
                # log.success(f"\nscraping total {posts['count']} posts of {user_id}")
                print(f"\nscraping total {posts['count']} posts of {user_id}")
                post_count = posts['count']
            else:
                # log.success(f"\nscraping posts page {_page_number}\n")
                print(f"\nscraping posts page {_page_number}\n")
            if not page_info["has_next_page"]:
                break
            if variables["after"] == page_info["end_cursor"]:
                break
            variables["after"] = page_info["end_cursor"]
            _page_number += 1
            if max_pages and _page_number > max_pages:
                break
        
        return all_posts, post_count
    else:
        return "error"

def scrape_user_id(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    BASE_CONFIG = {
        "asp": True,
        "country": "CA",
    }
    INSTAGRAM_APP_ID = "936619743392459"

    headers = {"x-ig-app-id": INSTAGRAM_APP_ID}
    response = requests.get(url, headers=headers, params=BASE_CONFIG)

    
    if response.status_code == 200:
        try:
            user_data = response.json()
            user_id = user_data.get('data', {}).get('user', {}).get('id')
            return(user_id)
        except:
            print("An error occurred")
            return("An error occurred")
        
    else:
        return("An error occurred")
    

def user_info(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    BASE_CONFIG = {
        "asp": True,
        "country": "CA",
    }
    INSTAGRAM_APP_ID = "936619743392459"

    headers = {"x-ig-app-id": INSTAGRAM_APP_ID}
    response = requests.get(url, headers=headers, params=BASE_CONFIG)

    if response.status_code == 200:
        try:
            user_data = response.json()
            return(user_data)
        except:
            return "error"
        
    else:
        return "error"
    

def converted_date(timestamp):
    date = datetime.fromtimestamp(timestamp, timezone.utc)
    return date.strftime("%d/%m/%Y %H:%M:%S")

def story(username: str):
    if username != "An error occurred":
        stories = []
        try:
            url = f"https://anonyig.com/api/ig/story?url=https%3A%2F%2Fwww.instagram.com%2Fstories%2F{username}%2F"
            result = requests.get(url)
            if result:
                data = json.loads(result.content)
                posts = data["result"]
                for post in posts:
                    story = {
                        "img_url" : post["image_versions2"]["candidates"][0]["url"],
                        "video_url" : post["video_versions"][0]["url"],
                        "taken_at" : converted_date(post["taken_at"]),
                        "expires" : converted_date(post["video_versions"][0]["url_signature"]["expires"])
                    }
                    stories.append(story)
                return stories
            else:
                return "error"
        except:
            return "error"
    else:
        return "error"


def user_posts(user_id: str, page_size=50, max_pages: Optional[int] = None):
    """Scrape all posts of an instagram user of given numeric user id"""
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": None,
    }
    _page_number = 1
    all_posts = []  
    url = base_url + json.dumps(variables)
    result = requests.get(url, headers={"x-ig-app-id": INSTAGRAM_APP_ID})
    data = json.loads(result.content)
    with open(f'{user_id}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # while True:
    #     url = base_url + json.dumps(variables)
    #     result = requests.get(url, headers={"x-ig-app-id": INSTAGRAM_APP_ID})
    #     data = json.loads(result.content)
    #     if "message" in data and data["message"] == 'Please wait a few minutes before you try again.':
    #         log.error(f"Rate limit exceeded. Waiting for a minute... | Data response: {data}")
    #         time.sleep(60) 
    #         continue
    #     posts = data["data"]["user"]["edge_owner_to_timeline_media"]
    #     for post in posts["edges"]:
    #         all_posts.append(parse_post(post["node"]))  
    #     page_info = posts["page_info"]
    #     if _page_number == 1:
    #         log.success(f"\nscraping total {posts['count']} posts of {user_id}")
    #     else:
    #         log.success(f"\nscraping posts page {_page_number}\n")
    #     if not page_info["has_next_page"]:
    #         break
    #     if variables["after"] == page_info["end_cursor"]:
    #         break
    #     variables["after"] = page_info["end_cursor"]
    #     _page_number += 1
    #     if max_pages and _page_number > max_pages:
    #         break
    
    # return all_posts
