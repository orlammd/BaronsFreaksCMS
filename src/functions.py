"""
Define custom functions here
"""

def parse_peertube_url(url):
    peertube_domain = 'videos.domainepublic.net'
    if peertube_domain in url:
        id = url.split('/')[-1]
        return {
            'thumbnail': 'https://%s/lazy-static/previews/%s.jpg' % (peertube_domain, id),
            'iframe': 'https://%s/videos/embed/%s' % (peertube_domain, id),
            '1080p': 'https://%s/download/videos/%s-1080.mp4' % (peertube_domain, id),
            '720p': 'https://%s/download/videos/%s-720.mp4' % (peertube_domain, id),
            '360p': 'https://%s/download/videos/%s-360.mp4' % (peertube_domain, id),
        }
    else:
        return {
            'thumbnail': '',
            'iframe': ''
        }


def video_link(name):
    return include('inc/video.html', **include('bases/clips.yml')[name], link='%s.html' % name)

def img(src, **k):
    return include('inc/img.html', src=src, **k)
