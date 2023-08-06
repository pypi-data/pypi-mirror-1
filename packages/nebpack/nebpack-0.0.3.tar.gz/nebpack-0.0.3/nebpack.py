
import hashlib
import os
import types

import git
import git.utils
import jsonical

class Pack(object):
    def __init__(self, dirname, actor=None):
        if not os.path.exists(dirname):
            self.repo = git.Repo.init_bare(dirname)
        else:
            self.repo = git.Repo(dirname)
        self.actor = None
        if actor is not None:
            self.actor = git.Actor.from_string(actor)
        self._active = None
        self._known = None

    @property
    def active_ids(self):
        "Dictionary of active object ID's."
        if self._active is None:
            data = self.get("objects/active")
            if data is None:
                data = {}
            self._active = data
        return self._active

    @property
    def known_ids(self):
        "Dictionary of all object ID's"
        if self._known is None:
            data = self.get("objects/known")
            if data is None:
                data = {}
            self._known = data
        return self._known

    def get_keyword(self, kwname):
        return self.lookup(kwname)

    def add_keyword(self, kwname, kwval):
        self.add((kwname, kwval), mesg="Adding keyword: %s" % kwname)

    def rem_keyword(self, kwname):
        self.remove(kwname, mesg="Removing keyword: %s" % kwname)

    def get_reference(self, refid):
        return self.lookup("ref/%s" % refid)

    def add_reference(self, refid, ref):
        self.add(("ref/%s" % refid, ref), mesg="Adding reference: %s" % refid)

    def rem_reference(self, refid):
        self.remove("ref/%s" % refid)

    def get_seqid(self):
        return self.lookup("seq/current")

    def add_seqid(self, seqid):
        known = []
        if not self.repo.empty:
            tree = self.repo.tree()/"seq"
            if tree is not None:
                obj = tree/"known"
                known = jsonical.loads(obj.data)
        if seqid not in known:
            known.append(seqid)
        
        objs = [
            ("seq/current", seqid.strip()),
            ("seq/known", known)
        ]
        self.add(objs, mesg="Updating sequence id: %s" % seqid)

    def get_feature_id(self, fid):
        if not isinstance(fid, types.StringTypes):
            raise TypeError("fid must be a string.")
        count = 0
        while fid != self.known_ids[fid] and count < 10:
            fid = self.known_ids[fid]
            count += 1
        if fid != self.known_ids[fid]:
            raise ValueError("Failed to get feature id: %s" % fid)
        return fid

    def get_feature(self, fid):
        fid = self.get_feature_id(fid)
        return self.lookup("objects/%s" % fid)

    def has_feature(self, fid):
        return fid in self.known_ids

    def add_feature(self, feature, prev=None):
        desc_id = self.desc_id(feature)
        if prev is not None:
            prev_id = self.get_feature_id(prev)
            feature["previous"] = prev_id
            for k, v in self.active_ids.iteritems():
                if k not in (prev_id, desc_id) and v == prev_id:
                    raise KeyError(
                        "Invalid link to previous id: %s -> %s" % (k, v)
                    )
            # A feature can be its own description and already be
            # deleted when removing features.
            if prev_id in self.active_ids:
                del self.active_ids[prev_id]
        elif desc_id in self.active_ids:
            raise ValueError("Feature description %r exists." % desc_id)

        fid = self.jshash(feature)
        if not feature.get("deleted", False):
            self.active_ids[fid] = fid
            self.active_ids[desc_id] = fid
        self.known_ids[fid] = fid
        self.known_ids[desc_id] = fid

        objs = [
            ("objects/%s" % self.jshash(feature), feature),
            ("objects/active", self.active_ids),
            ("objects/known", self.known_ids)
        ]
        self.add(objs, mesg="Adding feature: %s" % fid)
        return fid

    def rem_feature(self, feature):
        desc_id = self.desc_id(feature)
        fid = self.get_feature_id(desc_id)
        newfeat = {
            "location": feature["location"],
            "type": feature["type"],
            "deleted": True
        }
        del self.active_ids[fid]
        # Technically a feature can be exactly its description.
        if desc_id in self.active_ids:
            del self.active_ids[desc_id]
        return self.add_feature(newfeat, prev=fid)

    def get(self, path):
        if self.repo.empty:
            return None
        tree = self.repo.tree()
        parts = git.utils.split(path)
        for p in parts:
            tree = tree/p
            if tree is None:
                return None
        if isinstance(tree, git.Blob):
            return jsonical.loads(tree.data)
        return tree

    def lookup(self, path):
        ret = self.get(path)
        if ret is None:
            raise ValueError("Path %r not found" % path)
        return ret

    def add(self, objs, mesg=None):
        if not isinstance(objs, list):
            objs = [objs]
        idx = self.repo.index()
        for o in objs:
            idx.add(o[0], jsonical.dumps(o[1], indent=4) + "\n")
        idx.commit(mesg or "NEB Pack update.", actor=self.actor)

    def remove(self, paths, mesg=None):
        if not isinstance(paths, list):
            paths = [paths]
        idx = self.repo.index()
        for p in paths:
            idx.remove(p)
        idx.commit(mesg or "NEB Pack update.", actor=self.actor)

    def desc_id(self, desc):
        if isinstance(desc, dict):
            desc = {"location": desc["location"], "type": desc["type"]}
            desc = self.jshash(desc)
        return desc

    def jshash(self, arg):
        return hashlib.sha1(jsonical.dumps(arg)).hexdigest().upper()

