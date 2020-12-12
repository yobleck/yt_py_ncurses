# python ncurses youtube browser

todo: color coding, new video notifications, properly secure client secrets and api key, dl videos and extract audio, comment sections, livestream staus

## requirements
  - Linux only for now
  - python 3.7+ (package manager of choice)
  - youtube-dl (pip)
  - mpv (package manager of choice)
  - imagemagick (package manager of choice)
  - google oath python libraries (pip install google-api-core, google-api-python-client, google-auth, google-auth-httplib2, google-auth-oauthlib, googleapis-common-protos)

## controls
  - s = subscription page
  - i = self channel info page
  - arrow keys = navigation
  - enter = select
  - backspace = go back a page
  - l/d/n = like/dislike/none on video page
  - t = show thumbnail on video page
  - space bar = stream video via youtube-dl and mpv
  
  ## known issues
    - possible api bug where it fails to return last subscription on page with maxResults=50 returning 49 subs
    - api livestream status request is ridiculously expensive
