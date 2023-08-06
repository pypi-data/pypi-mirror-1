#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, Thomas Jost <thomas.jost@gmail.com>
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Regular expressions matching files and folders to exclude from the backup
EXCLUDES = [
    "/Cache",
    "/OfflineCache/",
    "\.mfasl$",
    "/urlclassifier",
    "/lock$",
    "/parent.lock$",
    "/.parentlock$",
]

import os, os.path, re, sys, tarfile, time
from optparse import OptionParser

# Parse command line
parser = OptionParser()
parser.add_option("-f", "--folder", dest="profile_path", help="profile folder to be saved")
parser.add_option("-u", "--user", dest="fd_user", help="username for connection to FileDropper (optional)")
parser.add_option("-p", "--password", dest="fd_pass", help="password for connection to FileDropper (optional)")
parser.add_option("-c", "--crypt-to", dest="crypt_to", help="comma-separated list of recipients for GPG encryption of archive file (optional)")
(options, args) = parser.parse_args()

# Check if constraints are respected
if options.profile_path is None:
    print "No profile specified"
    sys.exit(1)
if (options.fd_user is not None and options.fd_pass is None) or (options.fd_user is None and options.fd_pass is not None):
    print "Username AND password needed"
    sys.exit(1)

profile_name = os.path.basename(options.profile_path)
date = time.strftime("%Y%m%d_%H%M%S")
archive_name = "%s-%s.tar.bz2" % (profile_name, date)

# Compile exclusion regexps
EXCLUDES_RE = []
for regexp in EXCLUDES:
    r = re.compile(regexp)
    EXCLUDES_RE.append(r)

# Uncompressed size
total_size = 0

# Exclusion decision function
def is_excluded(filename):
    global EXCLUDES_RE, total_size
    for regexp in EXCLUDES_RE:
        if regexp.search(filename):
            return True
    total_size += os.path.getsize(filename)
    return False

# Open the destination tar archive
tar = tarfile.open(archive_name, 'w:bz2')

# Add the data to the archive
tar.add(options.profile_path, profile_name, exclude=is_excluded)

tar.close()

# Display archive name and sizes
print "Profile saved to %s" % archive_name
archive_size = os.path.getsize(archive_name)
print "%.1f MB --> %.1f MB" % (total_size/(1024**2), archive_size/(1024**2))

# Encrypt the archive if needed
if options.crypt_to is not None:
    import GnuPGInterface

    gpg = GnuPGInterface.GnuPG()
    gpg.options.meta_interactive = 0

    # Add recipients
    gpg.options.recipients = options.crypt_to.split(',')

    # Open input and output file
    encrypted_archive_name = archive_name + '.gpg'
    src = open(archive_name, 'rb')
    dst = open(encrypted_archive_name, 'wb')

    # Run GnuPG
    process = gpg.run(['--encrypt'], attach_fhs={'stdin': src, 'stdout': dst})

    # Cleanup
    process.wait()
    dst.close()
    src.close()

    # Use the encrypted file for the rest of the process
    archive_name = encrypted_archive_name

    print "Archive encrypted to %s (%.1f MB)" % (archive_name, os.path.getsize(archive_name)/(1024**2))

# Upload to FileDropper if needed
if options.fd_user is not None and options.fd_pass is not None:
    import FileDropper

    def cb(sent, total):
        if total < 0:
            print "Upload: %.4f %%" % (float(sent)/float(archive_size))
    FileDropper.upload_callback = cb

    fd = FileDropper.FileDropper()
    fd.login(options.fd_user, options.fd_pass)

    # Upload the file
    url = fd.upload(archive_name)

    # Get the file ID
    lst = fd.list()
    file_id = -1
    for line in lst:
        if line[6] == url:
            file_id = line[1]
            break
    if file_id == -1:
        # File not found in list!
        raise Exception("Error in upload, could not get file ID, permissions not set")

    # Set the permissions
    fd.set_perm(file_id, FileDropper.FD_PERM_PRIVATE)

    # Logout
    fd.logout()

    print "File uploaded to FileDropper: %s" % url
