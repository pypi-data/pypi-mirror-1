
import hashlib
import os

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
        if isinstance(fid, dict):
            fid = self.desc_id(fid)
        data = self.get("objects/%s" % fid)
        if isinstance(data, basestring):
            return data
        return fid

    def get_feature(self, fid):
        fid = self.get_feature_id(fid)
        return self.lookup("objects/%s" % fid)

    def has_feature(self, fid):
        fid = self.get_feature_id(fid)
        ret = self.get(fid)
        return ret is not None

    def add_feature(self, feature, prev=None):
        if prev is not None:
            feature["previous"] = self.get_feature_id(prev)
        else:
            desc_id = self.desc_id(feature)
            if self.get("objects/%s" % desc_id) is not None:
                raise ValueError("Feature description %r exists." % desc_id)

        fid = self.jshash(feature)

        objs = [
            ("objects/%s" % self.jshash(feature), feature),
            ("objects/%s" % self.desc_id(feature), fid)
        ]
        self.add(objs, mesg="Adding feature: %s" % fid)

    def rem_feature(self, feature):
        fid = self.get_feature_id(feature)
        newfeat = {
            "location": feature["location"],
            "type": feature["type"],
            "deleted": True
        }
        self.add_feature(newfeat, prev=fid)

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

