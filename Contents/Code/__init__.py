PREFIX = '/video/pbskids'
NAME = 'PBS Kids'

PBSKIDS_URL = 'http://www.pbskids.org/video/'
PBSKIDS_SHOWS = 'http://pbskids.org/pbsk/video/api/getShows/?return=images'
VIDEO_LIST = 'http://pbskids.org/pbsk/video/api/getVideos/?startindex=%d&endindex=%d&program=%s&status=available&type=%s&return=airdate,expirationdate,rating'
VIDEO_URL = 'http://pbskids.org/pbsk/video/api/getVideos/?guid=%s'

OFFSET = 20

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():

    oc = ObjectContainer()
    json_obj = JSON.ObjectFromURL(PBSKIDS_SHOWS)

    for item in json_obj['items']:

        title = item['title']
        summary = String.StripTags(item['description'])

        if 'program-mezzanine-16x9' in item['images']:
            thumb = item['images']['program-mezzanine-16x9']['url']
        elif 'program-kids-square' in item['images']:
            thumb = item['images']['program-kids-square']['url']
        else:
            thumb = ''

        oc.add(DirectoryObject(
            key = Callback(ShowPage, title=title, thumb=thumb),
            title = title,
            summary = summary,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb)
        ))

    return oc

####################################################################################################
@route(PREFIX + '/show')
def ShowPage(title, thumb):

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(key=Callback(VideoPage, type='Episode', title=title), title='Full Episodes',
        thumb=Resource.ContentsOfURLWithFallback(url=thumb)
    ))

    oc.add(DirectoryObject(key=Callback(VideoPage, type='Clip', title=title), title='Clips',
        thumb=Resource.ContentsOfURLWithFallback(url=thumb)
    ))

    return oc

####################################################################################################
@route(PREFIX + '/videos', start=int)
def VideoPage(type, title, start=0):

    oc = ObjectContainer(title2=title)
    end = start+OFFSET

    json_obj = JSON.ObjectFromURL(VIDEO_LIST % (start, end, String.Quote(title, usePlus=True), type), cacheTime=CACHE_1DAY)

    for item in json_obj['items']:

        url = VIDEO_URL % item['guid']
        video_title = item['title']
        summary = item['description']
        duration = item['videos']['iphone']['length']

        try: thumb = item['images']['originalres_16x9']['url']
        except:
            try: thumb = item['images']['originalres_4x3']['url']
            except: thumb = ''

        if type == 'Clip':
            oc.add(VideoClipObject(url=url, title=video_title, summary=summary, duration=duration,
                thumb=Resource.ContentsOfURLWithFallback(thumb)
            ))
        else:
            oc.add(EpisodeObject(url=url, title=video_title, show=title, summary=summary, duration=duration,
                thumb=Resource.ContentsOfURLWithFallback(thumb)
            ))

    if int(json_obj['matched']) > end:
        oc.add(NextPageObject(key=Callback(VideoPage, type=type, title=title, start=end), title='More ...'))

    if len(oc) < 1:
        return ObjectContainer(header='Empty', message="There aren't any items")

    return oc
