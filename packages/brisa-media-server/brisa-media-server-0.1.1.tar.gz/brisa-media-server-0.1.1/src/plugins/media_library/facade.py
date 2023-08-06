# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php or see LICENSE file.
# Copyright 2007-2008 Brisa Team <brisa-develop@garage.maemo.org>

__all__ = ('init', 'get_file_path', 'get_audio_all', 'get_audio_item',
           'get_audio_album', 'get_audio_albums', 'get_audio_genre',
           'get_audio_genres', 'get_audio_artist', 'get_audio_artists',
           'get_image_item', 'get_images_local', 'get_video_item',
           'get_videos_local', 'get_conn')

""" Database facade for the Media Library plugin.
"""

from sqlite3 import dbapi2 as sqlite

from brisa.upnp.didl.didl_lite import *
from brisa.core import log


db_path = ''
webserver = None

log = log.getLogger('plugins.media-library.facade')


def init(path, websrv):
    global db_path, webserver
    db_path = path
    webserver = websrv


def exit():
    global webserver
    webserver = None


def get_conn():
    return sqlite.connect(db_path)


def get_file_path(id):
    """ Returns the file path with this id.
    """
    conn = get_conn()
    path = ''

    try:
        c = conn.execute('SELECT path FROM files WHERE id=?', (id, ))
        path = str(c.fetchall()[0][0])
        c.close()
    except Exception, e:
        log.error('error retrieving file path: %s' % e)

    conn.close()
    return path


def get_audio_item(id):
    """ Returns the audio item (if exists) given its id.
    """
    conn = get_conn()
    url = '%s/media_library/audio-' % webserver.get_listen_url()
    c = conn.execute('SELECT files.path, audios.id, '\
                     'audios.title, audio_albums.name, '\
                     'audio_artists.name, audio_genres.name, '\
                     'audios.trackno FROM audios INNER JOIN '\
                     'audio_albums INNER JOIN audio_artists '\
                     'INNER JOIN audio_genres INNER JOIN files ON '\
                     'audios.album_id=audio_albums.id AND '\
                     'audios.genre_id=audio_genres.id AND '\
                     'audios.artist_id=audio_artists.id '\
                     'where files.id=? AND audios.id=?',
                     (id, id))
    result = c.fetchall()
    c.close()
    conn.close()

    if not result or len(result) < 1:
        return []

    r = result[0]
    track = MusicTrack('media_library:audio-%d' % r[1], '', r[2], genres=[r[5]],
                       artists=[r[4]], albums=[r[3]],
                       original_track_number=r[6])
    track.add_resource(Resource('%s%d' % (url, r[1]), 'http-get:*:audio/%s:*' %
                       str(r[0]).split('.')[-1]))

    return [track]


def get_audio_all():
    """ Returns all audio.
    """
    conn = get_conn()
    url = '%s/media_library/audio-' % webserver.get_listen_url()
    c = conn.execute('SELECT files.path, audios.id, '\
                     'audios.title, audio_albums.name, '\
                     'audio_artists.name, audio_genres.name, '\
                     'audios.trackno FROM audios INNER JOIN '\
                     'audio_albums INNER JOIN audio_artists '\
                     'INNER JOIN audio_genres INNER JOIN files ON '\
                     'audios.album_id=audio_albums.id AND '\
                     'audios.genre_id=audio_genres.id AND '\
                     'audios.artist_id=audio_artists.id AND '\
                     'audios.id = files.id', ())

    ans = []

    for r in c:
        track = MusicTrack('media_library:audio-%d' % r[1], '', r[2],
                           genres=[r[5]], artists=[r[4]], albums=[r[3]],
                           original_track_number=r[6])
        track.add_resource(Resource('%s%d' % (url, r[1]),
                           'http-get:*:audio/%s:*' % str(r[0]).split('.')[-1]))
        ans.append(track)

    c.close()
    conn.close()
    return ans


def get_audio_genres():
    """ Returns all audio genres.
    """
    conn = get_conn()
    c = conn.execute('SELECT ? || id, name FROM audio_genres',
                     ('media_library:genre-', ))

    result = []

    for r in c:
        if r[1] == 'genre':
            r = (r[0], 'Unknown Genre')
        result.append(MusicGenre(**dict(zip(['id', 'title'], r))))

    c.close()
    conn.close()
    return result


