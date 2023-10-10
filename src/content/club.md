
{%%

for page in compiled_pages:
    posts = []
    if 'club/' in page:
        posts.append(page)
    posts = posts[::-1]
    for post in posts:
        club_meta = get_meta(post)
        user = 'Plagiat le ?? à ??' if 'user' not in club_meta else club_meta['user']
        color = 'black' if 'color' not in club_meta else club_meta['color']
        title = page.split('/')[-1].split('.md')[0] if 'title' not in club_meta else club_meta['title']
        type = 'text' if 'type' not in club_meta else club_meta['type']
        club_content = include(post)
        print(f"""
        <div class="club-sandwish" id="{title}">
            <a href="#{title}" class="club-loser" title="{user}" style="background:{color}">
                {user[0]}
            </a>
            <div class="club-content {type}">
            {club_content}
            </div>
        </div>
        """)

 %%}
