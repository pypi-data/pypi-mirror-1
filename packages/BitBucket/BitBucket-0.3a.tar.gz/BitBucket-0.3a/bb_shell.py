#!/usr/bin/env python
import bitbucket
import cmd
import sys
import getopt
import os

class BBCmdLine(cmd.Cmd):

    def __init__(self):
	cmd.Cmd.__init__(self)
	self.connection = bitbucket.connect()
	self.current_bucket = None
	self.page_size = 100
	self.prompt = '> '

    def do_cd(self, arg):
	if arg not in self.connection.keys():
	    print 'unknown bucket: %s' % arg
	else:
	    self.current_bucket = self.connection[arg]
	    self.prompt = '%s> ' % self.current_bucket.name

    def help_cd(self):
	print 'cd -- change current bucket to bucket_name'
	print 'SYNOPSIS'
	print 'cd bucket_name'
	print '   bucket_name is a valid bucket'

    def do_cdup(self, arg):
	self.current_bucket = None
	self.prompt = '> '

    def help_cdup(self):
	print 'cd -- move back up to top level of bucket'
	print 'SYNOPSIS'
	print 'cdup'

    def do_delete(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    key = arg.strip()
	    try:
		bits = self.current_bucket[key]
		del self.current_bucket[key]
	    except KeyError:
		print '++ %s not found ++' % key
	    except bitbucket.BitBucketResponseError, e:
		print 'the following error occured:'
		print '%d: %s' % (e.status, e.reason)

    def help_delete(self):
	print 'delete -- delete an S3 object'
	print 'SYNOPSIS'
	print 'delete key'
	print '   key is the key of the S3 object'

    def do_get(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    arglist = arg.split()
	    if len(arglist) != 2:
		help_get()
	    else:
		key = arglist[0]
		filename = arglist[1]
		bits = self.current_bucket[key]
		bits.to_file(filename)

    def help_get(self):
	print 'get -- retrieve an object from S3 to a local file'
	print 'SYNOPSIS'
	print 'get key filename'
	print '   key is the key of the S3 object to retrieve'
	print '   filename name of local file to hold S3 object'

    def do_getacl(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    key = arg.strip()
	    bits = self.current_bucket[key]
	    acl = bits.get_acl()
	    print acl

    def do_getbucketacl(self, arg):
	bucket_name = arg.strip()
	bucket = self.connection[bucket_name]
	acl = bucket.get_acl()
	print acl

    def do_get_md(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    key = arg.strip()
	    try:
		bits = self.current_bucket[key]
		print '%s:' % key
		print '\tetag=%s' % bits.etag
		print '\tlast_modified: %s' % bits.last_modified
		print '\tstorage_class: %s' % bits.storage_class
		for key in bits.metadata.keys():
		    print '\t%s: %s' % (key, bits[key])
	    except KeyError:
		print '++ %s not found ++' % key

    def help_get_md(self):
	print 'get_md -- retrieve metadata for an S3 object'
	print 'SYNOPSIS'
	print 'get_md key'
	print '   key is the key of the S3 object'

    def do_ls(self, arg):
	arglist = arg.split()
	if len(arglist) > 0:
	    bucket_name = arglist[0]
	    bucket = self.connection[bucket_name]
	elif self.current_bucket != None:
	    bucket = self.current_bucket
	else:
	    for key in self.connection.keys():
		print key
	    return
	bucket.page_size = self.page_size
	it = iter(bucket)
	try:
	    for i in range(0, self.page_size):
		b = it.next()
		print b.key
	    print '...listing truncated:',
	    print ' use pagesize command to increase page size'
	except StopIteration:
	    print 'listing complete'
	del it

    def help_ls(self):
	print 'ls -- list contents of current location'
	print 'SYNOPSIS'
	print 'ls [bucket_name]'
	print 'bucket_name'
	print '   Specifiy the bucket_name to list, else use current bucket'

    def do_mkbucket(self, arg):
	arglist = arg.split()
	if len(arglist) != 1:
	    help_mkbucket()
	else:
	    bucket_name = arglist[0]
	    try:
		self.connection.get_bucket(bucket_name, headers)
	    except bitbucket.BitBucketCreateError:
		print 'bucket %s already exists' % bucket_name
	    except bitbucket.BitBucketResponseError, e:
		print 'the following error occured:'
		print '%d: %s' % (e.status, e.reason)

    def help_mkbucket(self):
	print 'mkbucket -- create a new S3 bucket'
	print 'SYNOPSIS'
	print 'mkbucket bucket_name'
	print '   bucket_name is the name of the S3 bucket'

    def do_pagesize(self, arg):
	arglist = arg.split()
	if len(arglist) == 0:
	    print 'current pagesize is %d' % self.page_size
	elif len(arglist) == 1:
	    self.page_size = int(arglist[0])
	    print 'pagesize set to %d' % self.page_size
	else:
	    help_pagesize()

    def help_pagesize(self):
	print 'pagesize -- list or change the page size'
	print 'SYNOPSIS'
	print 'pagesize [new_page_size]'
	print '   new_page_size is the new page size, otherwise print current'

    def do_put(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    arglist = arg.split()
	    if len(arglist) != 1:
		help_put()
	    else:
		filename = arglist[0]
		key = arglist[1]
		if os.path.exists(filename):
		    bits = bitbucket.Bits(filename)
		    self.current_bucket[key] = bits

    def help_put(self):
	print 'put -- store a local file to an S3 bucket'
	print 'SYNOPSIS'
	print 'put file key'
	print '   file is the path to the local file to put to S3'
	print '   key is the key used to store the file in S3'

    def do_quit(self, arg):
	sys.exit(1)

    def help_quit(self):
	print 'syntax: quit',
	print '-- terminates the application'

    def do_rmbucket(self, arg):
	bucket_name = arg.strip()
	try:
	    if self.current_bucket == bucket_name:
		self.current_bucket = None
		self.prompt = '> '
	    self.connection.delete_bucket(bucket_name)
	except bitbucket.BitBucketResponseError, e:
	    print 'the following error occured:'
	    print '%d: %s' % (e.status, e.reason)

    def help_rmbucket(self):
	print 'rmbucket -- delete an S3 bucket'
	print 'SYNOPSIS'
	print 'rmbucket bucket_name'
	print '   bucket_name is the name of the S3 bucket'

    def do_rm_all_keys(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    self.current_bucket.delete_all_keys()
	
    def do_setacl(self, arg):
	if self.current_bucket == None:
	    print 'Please set your current bucket first'
	else:
	    arglist = arg.split()
	    if len(arglist) != 2:
		help_setacl()
	    else:
		try:
		    policy = arglist[0]
		    key = arglist[1]
		    if policy not in bitbucket._canned_access_policies:
			print 'invalid policy: %s' % policy
		    else:
			bits = self.current_bucket[key]
			bits.set_canned_acl(policy)
		except KeyError:
		    print 'unknown key: %s' % key

    def help_setacl(self):
	print 'setacl -- set the ACL for an S3 object to a canned ACL'
	print 'SYNOPSIS'
	print 'setacl policy key'
	print '   policy is one of:'
	print '     private|public-read|public-read-write|authenticated-read'
	print '   key is the key of the S3 object'

    def do_setbucketacl(self, arg):
	arglist = arg.split()
	if len(arglist) != 2:
	    help_setbucketacl()
	else:
	    policy = arglist[0]
	    bucket_name = arglist[1]
	    if policy not in bitbucket._canned_access_policies:
		print 'invalid policy: %s' % policy
	    else:
		bucket = self.connection[bucket_name]
		bucket.set_canned_acl(policy)

    def help_setbucketacl(self):
	print 'setbucketacl -- set the ACL for an S3 bucket to a canned ACL'
	print 'SYNOPSIS'
	print 'setbucketacl policy bucket_name'
	print '   policy is one of:'
	print '     private|public-read|public-read-write|authenticated-read'
	print '   bucket_name is the key of the S3'

    def do_user(self, arg):
	arglist = arg.split()
	if len(arglist) != 2:
	    help_user()
	else:
	    access_key = arglist[0]
	    secret_key = arglist[1]
	    self.connection = bitbucket.connect(access_key, secret_key)

    def help_user(self):
	print 'user -- identify yourself to S3 and establish new connection'
	print 'SYNOPSIS'
	print 'user access_key secret_key'
	print '    access_key is your AWS Access Key ID'
	print '    secret_key is your AWS Secret Access Key'

    # shortcuts/aliases
    do_bye = do_quit
    do_dir = do_ls

if __name__ == "__main__":
    cli = BBCmdLine()
    cli.cmdloop()