def get_audio_genre(id):
    """ Returns an audio genre given its id.
    """
    conn = get_conn()
    url = '%s/%s/audio-' % (webserver.get_listen_url(), 'media_library')
    c = conn.execute('SELECT files.path, audios.id, '\
                     'audios.title, audio_albums.name, '\
                     'audio_artists.name, audio_genres.name, '\
                     'audios.trackno FROM audios INNER JOIN '\
                     'audio_albums INNER JOIN audio_artists '\
                     'INNER JOIN audio_genres INNER JOIN files ON '\
                     'audios.album_id=audio_albums.id AND '\
                     'audios.genre_id=audio_genres.id AND '\
                     'audios.artist_id=audio_artists.id AND '\
                     'audios.id = files.id WHERE audios.genre_id '\
                     '= ?', (id, ))
    ans = []

    for r in c:
        track = MusicTrack('media_library:audio-%d' % r[1], '', r[2],
                           genres=[r[5]], artists=[r[4]], albums=[r[3]],
                           original_track_number=r[6])
        track.add_resource(Resource('%s%d' % (url, r[1]),
                           'http-get:*:audio/%s:*' % str(r[0]).split('.')[-1]))
        ans.append(track)

    c.close()
    conn.close()
    return ans

def get_audio_artists():
    """ Returns all audio artists.
    """
    conn = get_conn()
    c = conn.execute('SELECT ? || id, name FROM audio_artists',
                     ('media_library:artist-', ))

    rows = c.fetchall()
    c.close()
    conn.close()

    return [MusicArtist(**dict(zip(['id', 'title'], r))) for r in rows]


def get_audio_artist(id):
    """ Returns an audio artist given its id.
    """
    conn = get_conn()
    url = '%s/%s/audio-' % (webserver.get_listen_url(), 'media_library')
    c = conn.execute('SELECT files.path, audios.id, '\
                     'audios.title, audio_albums.name, '\
                     'audio_artists.name, audio_genres.name, '\
                     'audios.trackno FROM audios INNER JOIN '\
                     'audio_albums INNER JOIN audio_artists '\
                     'INNER JOIN audio_genres INNER JOIN files ON '\
                     'audios.album_id=audio_albums.id AND '\
                     'audios.genre_id=audio_genres.id AND '\
                     'audios.artist_id=audio_artists.id AND '\
                     'audios.id = files.id WHERE audios.artist_id '\
                     '= ?', (id, ))

    ans = []

    for r in c:
        track = MusicTrack('media_library:audio-%d' % r[1], '', r[2],
                           genres=[r[5]], artists=[r[4]], albums=[r[3]],
                           original_track_number=r[6])
        track.add_resource(Resource('%s%d' % (url, r[1]), 'http-get:*:audio/%s:*' %
                                    str(r[0]).split('.')[-1]))
        ans.append(track)

    c.close()
    conn.close()
    return ans


def get_audio_albums():
    """ Returns all audio albums.
    """
    conn = get_conn()
    c = conn.execute('SELECT ? || id, name FROM audio_albums',
                     ('media_library:album-', ))
    ret = [MusicAlbum(**dict(zip(['id', 'title'], r))) for r in c]
    c.close()
    conn.close()
    return ret


def get_audio_album(id):
    """ Returns an audio album given its id.
    """
    conn = get_conn()
    url = '%s/%s/audio-' % (webserver.get_listen_url(), 'media_library')
    c = conn.execute('SELECT files.path, audios.id, '\
                     'audios.title, audio_albums.name, '\
                     'audio_artists.name, audio_genres.name, '\
                     'audios.trackno FROM audios INNER JOIN '\
                     'audio_albums INNER JOIN audio_artists '\
                     'INNER JOIN audio_genres INNER JOIN files ON '\
                     'audios.album_id=audio_albums.id AND '\
                     'audios.genre_id=audio_genres.id AND '\
                     'audios.artist_id=audio_artists.id AND '\
                     'audios.id = files.id WHERE audios.album_id '\
                     '= ?', (id, ))

    ans = []

    for r in c:
        track = MusicTrack('media_library:audio-%d' % r[1], '', r[2],
                           genres=[r[5]], artists=[r[4]], albums=[r[3]],
                           original_track_number=r[6])
        track.add_resource(Resource('%s%d' % (url, r[1]),
                           'http-get:*:audio/%s:*' % str(r[0]).split('.')[-1]))
        ans.append(track)

    c.close()
    conn.close()
    return ans


