# Python ncurses YouTube Browser

todo: color coding, new video notifications, properly secure client secrets and api key, dl videos and extract audio, comment sections, livestream staus

## Requirements
  - Linux only for now
  - python 3.7+ (package manager of choice)
  - youtube-dl (pip)
  - mpv (package manager of choice)
  - imagemagick (package manager of choice)
  - google oath python libraries (pip install google-api-core, google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib, googleapis-common-protos)

## Controls
  - s = subscription page
  - i = self channel info page
  - arrow keys = navigation
  - enter = select
  - backspace = go back a page
  - l/d/n = like/dislike/none on video page
  - t = show thumbnail on video page
  - space bar = stream video via youtube-dl and mpv
  
## Tested With
  - KDE(5.20.4) Manjaro Linux(5.8)
  - Konsole(20.08.3)/xterm(362)
  - python 3.8.6
  - youtube-dl/mpv/imagemagick current version
  
## Known Issues
  - possible api bug where it fails to return last subscription on page with maxResults=50 returning 49 subs
  - api livestream status request is ridiculously expensive
  - ctrl + backspace on xterm
