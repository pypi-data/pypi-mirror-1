# Copyright 2004-2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.batchnavigator
#
# lazr.batchnavigator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.batchnavigator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.batchnavigator. If not, see <http://www.gnu.org/licenses/>.

__metaclass__ = type

import urllib
import cgi

from zope.interface import implements, classProvides
from zope.cachedescriptors.property import Lazy

from lazr.batchnavigator.z3batching.batch import _Batch
from lazr.batchnavigator.interfaces import (
    IBatchNavigator, InvalidBatchSizeError, IBatchNavigatorFactory)

__all__ = ['BatchNavigator']

class BatchNavigator:

    # subclasses can override
    _batch_factory = _Batch

    implements(IBatchNavigator)
    classProvides(IBatchNavigatorFactory)

    start_variable_name = 'start'
    batch_variable_name = 'batch'

    default_batch_size = 50
    max_batch_size = 300

    # We want subclasses to be able to hide the 'Last' link from
    # users.  They may want to do this for really large result sets;
    # for example, batches with over a hundred thousand items.
    show_last_link = True

    # The default heading describing the kind of objects in the batch.
    # Sub-classes can override this to be more specific.
    default_singular_heading = 'result'
    default_plural_heading = 'results'

    transient_parameters = None

    @Lazy
    def query_string_parameters(self):
        query_string = self.request.get('QUERY_STRING', '')

        # Just in case QUERY_STRING is in the environment explicitly as
        # None (Some tests seem to do this, but not sure if it can ever
        # happen outside of tests.)
        if query_string is None:
            query_string = ''
        return cgi.parse_qs(query_string, keep_blank_values=True)

    def __init__(self, results, request, start=0, size=None, callback=None,
                 transient_parameters=None, force_start=False):
        "See `IBatchNavigatorFactory.__call__`"
        self.request = request
        local = (self.batch_variable_name, self.start_variable_name)
        self.transient_parameters = set(local)
        if transient_parameters is not None:
            self.transient_parameters.update(transient_parameters)

        # For backwards compatibility (as in the past a work-around has been
        # to include the url batch params in hidden fields within posted
        # forms), if the request is a POST request, and either the 'start'
        # or 'batch' params are included then revert to the default behaviour
        # of using the request (which automatically gets the params from the
        # request.form dict).
        if request.method == 'POST' and (
            self.start_variable_name in request.form or
            self.batch_variable_name in request.form):
            batch_params_source = request
        else:
            # We grab the request variables directly from the requests
            # query_string_parameters so that they will be recognized
            # even during post operations.
            batch_params_source = dict(
                (k, v[0]) for k, v
                in self.query_string_parameters.items() if k in local)

        # In this code we ignore invalid request variables since it
        # probably means the user finger-fumbled it in the request. We
        # could raise UnexpectedFormData, but is there a good reason?
        request_start = batch_params_source.get(
            self.start_variable_name, None)
        if force_start or request_start is None:
            self.start = start
        else:
            try:
                self.start = int(request_start)
            except (ValueError, TypeError):
                self.start = start

        self.default_size = size

        request_size = batch_params_source.get(self.batch_variable_name, None)
        if request_size:
            try:
                size = int(request_size)
            except (ValueError, TypeError):
                pass
            if size > self.max_batch_size:
                raise InvalidBatchSizeError(
                    'Maximum for "%s" parameter is %d.' %
                    (self.batch_variable_name,
                     self.max_batch_size))

        if size is None:
            size = self.default_batch_size

        self.batch = self._batch_factory(results, start=self.start, size=size)
        if callback is not None:
            callback(self, self.batch)
        self.setHeadings(
            self.default_singular_heading, self.default_plural_heading)

    @property
    def heading(self):
        """See `IBatchNavigator`"""
        if self.batch.total() == 1:
            return self._singular_heading
        return self._plural_heading

    def setHeadings(self, singular, plural):
        """See `IBatchNavigator`"""
        self._singular_heading = singular
        self._plural_heading = plural

    def getCleanQueryString(self, params=None):
        """Removes start and batch params if present and returns a query
        string.

        If ``params`` is None, uses the current query_string_params.
        """
        if params is None:
            params = []
            for k, v in self.query_string_parameters.items():
                params.extend((k, item) for item in v)
        else:
            try:
                params = params.items()
            except AttributeError:
                pass

        # We need the doseq=True because some url params are for multi-value
        # fields.
        return urllib.urlencode(
            [(key, value) for (key, value) in sorted(params)
             if key not in self.transient_parameters],
             doseq=True)

    def generateBatchURL(self, batch):
        url = ""
        if not batch:
            return url

        qs = self.getCleanQueryString()
        if qs:
            qs += "&"

        start = batch.startNumber() - 1
        size = batch.size
        base_url = str(self.request.URL)
        url = "%s?%s%s=%d" % (base_url, qs, self.start_variable_name, start)
        if size != self.default_size:
            # The current batch size should only be part of the URL if it's
            # different from the default batch size.
            url = "%s&%s=%d" % (url, self.batch_variable_name, size)
        return url

    def getBatches(self):
        batch = self.batch.firstBatch()
        batches = [batch]
        while 1:
            batch = batch.nextBatch()
            if not batch:
                break
            batches.append(batch)
        return batches

    def firstBatchURL(self):
        batch = self.batch.firstBatch()
        if self.start == 0:
            # We are already on the first batch.
            batch = None
        return self.generateBatchURL(batch)

    def prevBatchURL(self):
        return self.generateBatchURL(self.batch.prevBatch())

    def nextBatchURL(self):
        return self.generateBatchURL(self.batch.nextBatch())

    def lastBatchURL(self):
        batch = self.batch.lastBatch()
        if self.start == batch.start:
            # We are already on the last batch.
            batch = None
        return self.generateBatchURL(batch)

    def batchPageURLs(self):
        batches = self.getBatches()
        urls = []
        size = len(batches)

        nextb = self.batch.nextBatch()

        # Find the current page
        if nextb:
            current = nextb.start/nextb.size
        else:
            current = size

        self.current = current
        # Find the start page to show
        if (current - 5) > 0:
            start = current-5
        else:
            start = 0

        # Find the last page to show
        if (start + 10) < size:
            stop = start + 10
        else:
            stop = size

        initial = start
        while start < stop:
            this_batch = batches[start]
            url = self.generateBatchURL(this_batch)
            if (start+1) == current:
                urls.append({'['+str(start + 1)+']' : url})
            else:
                urls.append({start + 1 : url})
            start += 1

        if current != 1:
            url = self.generateBatchURL(batches[0])
            urls.insert(0, {'_first_' : url})
        if current != size:
            url = self.generateBatchURL(batches[size-1])
            urls.append({'_last_':url})

        return urls

    def currentBatch(self):
        return self.batch
