import requests
import re
import json

url = 'https://mqfmnetwork.com/cahaya-tauhiid-kh-abdullah-gymnastiar/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

res = requests.get(url, headers=headers)
print("Page length:", len(res.text))

# Let's search the HTML for any .mp3
mp3s = set(re.findall(r'https?://[^"\']+\.mp3', res.text))
print("MP3s in HTML:", mp3s)

# Let's try the playlist URL again with GET and POST
pl_url = 'https://mqfmnetwork.com/?load=playlist.json&albums=7267&feed=1'
ajax_headers = headers.copy()
ajax_headers.update({
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': url
})

res_get = requests.get(pl_url, headers=ajax_headers)
print("GET PL status:", res_get.status_code)
print("GET PL length:", len(res_get.text))

res_post = requests.post(pl_url, headers=ajax_headers)
print("POST PL status:", res_post.status_code)
print("POST PL length:", len(res_post.text))
if len(res_post.text) > 0:
    print("POST PL content:", res_post.text[:200])

# Try admin-ajax.php ?
pl_ajax = 'https://mqfmnetwork.com/wp-admin/admin-ajax.php'
data = {
    'action': 'sonaar_music_playlist',
    'album_id': '7267'
}
res_ajax = requests.post(pl_ajax, headers=ajax_headers, data=data)
print("AJAX PL status:", res_ajax.status_code)
print("AJAX PL length:", len(res_ajax.text))
if len(res_ajax.text) > 0:
    print("AJAX PL content:", res_ajax.text[:200])
