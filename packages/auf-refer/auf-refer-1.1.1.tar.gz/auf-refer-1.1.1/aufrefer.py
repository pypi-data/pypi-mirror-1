#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Librairie de copie et mise à jour des référentiels AuF.

Copyright ©2009  Agence universitaire de la Francophonie
Licence : LGPL version 3
Auteur : Progfou <jean-christophe.andre@auf.org>

Dépendances Debian : python >= 2.5, python-simplejson
"""

CONFIG_FILE = '/etc/auf-refer/auf-refer.conf'

DIR_BASE = '/var/lib/auf-refer'
URL_BASE = 'http://intranet.auf/auf-refer'
AVAILABLE_LIST = 'auf-refer.json'

lines = filter(lambda l: not l.startswith('#'), file(CONFIG_FILE))
config = dict(map(lambda l: map(lambda s: s.strip(), l.split('=')), lines))

DIR_BASE = config.get('DIR_BASE', DIR_BASE).rstrip('/')
URL_BASE = config.get('URL_BASE', URL_BASE).rstrip('/')
AVAILABLE_LIST = config.get('AVAILABLE_LIST', AVAILABLE_LIST)

__all__ = ( 'DIR_BASE', 'URL_BASE', 'AVAILABLE_LIST' )

TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

from os import listdir, utime, unlink
from os.path import join, exists, getmtime
from time import gmtime, strftime
from calendar import timegm
from urllib2 import Request, urlopen, HTTPError, URLError
from cStringIO import StringIO
from gzip import GzipFile
from simplejson import loads

def path(referentiel):
    return join(DIR_BASE, referentiel)

def _update(referentiel, force=False):
    headers = {}
    headers['Accept-Encoding'] = 'gzip,x-gzip'
    if force:
        headers['Pragma'] = 'no-cache'
    filename = join(DIR_BASE, referentiel)
    if exists(filename):
        # n'effectuer le chargement qu'en cas de nouvelle version
        mtime = gmtime(getmtime(filename))
        headers['If-Modified-Since'] = strftime(TIME_FORMAT, mtime)
    else:
        # fichier vide à date très ancienne pour déclencher la synchro
        try:
            file(filename, 'a').close()
        except IOError, e:
            raise RuntimeError, \
                "La création du référentiel '%s' a été refusée :\n  %s" \
                                                        % (referentiel, e)
        utime(filename, (0, 0))
    url = URL_BASE + '/' + referentiel
    req = Request(url, None, headers)
    try:
        u = urlopen(req)
    except HTTPError, e:
        if e.code == 304:
            return
        raise RuntimeError, \
            "L'URL suivante renvoie un code d'erreur %s :\n  %s" \
                                                        % (e.code, url)
    except URLError:
        raise RuntimeError, "L'URL suivante est inaccessible :\n  %s" % url
    i = u.info()
    if referentiel.endswith('.json') and i.type != 'application/json':
        u.close()
        raise RuntimeError, \
            "Le type des données chargées n'est pas JSON mais '%s'.\n" \
            "URL concernée : %s" % (i.type, url)
    data = u.read()
    if i.get('content-encoding') in ('gzip','x-gzip'):
        data = GzipFile('', 'r', 0, StringIO(data)).read()
    u.close()
    if referentiel.endswith('.json'):
        try:
            loads(data, encoding='utf-8')
        except ValueError:
            raise RuntimeError, "Les données ne sont pas au format JSON.\n" \
                                "URL concernée : %s" % url
    # si on est arrivé jusqu'ici c'est que tout va bien... on enregistre !
    try:
        f = file(filename, 'wb')
    except IOError, e:
        raise RuntimeError, \
            "L'écriture du référentiel '%s' a été refusée :\n  %s" \
                                                        % (referentiel, e)
    f.write(data)
    f.close()
    # on fixe la date donnée par le serveur, le cas échéant
    mtime = i.getdate('last-modified')
    if mtime:
        mtime = timegm(mtime)
        utime(filename, (mtime, mtime))

def get(referentiel, force=False):
    filename = join(DIR_BASE, referentiel)
    if not exists(filename):
        _update(referentiel, force)
    try:
        f = open(filename, 'rb')
    except IOError:
        raise RuntimeError, "Le référentiel '%s' est indisponible." \
                                                            % referentiel
    data = f.read()
    f.close()
    if referentiel.endswith('.json'):
        try:
            data = loads(data, encoding='utf-8')
        except ValueError:
            raise RuntimeError, \
                "Les données du référentiel '%s' ne sont pas au format JSON.\n" \
                "Le fichier est peut-être corrompu, essayez de forcer une mise à jour." % referentiel
    # XXX: voir comment faire : data.last_modified = gmtime(getmtime(filename))
    return data

def add(referentiel, force=False):
    filename = join(DIR_BASE, referentiel)
    if exists(filename):
        raise RuntimeError, \
            "Le référentiel '%s' avait déjà été ajouté." % referentiel
    _update(referentiel, force)

def remove(referentiel):
    filename = join(DIR_BASE, referentiel)
    if not exists(filename):
        raise RuntimeError, "Le référentiel '%s' est absent." % referentiel
    try:
        unlink(filename)
    except (IOError, OSError), e:
        raise RuntimeError, \
            "La suppression du référentiel '%s' a été refusée :\n  %s" \
                                                        % (referentiel, e)

def update(referentiel=False, force=False):
    if referentiel:
        _update(referentiel, force)
        return
    error_messages = []
    for referentiel in listdir(DIR_BASE):
        try:
            _update(referentiel, force)
        except Exception, e:
            error_messages.append(str(e))
    if error_messages:
        raise RuntimeError, '\n'.join(error_messages)

def list():
    return listdir(DIR_BASE)

def list_available(force=False):
    return get(AVAILABLE_LIST, force)

def add_available(force=False):
    missing = set(list_available(force)) - set(listdir(DIR_BASE))
    for referentiel in missing:
        _update(referentiel, force)

