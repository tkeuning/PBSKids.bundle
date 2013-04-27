PREFIX = "/video/pbskids"
NAME = "PBS Kids"

PBSKIDS_URL   = "http://www.pbskids.org/video/"
PBSKIDS_SHOWS = "http://pbskids.org/go/video/js/org.pbskids.shows.js" #"http://pbskids.org/everything.html"
VIDEO_LIST    = "http://pbskids.org/pbsk/video/api/getVideos/?startindex=%d&endindex=%d&program=%s&status=available&type=%s&return=airdate,expirationdate,rating"
CATEGORY_LIST = "http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&query=CustomText|CategoryType|%s&query=HasReleases&field=title&field=thumbnailURL"

OFFSET = 20
VIDEO_URL = '%sid=%s'

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():

    oc = ObjectContainer()
    content = JSON.ObjectFromURL(PBSKIDS_SHOWS)

    for item in content:
        title = item['title']
        thumb = item['thumbnail2URL']
        summary = String.StripTags(item['description'])
        oc.add(DirectoryObject(key=Callback(ShowPage, title=title, thumb=thumb), title=title, summary=summary,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    return oc

####################################################################################################
@route(PREFIX + '/show')
def ShowPage(title, thumb):

    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(VideoPage, type='Episode', title=title), title="Full Episodes",
        thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
    oc.add(DirectoryObject(key=Callback(VideoPage, type='Clip', title=title), title="Clips",
        thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    return oc

####################################################################################################
@route(PREFIX + '/videos', start=int)
def VideoPage(type, title, start=0):

    oc = ObjectContainer(title2=title)
    end = start+OFFSET

    content = JSON.ObjectFromURL(VIDEO_LIST % (start, end, String.Quote(title, usePlus=True), type), cacheTime=CACHE_1DAY)

    for item in content['items']:
        series_url = item['series_url']

        if not series_url.endswith('/'):
            series_url = series_url + '/'

        url = VIDEO_URL % (series_url, item['id'])
        video_title = item['title']
        summary = item['description']
        duration = item['videos']['iphone']['length']

        try: thumb = item['images']['originalres_4x3']['url']
        except:
            try: thumb = item['images']['originalres_16x9']['url']
            except: thumb = ''

        if type == 'Clip':
            oc.add(VideoClipObject(url=url, title=video_title, summary=summary, duration=duration,
                thumb=Resource.ContentsOfURLWithFallback(thumb)))
        else:
            oc.add(EpisodeObject(url=url, title=video_title, show=title, summary=summary, duration=duration,
                thumb=Resource.ContentsOfURLWithFallback(thumb)))

    if int(content['matched']) > end:
        oc.add(NextPageObject(key=Callback(VideoPage, type=type, title=title, start=end), title="More ..."))

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There aren't any items")

    return oc
