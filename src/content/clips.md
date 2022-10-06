{%%

clips = include('bases/clips.yml')

for name in clips:
    print(include('inc/video.html', **clips[name], link=name + '.html'))

%%}