def get_images_local():
    """ Returns all local images.
    """
    conn = get_conn()
    url = '%s/%s/image-' % (webserver.get_listen_url(), 'media_library')
    c = conn.execute('SELECT images.id, images.title, files.path '\
                     'FROM images INNER JOIN files ON images.id '\
                     '= files.id', ())
    ans = []

    for r in c:
        item = ImageItem('media_library:image-%d' % r[0], title=r[1])
        item.add_resource(Resource('%s%d' % (url, r[0]), 'http-get:*:image/%s:*' %
                          str(r[2]).split('.')[-1]))
        ans.append(item)

    c.close()
    conn.close()
    return ans


def get_image_item(id):
    """ Returns an image given its id.
    """
    conn = get_conn()
    url = '%s/media_library/image-' % webserver.get_listen_url()
    c = conn.execute('SELECT images.id, images.title, files.path '\
                     'FROM images INNER JOIN files ON images.id '\
                     '= files.id WHERE images.id=?', (id, ))
    rows = c.fetchall()
    c.close()
    conn.close()

    if not rows or len(rows) < 1:
        return []

    r = rows[0]

    item = ImageItem('media_library:image-%d' % r[0], title=r[1])
    item.add_resource(Resource('%s%d' % (url, r[0]), 'http-get:*:image/%s:*' %
                      str(r[2]).split('.')[-1]))

    return [item]


def get_videos_local():
    """ Returns all local videos.
    """
    conn = get_conn()
    url = '%s/media_library/video-' % webserver.get_listen_url()
    c = conn.execute('SELECT videos.id, videos.title, '\
                     'videos.artist, files.path FROM videos '\
                     'INNER JOIN files ON videos.id = files.id', ())
    ans = []

    for r in c:
        item = VideoItem('media_library:video-%d' % r[0], title=r[1],
                         actors=[r[2]])
        item.add_resource(Resource('%s%d' % (url, r[0]), 'http-get:*:video/%s:*' %
                          str(r[3]).split('.')[-1]))
        ans.append(item)

    c.close()
    conn.close()
    return ans


def get_video_item(id):
    """ Returns a video item given its id.
    """
    conn = get_conn()
    url = '%s/media_library/video-' % webserver.get_listen_url()
    c = conn.execute('SELECT videos.id, videos.title, '\
                                'videos.artist, files.path FROM '\
                                'videos INNER JOIN files ON videos.id = '\
                                'files.id WHERE videos.id=?', (id, ))
    rows = c.fetchall()
    c.close()
    conn.close()

    if not rows or len(rows) < 1:
        return []

    item = VideoItem('media_library:video-%d' % r[0], title=r[1], actors=[r[2]])
    item.add_resource(Resource('%s%d' % (url, r[0]), 'http-get:*:video/%s:*' %
                               str(r[3]).split('.')[-1]))
    return [item]


def get_playlists():
    """ Returns all playlists.
    """
    conn = get_conn()
    url = '%s/media_library/playlist-' % webserver.get_listen_url()
    ans = []

    c = conn.execute('SELECT id, title FROM playlists', ())

    for r in c:
        playlist = PlaylistItem('media_library:playlist-%d' % r[0], title=r[1])
        playlist.add_resource(Resource('%s%d' % (url, r[0]),
                              'http-get:*:audio/mpegurl:*'))
        ans.append(playlist)

    c.close()
    conn.close()
    return ans


def get_playlist(id):
    """ Returns a single playlist item based on its id.
    """
    conn = get_conn()
    url = '%s/media_library/playlist-' % webserver.get_listen_url()
    c = conn.execute('SELECT title FROM playlists WHERE id=?', (id, ))
    rows = c.fetchall()
    c.close()
    conn.close()

    if not rows or len(rows) < 1:
        return []

    playlist = PlaylistItem('media_library:playlist-%d' % id, title=rows[0][0])
    playlist.add_resource(Resource('%s%d' % (url, id),
                          'http-get:*:audio/mpegurl:*'))

    return [playlist]
