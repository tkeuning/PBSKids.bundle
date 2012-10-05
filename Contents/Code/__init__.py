VIDEO_PREFIX  = "/video/pbskids"
NAME          = "PBS Kids"

PBSKIDS_URL   = "http://www.pbskids.org/video/"
PBSKIDS_SHOWS = "http://pbskids.org/everything.html"
PBS_JSON      = "http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&startIndex=1&endIndex=500&sortField=airdate&sortDescending=true&query=contentCustomBoolean|isClip|%s&field=airdate&field=author&field=bitrate&field=description&field=format&field=length&field=PID&field=thumbnailURL&field=title&field=URL&contentCustomField=isClip&param=affiliate|prekPlayer&field=categories&field=expirationDate&query=categories|%s"
CATEGORY_LIST = "http://pbs.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=6HSLquMebdOkNaEygDWyPOIbkPAnQ0_C&query=CustomText|CategoryType|%s&query=HasReleases&field=title&field=thumbnailURL"

ART           = "art-default.jpg"
ICON          = "icon-default.png"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb=R(ICON)

####################################################################################################
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ShowsList, categoryType="Show", title="Shows"), title="Shows"))
    oc.add(DirectoryObject(key=Callback(ShowsList, categoryType="Channel", title="Topics"), title="Topics"))
    return oc

####################################################################################################
def ShowPage(title, thumb):
    oc = ObjectContainer(title2=title)
    
    oc.add(DirectoryObject(key=Callback(VideoPage, clip='false', title=title), title="Full Episodes", thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    oc.add(DirectoryObject(key=Callback(VideoPage, clip='true', title=title), title="Clips", thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    if len(oc) == 0:
        return ObjectContainer(header="Empty", message="There aren't any items")
    else:
        return oc

####################################################################################################
def VideoPage(clip, title):
    oc = ObjectContainer(title2=title)
    show_title = title.replace(' ', '%20').replace('&', '%26')  ### FORMATTING FIX
    content = JSON.ObjectFromURL(PBS_JSON % (clip, show_title), cacheTime=CACHE_1DAY)
    for item in content['items']:
        thumb = item['thumbnailURL']
        link = item['URL']
        video_title = item['title']
        summary = item['description']
        duration = item['length']
        
        if clip == 'true':
            oc.add(VideoClipObject(url=link, title=video_title, summary=summary, duration=int(duration), thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
        else:
            oc.add(EpisodeObject(url=link, title=video_title, show=title, summary=summary, duration=int(duration), thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    if len(oc) == 0:
        return ObjectContainer(header="Empty", message="There aren't any items")
    else:
        return oc

####################################################################################################
def ShowsList(categoryType, title):
    oc = ObjectContainer(title2=title)
    content = JSON.ObjectFromURL(CATEGORY_LIST % categoryType)
    for item in content['items']:
        title = item['title']
        thumb = item['thumbnailURL']
        if thumb != "":
            if "Channel Sample" not in title:
                if categoryType == "Show":
                    oc.add(DirectoryObject(key=Callback(ShowPage, title=title, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
                else:
                    oc.add(DirectoryObject(key=Callback(VideoPage, title=title, clip='true'), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    return oc
