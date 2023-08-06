""" This module implements the DecompressionMiddleware which tries to recognise
and extract the potentially compressed responses that may arrive. 
"""

import zipfile
import tarfile
import gzip
import bz2
from cStringIO import StringIO
from tempfile import mktemp

from scrapy import log
from scrapy.http import Response
from scrapy.core.downloader.responsetypes import responsetypes

class DecompressionMiddleware(object):
    """ This middleware tries to recognise and extract the possibly compressed
    responses that may arrive. """

    def __init__(self):
        self.decompressors = {
            'tar': self.is_tar,
            'zip': self.is_zip,
            'gz': self.is_gzip,
            'bz2': self.is_bzip2
        }

    def is_tar(self, response):
        try:
            tar_file = tarfile.open(name=mktemp(), fileobj=self.archive)
        except tarfile.ReadError:
            return False
        if tar_file.members:
            body = body=tar_file.extractfile(tar_file.members[0]).read()
            respcls = responsetypes.from_args(filename=tar_file.members[0].name, body=body)
            return response.replace(body=body, cls=respcls)
        else:
            raise self.ArchiveIsEmpty

    def is_zip(self, response):
        try:
            zip_file = zipfile.ZipFile(self.archive)
        except zipfile.BadZipfile:
            return False
        namelist = zip_file.namelist()
        if namelist:
            body = zip_file.read(namelist[0])
            respcls = responsetypes.from_args(filename=namelist[0], body=body)
            return response.replace(body=body, cls=respcls)
        else:
            raise self.ArchiveIsEmpty

    def is_gzip(self, response):
        try:
            gzip_file = gzip.GzipFile(fileobj=self.archive)
            decompressed_body = gzip_file.read()
        except IOError:
            return False
        respcls = responsetypes.from_args(body=decompressed_body)
        return response.replace(body=decompressed_body, cls=respcls)

    def is_bzip2(self, response):
        try:
            decompressed_body = bz2.decompress(self.body)
        except IOError:
            return False
        respcls = responsetypes.from_args(body=decompressed_body)
        return response.replace(body=decompressed_body, cls=respcls)

    def extract(self, response):
        """ This method tries to decompress the given response, if possible,
        and returns a tuple containing the resulting response, and the name
        of the used decompressor """

        self.body = response.body
        self.archive = StringIO()
        self.archive.write(self.body)

        for decompressor in self.decompressors.keys():
            self.archive.seek(0)
            new_response = self.decompressors[decompressor](response)
            if new_response:
                return (new_response, decompressor)
        return (response, None)

    def process_response(self, request, response, spider):
        if isinstance(response, Response) and response.body:
            response, format = self.extract(response)
            if format:
                log.msg('Decompressed response with format: %s' % format, log.DEBUG, domain=spider.domain_name)
        return response
