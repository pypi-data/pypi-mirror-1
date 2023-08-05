#!/usr/bin/env python
import bitbucket
import os

def sync_dir(bucket_name, path, ignore_dirs=[]):
    bucket = bitbucket.BitBucket(bucket_name)
    for root, dirs, files in os.walk(path):
	for ignore in ignore_dirs:
	    if ignore in dirs:
		dirs.remove(ignore)
	for file in files:
	    fullpath = os.path.join(root, file)
	    try:
		if bucket.has_key(fullpath):
		    bits = bucket[fullpath]
		    bits.filename = fullpath
		else:
		    bits = bitbucket.Bits(filename=fullpath)
		    bucket[fullpath] = bits
	    except bitbucket.BitBucketEmptyError:
		print 'sync_dir: Empty File - Ignored %s' % fullpath
    return bucket

