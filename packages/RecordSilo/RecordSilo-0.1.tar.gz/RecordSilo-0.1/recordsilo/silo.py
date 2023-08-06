#!/usr/bin/env python

# OAIPMH Scraper

from persiststate import PersistentState

from pairtree import PairtreeStorageClient
from pairtree import id_encode, id_decode
from pairtree import FileNotFoundException

from datetime import datetime

from os import path, mkdir

import simplejson

import logging

import sys, traceback

import re

logger = logging.getLogger("RecordSilo")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)

PAIRTREE_ROOT_DIR = "pairtree_root"

NAMASTE_PATTERN = re.compile(r"[^0=|1=|2=|3=|4=]")

class HarvestedRecord(object):
    """Convenience class, handling the persistence of some basic metadata about a harvest item, as well as organising the items files, metadata or otherwise."""
    def __init__(self, pairtree_object, last_modified_date=None, manifest_filename="__manifest.json"):
        self.po = pairtree_object
        self.item_id = self.po.id
        self.manifest_filename = manifest_filename
        if not last_modified_date:
            last_modified_date = datetime.now().isoformat()
        self.itempath = self.path_to_item()
        self.revert(last_modified_date=last_modified_date)
    
    def _setup_version_dir(self, version, last_modified_date=None):
        if not last_modified_date:
            if self.manifest['last_modified_date']:
                last_modified_date = self.manifest['last_modified_date']
            else:
                last_modified_date = datetime.now().isoformat()
        if version not in self.manifest['versions']:
            self.manifest['versions'].append(version)
        self.manifest['version_dates'][version] = last_modified_date
        self.manifest['metadata_files'][version] = []
        self.manifest['files'][version] = []
        self.set_version_date(version, last_modified_date)
        self.po.add_bytestream_by_path(path.join(str(version), "4=%s" % id_encode(self.item_id)), self.item_id)

    def _init_manifests_emptydatastructures(self):
        self.item_id = self.manifest['item_id']
        if not self.manifest.has_key('metadata_files'):
            self.manifest['metadata_files'] = {}
        if not self.manifest.has_key('files'):
            self.manifest['files'] = {}
        for version in self.manifest['versions']:
            if not self.manifest['metadata_files'].has_key(version):
                self.manifest['metadata_files'][version] = []

    def _reload_filelist(self, version):
        if not self.manifest['files'].has_key(version) and version in self.manifest['versions']:
            self.manifest['files'][version] = []
            # init from disc
            for filename in [x for x in self.po.list_parts(version) if NAMASTE_PATTERN.match(x) != None]:
                self.manifest['files'][version].append(filename)

    def _init_manifest(self):
        """Set up the template for the item's manifest"""
        self.manifest['metadata_files'] = {}
        self.manifest['files'] = {}
        self.manifest['item_id'] = self.po.id
        self.manifest['versions'] = []
        self.manifest['version_dates'] = {}
        self.manifest['currentversion'] = "1"
        self._setup_version_dir("1", self.manifest['last_modified_date'])
        self.manifest.sync()
    
    def _read_last_modified_date(self, version = None):
        if not version:
            version = self.manifest['currentversion']
        date_namaste_tags = takewhile(lambda x: x.startswith("3="), self.po.list_parts(str(version)))
        if len(date_namaste_tags) >= 1:
            lmd = date_namaste_tags.pop()[2:]   # take the first tag and remove the '3='
            lmd = id_decode(lmd)                # reverse the 'pairtree' encoding of the date
            self.manifest['last_modified_date'] = lmd

    def _incr_version(self, latest_version):
        try:
            v = int(latest_version)
            return str(v+1)
        except:
            return latest_version + "_new"

    def path_to_item(self):
        return self.po.fs._id_to_dirpath(self.po.id)
    
    def revert(self, **kw):
        if not path.isdir(self.itempath):
            logger.error("Path to harvested item does not exist")
            raise Exception("Path to harvested item does not exist")
        try:
            self.manifest = PersistentState(self.itempath, self.manifest_filename)
            self.manifest.revert()
            if not self.manifest:
                if kw.has_key('last_modified_date'):
                    self.manifest['last_modified_date'] = kw['last_modified_date']
                else:
                    self.manifest['last_modified_date'] = datetime.now().isoformat()
                self._init_manifest()
                logger.debug(self.manifest)
            self._init_manifests_emptydatastructures()
            logger.debug(self.manifest)
        except Exception, e:
            logger.error("Failed to setup on-disc stored state for this item.")
            traceback.print_exc(file=sys.stdout)

    # Some dict methods
    def __setitem__(self, key, item):
        if key not in ["metadata_files", "files"]:
            self.manifest[key]
    def __getitem__(self, key):
        try:
            return self.manifest[key]
        except KeyError:
            raise KeyError(key)

    def keys(self): return self.manifest.keys()
    def has_key(self, key): return self.manifest.has_key(key)
    def items(self): return self.manifest.items()
    def values(self): return self.manifest.values()

    def sync(self):
        self.manifest.sync()
        
    def revert_manifest(self):
        self.manifest.revert()
        self._init_manifests_emptydatastructures()
    
    def add_stream(self, filename, stream, metadata=True):
        if metadata and filename not in self.manifest['metadata_files'][self.manifest['currentversion']]:
            self.manifest['metadata_files'][self.manifest['currentversion']].append(filename)
        if filename not in self.manifest['files'][self.manifest['currentversion']]:
            self.manifest['files'][self.manifest['currentversion']].append(filename)
        self.sync()
        return self.po.add_bytestream_by_path(path.join(str(self.manifest['currentversion']), filename), stream)
    
    def get_stream(self, filename):
        if filename in self.manifest['files'][self.manifest['currentversion']]:
            return self.po.get_bytestream_by_path(path.join(str(self.manifest['currentversion']), filename),
                                                  streamable=True)
        else:
            raise FileNotFoundException
    
    def del_stream(self, filename, versions=[]):
        if not versions:
            versions = [self.manifest['currentversion']]
        for version in versions:
            try:
                self.po.del_file_by_path(path.join(str(version), filename))
                if filename in self.manifest['metadata_files'][version]: 
                    self.manifest[metadata_files].remove(filename)
                self._reload_filelist(version)
            except FileNotFoundException:
                logger.info("File %s not found at version %s and so cannot be deleted" % (filename, version))
        self.sync()

    def set_version_cursor(self, version):
        if version in self.manifest['versions']:
            self.manifest['currentversion'] = version
            self._read_last_modified_date()
            return True
        else:
            logger.error("Version %s does not exist" % version)
            return False
        
    def get_versions(self):
        return self.manifest['versions']

    def increment_version(self, last_modified_date, clone_previous_version=False):
        self.manifest['last_modified_date'] = last_modified_date
        latest_version = self.manifest['versions'][-1]
        new_version = self._incr_version(latest_version)
        self._setup_version_dir(new_version, last_modified_date)
        if clone_previous_version:
            logger.error("Sorry, cloning is a TODO atm")
            pass
        self.manifest['currentversion'] = new_version
        self._read_last_modified_date()
        self.sync()
        return new_version
    
    def create_new_version(self, version, last_modified_date=None):
        version = str(version)
        if version not in self.manifest['versions']:
            self._setup_version_dir(version, last_modified_date)
        else:
            logger.error("Cannot create new version %s - version directory already exists" % version)

    def del_version(self, version):
        if version not in self.manifest['versions']:
            logger.error("Version %s does not exist" % version)
            return False
        else:
            self.manifest['versions'].remove(version)
            if self.manifest['files'].has_key(version):
                del self.manifest['files'][version]
            if self.manifest['metadata_files'].has_key(version):
                del self.manifest['metadata_files'][version]
            if self.manifest['versions']:
                # TODO revert object manifest to previous version if current version is being deleted
                self.manifest['currentversion'] = self.manifest['versions'][-1]
                self._read_last_modified_date()
            else:
                self.manifest['currentversion'] = "1"
                self._read_last_modified_date()
                self._setup_version_dir(version, last_modified_date)
            self.sync()
            return self.po.del_path(version, recursive=True)

    def set_version_date(self, version, date):
        if version in self.manifest['versions']:
            self.manifest['version_dates'][version] = date
            self.po.add_bytestream_by_path(path.join(str(version), "3=%s" % id_encode(date)), date)
            return True
        else:
            logger.error("Version %s does not exist" % version)
            return False

    def get_version_cursor(self):
        return self.manifest['currentversion']

