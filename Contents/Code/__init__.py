NAME = "ABC Family"
SHOWS = "http://abcfamily.go.com/shows"
IMG_BASE = "http://cdn.static.abcfamily.com/service/image/ratio/id/%s/dim/320.16x9.jpg"

ICON = R('icon-default.png')
ART = R('art-default.jpg')

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

####################################################################################################
@handler('/video/abcfamily', NAME, thumb=ICON, art=ART)
def MainMenu():

    oc = ObjectContainer()

    if not Client.Platform in ('Android', 'iOS', 'Roku') and not (Client.Platform == 'Safari' and Platform.OS == 'MacOSX'):
        oc.header = 'Not supported'
        oc.message = 'This channel is not supported on %s' % (Client.Platform if Client.Platform is not None else 'this client')
        return oc

    html = HTML.ElementFromURL(SHOWS)

    for item in html.xpath('//section[@class="moduleBody"]/article'):

        title = item.xpath('.//a/@title')[0]

        if title.lower() in ['abc family movies']:
            continue

        url = item.xpath('.//a/@href')
        thumb_data = item.xpath('.//img/@data-properties')[0]
        thumb_id = JSON.ObjectFromString(thumb_data)['image']['src']
        thumb = IMG_BASE % thumb_id

        oc.add(DirectoryObject(
            key = Callback(Episodes, url=url, title=title),
            title = title,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
        ))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no shows listed." )
    else:
        return oc

####################################################################################################
@route('/video/abcfamily/episodes')
def Episodes(url, title):

    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)

    # Locked videos have lockedEpisode in the article class, so only pulling unlocked videos
    for item in html.xpath('//div[@data-module="latest episodes"]//article[@class="item fep available"]'):

        url = item.xpath('.//h4/a/@href')[0]
        ep_title = item.xpath('.//h4/a//text()')[0]
        thumb_data = item.xpath('.//img/@data-properties')[0]
        thumb_id = JSON.ObjectFromString(thumb_data)['image']['src']
        thumb = IMG_BASE % thumb_id
        ep_info = item.xpath('.//div/span[1]//text()')[0].strip()
        episode = ep_info.split()[1].split('E')[1].strip()
        season = ep_info.split('S')[1].split()[0].strip()
        originally_available_at = Datetime.ParseDate(item.xpath('.//div/span[2]//text()')[0].strip()).date()

        oc.add(EpisodeObject(
            url = url,
            title = ep_title,
            show = title,
            season = int(season),
            index = int(episode),
            thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
            originally_available_at = originally_available_at
        ))

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are currently no unlocked videos available for this show." )
    else:
        return oc
