# -*- coding: utf-8 -*-
"""
<+ MODULE_NAME +>

Licensed under the <+ LICENSE +> license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Five import BrowserView
from pyamf import amf0
#from sqlalchemy import *


def as_recordset(result):
    results = []
    for i in result.fetchall():
        res = {}
        for j in range(len(i)):
            res[result.keys[j]] = i[j]
            results.append(res)
    return amf0.RecordSet(result._ResultProxy__keys, results)


class TestFlashView(BrowserView):

    def getGitesOfTheDay(self):
        self.engine = create_engine('postgres://%s:%s@localhost:5432/%s' % ('jfroche',
                                                              'xMLMY4',
                                                              'arsia'))
        metadata = MetaData(self.engine)

        def getAidOssature(metadata):
            autoload = True
            return Table('aidossature', metadata,
                Column(u'ossature', Integer(), primary_key=True),
                Column(u'libossature', Text()),
                Column(u'libossature_al', Text()),
                useexisting=True,
                autoload=autoload)

        ossature = getAidOssature(metadata)
        self.db = self.engine.connect()
        result = self.engine.execute(select([ossature]))
        return as_recordset(result)
