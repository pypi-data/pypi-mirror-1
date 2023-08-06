#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Fileinfo caching.

"""


def writeCache(all):
    "Write file attribute values into one cache file of the containing folder."
    
    func = lambda rec:normpath(dirname(rec["path"]))
    cacheDict = groupby([a.__dict__ for a in all], func)
    for k, aList in cacheDict:
        for i, dic in enumerate(aList):
            aList[i]["path"] = normpath(aList[i]["path"])
        cachePath = normpath(join(k, "_fileinfoCachePickle.txt"))
        pickle.dump(aList, open(cachePath, "w"))
    
        print "written cache at path:", cachePath
        pp(aList)


def readCaches(paths):
    "Read fileinfo caches for given paths."
    
    res = {}
    cache = groupby(paths, lambda x:dirname(x))
    ## print "+++", cache
    for k in cache.keys():
        cachePath = join(k, "_fileinfoCachePickle.txt")
        ## print "***", k, cachePath
        if not exists(cachePath):
            continue
        f = open(cachePath, "r")        
        cacheDict = pickle.load(f)
        # [{'lc': 83, 'nkw': 54, 'path': 'find.py', 'wc': 280}, ...]
        cacheDict2 = groupby(cacheDict, lambda x:x["path"])
        pp(cacheDict2)
        # {'find.py': [{'path': 'find.py', 'wc': 280, 'lc': 83, 'nkw': 54}], ...}
        # for k in cacheDict2:
        #     cacheDict2[k] = cacheDict2[k][0]
        # {'find.py': {'path': 'find.py', 'wc': 280, 'lc': 83, 'nkw': 54}, ...}
        res.update(cacheDict2)
        
    for k in res:
        res[k] = res[k][0]

    ## print "read cache"
    pp(res)
    
    return res