class Silo(object):
    """Item persistence layer - uses pairtree as a basis for storage."""
    def __init__(self, storage_dir, uri_base=None, **kw):
        self.state = PersistentState()
        self.state['storage_dir'] = storage_dir
        if not uri_base:
            uri_base = "info:"
        self.state['uri_base'] = uri_base
        self.state.update(kw)
        self._init_storage()
        
    def _init_storage(self):
        try:
            self._store = PairtreeStorageClient(self.state['uri_base'], self.state['storage_dir'], shorty_length=2)
            if not self.state.set_filepath(self.state['storage_dir']):
                raise Exception
            else:
                self.state.revert()
        except OSError:
            logger.error("Cannot make storage directory")
            raise Exception("Cannot make storage directory")
        except Exception:
            logger.error("Cannot setup the state persistence file at %s/%s" % (self.state['storage_dir'], PERSISTENCE_FILENAME))
            raise Exception("Cannot setup the state persistence file at %s/%s" % (self.state['storage_dir'], PERSISTENCE_FILENAME))

    def exists(self, item_id):
        return self._store.exists(item_id)

    def get_item(self, item_id):
        p_obj = self._store.get_object(item_id)
        return HarvestedRecord(p_obj)

    def del_item(self, item_id):
        return self._store.delete_object(item_id)


