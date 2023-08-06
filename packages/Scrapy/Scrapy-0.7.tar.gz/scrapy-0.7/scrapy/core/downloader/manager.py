"""
Download web pages using asynchronous IO
"""

from time import time

from twisted.internet import reactor, defer
from twisted.python.failure import Failure

from scrapy.core.exceptions import IgnoreRequest
from scrapy.conf import settings
from scrapy.utils.defer import mustbe_deferred
from scrapy import log
from .middleware import DownloaderMiddlewareManager
from .handlers import download_any


class SiteInfo(object):
    """This is a simple data record that encapsulates the details we hold on
    each domain which we are scraping.
    """
    def __init__(self, download_delay=None, max_concurrent_requests=None):
        if download_delay is None:
            self.download_delay = settings.getint('DOWNLOAD_DELAY')
        else:
            self.download_delay = download_delay
        if download_delay:
            self.max_concurrent_requests = 1
        elif max_concurrent_requests is None:
            self.max_concurrent_requests = settings.getint('REQUESTS_PER_DOMAIN')
        else:
            self.max_concurrent_requests =  max_concurrent_requests

        self.active = set()
        self.queue = []
        self.transferring = set()
        self.closing = False
        self.lastseen = 0

    def free_transfer_slots(self):
        return self.max_concurrent_requests - len(self.transferring)

    def needs_backout(self):
        # use self.active to include requests in the downloader middleware
        return len(self.active) > 2 * self.max_concurrent_requests


class Downloader(object):
    """Mantain many concurrent downloads and provide an HTTP abstraction.
    It supports a limited number of connections per spider and many spiders in
    parallel.
    """

    def __init__(self):
        self.sites = {}
        self.middleware = DownloaderMiddlewareManager()
        self.concurrent_domains = settings.getint('CONCURRENT_DOMAINS')

    def fetch(self, request, spider):
        """Main method to use to request a download

        This method includes middleware mangling. Middleware can returns a
        Response object, then request never reach downloader queue, and it will
        not be downloaded from site.
        """
        site = self.sites[spider]
        if site.closing:
            raise IgnoreRequest('Cannot fetch on a closing spider')

        site.active.add(request)
        def _deactivate(_):
            site.active.remove(request)
            self._close_if_idle(spider)
            return _

        dfd = self.middleware.download(self.enqueue, request, spider)
        return dfd.addBoth(_deactivate)

    def enqueue(self, request, spider):
        """Enqueue a Request for a effective download from site"""
        site = self.sites[spider]
        if site.closing:
            raise IgnoreRequest
        deferred = defer.Deferred()
        site.queue.append((request, deferred))
        self._process_queue(spider)
        return deferred

    def _process_queue(self, spider):
        """Effective download requests from site queue"""
        site = self.sites.get(spider)
        if not site:
            return

        # Delay queue processing if a download_delay is configured
        now = time()
        if site.download_delay:
            penalty = site.download_delay - now + site.lastseen
            if penalty > 0:
                reactor.callLater(penalty, self._process_queue, spider=spider)
                return
        site.lastseen = now

        # Process enqueued requests if there are free slots to transfer for this site
        while site.queue and site.free_transfer_slots() > 0:
            request, deferred = site.queue.pop(0)
            if site.closing:
                dfd = defer.fail(Failure(IgnoreRequest()))
            else:
                dfd = self._download(site, request, spider)
            dfd.chainDeferred(deferred)

        self._close_if_idle(spider)

    def _close_if_idle(self, spider):
        site = self.sites.get(spider)
        if site and site.closing and not site.active:
            del self.sites[spider]

    def _download(self, site, request, spider):
        # The order is very important for the following deferreds. Do not change!

        # 1. Create the download deferred
        dfd = mustbe_deferred(download_any, request, spider)

        # 2. After response arrives,  remove the request from transferring
        # state to free up the transferring slot so it can be used by the
        # following requests (perhaps those which came from the downloader
        # middleware itself)
        site.transferring.add(request)
        def finish_transferring(_):
            site.transferring.remove(request)
            self._process_queue(spider)
            # avoid partially downloaded responses from propagating to the
            # downloader middleware, to speed-up the closing process
            if site.closing:
                log.msg("Crawled while closing spider: %s" % request, \
                    level=log.DEBUG)
                raise IgnoreRequest
            return _
        return dfd.addBoth(finish_transferring)

    def open_spider(self, spider):
        """Allocate resources to begin processing a spider"""
        domain = spider.domain_name
        if spider in self.sites:
            raise RuntimeError('Downloader spider already opened: %s' % domain)

        self.sites[spider] = SiteInfo(
            download_delay=getattr(spider, 'download_delay', None),
            max_concurrent_requests=getattr(spider, 'max_concurrent_requests', None)
        )

    def close_spider(self, spider):
        """Free any resources associated with the given spider"""
        domain = spider.domain_name
        site = self.sites.get(spider)
        if not site or site.closing:
            raise RuntimeError('Downloader spider already closed: %s' % domain)

        site.closing = True
        self._process_queue(spider)

    def has_capacity(self):
        """Does the downloader have capacity to handle more spiders"""
        return len(self.sites) < self.concurrent_domains

    def is_idle(self):
        return not self.sites

