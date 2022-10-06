{%%

data = include('bases/clips.yml')[current_page]
peertube = parse_peertube_url(data['url'])

%%}
----
nav: clips
title: {% data['title'] %}
----

### {% data['title'] %}

<div class="iframe">
    <iframe src="{% peertube['iframe'] %}?warningTitle=0&peertubeLink=0&title=0" allow="fullscreen"></iframe>
</div>


### Téléchargement

- [1080p]({% peertube['1080p'] %})
- [720p]({% peertube['720p'] %})
- [360p]({% peertube['360p'] %})

{%%

notes = include('content/clips/%s.md' % current_page)

if 'ERROR' not in notes:

    print('### Notes d\'intentions')
    print(notes)


%%}
