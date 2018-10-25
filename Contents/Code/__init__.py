import urllib2
import ssl

PREFIX = '/video/pbskids'
NAME = 'PBS Kids'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

PBSKIDS_URL = 'https://www.pbskids.org/video/'
PBSKIDS_SHOWS = 'https://pbskids.org/pbsk/video/api/getShows/?return=images'
VIDEO_LIST = 'https://pbskids.org/pbsk/video/api/getVideos/?startindex=%d&endindex=%d&program=%s&status=available&type=%s&return=airdate,expirationdate,rating'
VIDEO_URL = 'https://pbskids.org/pbsk/video/api/getVideos/?guid=%s'
SHOW_ICON_URL = 'http://www-tc.pbskids.org/shell/images/content/show-bubbles/square/%s.png'
OFFSET = 20

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME

####################################################################################################
@handler(PREFIX, NAME, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()
    req = urllib2.Request(PBSKIDS_SHOWS)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    show_data = urllib2.urlopen(req, context=ssl_context).read()
    json_obj = JSON.ObjectFromString(show_data)

    for item in json_obj['items']:
        title = item['title']
        summary = String.StripTags(item['description'])
        # API now uses slug for program id
        if 'cove_slug' in item:
            slug = item['cove_slug']

            # The API appears to no longer serve thumbnail URLs
            # This hack gets some thumbnails, in some cases the 
            # slug matches the image filename on the pbs site.
            # Fails for some shows.
            thumb = SHOW_ICON_URL % slug

            oc.add(DirectoryObject(
                key = Callback(ShowPage, title=title, thumb=thumb, slug=slug),
                title = title,
                summary = summary,
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/show')
def ShowPage(title, thumb, slug=''):

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key = Callback(VideoPage, type='Episode', title=title, slug=slug),
        title = 'Full Episodes',
        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
    ))

    oc.add(DirectoryObject(
        key = Callback(VideoPage, type='Clip', title=title, slug=slug),
        title = 'Clips',
        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
    ))

    return oc

####################################################################################################
@route(PREFIX + '/videos', start=int)
def VideoPage(type, title, slug, start=0):

    oc = ObjectContainer(title2=title)
    end = start+OFFSET
    
    req = urllib2.Request(VIDEO_LIST % (start, end, String.Quote(slug, usePlus=True), type))
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    video_list = urllib2.urlopen(req, context=ssl_context).read()
    json_obj = JSON.ObjectFromString(video_list)

    for item in json_obj['items']:

        url = VIDEO_URL % item['guid']
        video_title = item['title']
        summary = item['description']
        try: duration = item['videos']['iphone']['length']
        except: duration = None

        thumb = ''
        images = ['kids-mezzannine-16x9', 'originalres_16x9', 'kids-mezzannine-4x3', 'originalres_4x3']

        for img in images:
            if img in item['images'] and 'url' in item['images'][img] and item['images'][img]['url']:
                thumb = item['images'][img]['url']
                break

        if type == 'Clip':
            oc.add(VideoClipObject(
                url = url,
                title = video_title,
                summary = summary,
                duration = duration,
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
            ))
        else:
            oc.add(EpisodeObject(
                url = url,
                title = video_title,
                show = title,
                summary = summary,
                duration = duration,
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
            ))

    if int(json_obj['matched']) > end:

        oc.add(NextPageObject(
            key = Callback(VideoPage, type=type, title=title, start=end),
            title = 'More ...'
        ))

    if len(oc) < 1:
        return ObjectContainer(header='Empty', message="There aren't any items")

    return oc
