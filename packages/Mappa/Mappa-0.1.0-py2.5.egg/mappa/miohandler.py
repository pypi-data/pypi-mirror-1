# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 - 2009 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the name 'Semagia' nor the name 'Mappa' nor the names of the
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
``tm.mio.handler.MapHandler`` implementation for Mappa.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - <http://www.semagia.com/>
:version:      $Rev: 164 $ - $Date: 2009-06-26 00:59:52 +0200 (Fr, 26 Jun 2009) $
:license:      BSD License
"""
from tm import mio, UCS, TMDM
import tm.mio.handler as mio_handler
try:
    set
except NameError:
    from sets import Set as set # pylint: disable-msg=W0622

__all__ = ['MappaMapHandler']

# States
_TOPIC_MAP = 1
_TOPIC = 2
_ASSOCIATION = 3
_ROLE = 4
_OCCURRENCE = 5
_NAME = 6
_VARIANT = 7
_TYPE = 8
_SCOPE = 9
_THEME = 10
_PLAYER = 11
_REIFIER = 12
_ISA = 13

class _Construct(object):
    """\
    A universal Topic Maps construct which is used to keep track about
    several properties.
    """
    __slots__ = ['type', 'player', 'scope', 'types', 'roles', 
                 'variants', 'reifier', 'iids', 'value']
    def __init__(self):
        self.type = None
        self.player = None
        self.scope = UCS
        self.types = []
        self.roles = []
        self.variants = []
        self.reifier = []
        self.iids = []
        self.value = None

    def add_iid(self, iid):
        """\
        Adds the item identifier ``iid`` to this construct.
        """
        self.iids.append(iid)

    def add_theme(self, theme):
        """\
        Adds the ``theme`` to the scope.
        """
        if self.scope is UCS:
            self.scope = set()
        self.scope.add(theme)


class MappaMapHandler(mio_handler.MapHandler):
    """\
    ``MapHandler`` implementation for Mappa.
    """
    __slots__ = ['_tm', '_states', '_constructs']

    # Default name type
    _TOPIC_NAME = mio.SUBJECT_IDENTIFIER, TMDM.topic_name

    def __init__(self, tm):
        """\
        Initializes the handler with the given topic map.
        
        `tm`
            The topic map to operate upon.
        """
        super(MappaMapHandler, self).__init__()
        self._tm = tm
        self._states = []
        self._constructs = []

    def startTopicMap(self):
        self._states = [_TOPIC_MAP]
        self._constructs = [self._tm]

    def endTopicMap(self):
        self._states = None
        self._constructs = None
        self._tm = None

    def startTopic(self, identity):
        self._states.append(_TOPIC)
        self._constructs.append(self._create_topic(identity))

    def endTopic(self):
        if _TOPIC is not self._states.pop():
            raise mio.MIOException('Unexpected "endTopic" event')
        self._handle_topic(self._constructs.pop())

    def topicRef(self, identity):
        self._handle_topic(self._create_topic(identity))

    def subjectIdentifier(self, sid):
        if _TOPIC is not self._states[-1]:
            raise mio.MIOException('Unexpected "subjectIdentifier" event, not in a topic')
        topic = self._constructs[-1]
        existing = self._tm.topic_by_sid(sid) or self._tm.topic_by_iid(sid)
        if existing and existing != topic:
            self._merge(topic, existing)
            topic = existing
        topic.add_sid(sid)

    def subjectLocator(self, slo):
        if _TOPIC is not self._states[-1]:
            raise mio.MIOException('Unexpected "subjectLocator" event, not in a topic')
        topic = self._constructs[-1]
        existing = self._tm.topic_by_slo(slo)
        if existing and existing != topic:
            self._merge(topic, existing)
            topic = existing
        topic.add_slo(slo)

    def itemIdentifier(self, iid):
        tmc = self._constructs[-1]
        if self._states[-1] is _TOPIC:
            existing = self._tm.topic_by_iid(iid) or self._tm.topic_by_sid(iid)
            if existing and existing != tmc:
                self._merge(tmc, existing)
                tmc = existing
        tmc.add_iid(iid)

    def startReifier(self):
        self._states.append(_REIFIER)

    def endReifier(self):
        if _REIFIER is not self._states.pop():
            raise mio.MIOException('Unexpected "endReifier" event')

    def startAssociation(self):
        self._states.append(_ASSOCIATION)
        self._constructs.append(_Construct())

    def endAssociation(self):
        if _ASSOCIATION is not self._states.pop():
            raise mio.MIOException('Unexpected "endAssociation" event')
        c = self._constructs.pop()
        if not c.roles:
            raise mio.MIOException('The association has no roles')
        apply_iids = self._apply_iids
        assoc = self._tm.create_association(c.type, c.scope)
        apply_iids(assoc, c.iids)
        assoc.reifier = c.reifier
        for r in c.roles:
            role = assoc.create_role(r.type, r.player)
            apply_iids(role, r.iids)
            role.reifier = r.reifier

    def startRole(self):
        if _ASSOCIATION is not self._states[-1]:
            raise mio.MIOException('Unexpected "startRole" event, not in an association')
        self._states.append(_ROLE)
        self._constructs.append(_Construct())

    def endRole(self):
        if _ROLE is not self._states.pop():
            raise mio.MIOException('Unexpected "endRole" event')
        role = self._constructs.pop()
        self._constructs[-1].roles.append(role)

    def startOccurrence(self):
        if _TOPIC is not self._states[-1]:
            raise mio.MIOException('Unexpected "startOccurrence" event, not in a topic')
        self._states.append(_OCCURRENCE)
        self._constructs.append(_Construct())

    def endOccurrence(self):
        if _OCCURRENCE is not self._states.pop():
            raise mio.MIOException('Unexpected "endOccurrence" event')
        c = self._constructs.pop()
        occ = self._constructs[-1].create_occurrence(c.type, c.value, c.scope)
        self._apply_iids(occ, c.iids)
        occ.reifier = c.reifier

    def startName(self):
        if _TOPIC is not self._states[-1]:
            raise mio.MIOException('Unexpected "startName" event, not in a topic')
        self._states.append(_NAME)
        self._constructs.append(_Construct())

    def endName(self):
        if _NAME is not self._states.pop():
            raise mio.MIOException('Unexpected "endName" event')
        c = self._constructs.pop()
        apply_iids = self._apply_iids
        typ = c.type or self._create_topic(MappaMapHandler._TOPIC_NAME)
        name = self._constructs[-1].create_name(type=typ, value=c.value, scope=c.scope)
        apply_iids(name, c.iids)
        name.reifier = c.reifier
        create_variant = name.create_variant
        for v in c.variants:
            var = create_variant(v.value, v.scope)
            apply_iids(var, v.iids)
            var.reifier = v.reifier

    def startVariant(self):
        if _NAME is not self._states[-1]:
            raise mio.MIOException('Unexpected "startVariant" event, not in a name')
        self._states.append(_VARIANT)
        self._constructs.append(_Construct())

    def endVariant(self):
        if _VARIANT is not self._states.pop():
            raise mio.MIOException('Unexpected "endVariant" event')
        var = self._constructs.pop()
        if not var.scope:
            raise mio.MIOException('Invalid variant, no scope was defined')
        name = self._constructs[-1]
        if var.scope == name.scope:
            raise mio.MIOException('Invalid variant, the scope is not a superset of the name scope')
        name.variants.append(var)

    def value(self, value, datatype=None):
        tmc = self._constructs[-1]
        if datatype is None:
            if _NAME is not self._states[-1]:
                raise mio.MIOException('Unexpected "value" event. No datatype given, but not in a name')
            tmc.value = value
        else:
            if self._states[-1] not in (_OCCURRENCE, _VARIANT):
                raise mio.MIOException('Unexpected "value" event. Datatype given, but not in an occurrence or variant')
            tmc.value = value, datatype

    def startIsa(self):
        if _TOPIC is not self._states[-1]:
            raise mio.MIOException('Unexpected "startIsa" event, not in a topic')
        self._states.append(_ISA)

    def endIsa(self):
        if _ISA is not self._states.pop():
            raise mio.MIOException('Unexpected "endIsa" event')

    def startType(self):
        if self._states[-1] not in (_ASSOCIATION, _ROLE, _OCCURRENCE, _NAME):
            raise mio.MIOException('Unexpected "startType" event; not in an association, role, occurrence, or name')
        self._states.append(_TYPE)

    def endType(self):
        if _TYPE is not self._states.pop():
            raise mio.MIOException('Unexpected "endType" event')

    def startPlayer(self):
        if _ROLE is not self._states[-1]:
            raise mio.MIOException('Unexpected "startPlayer" event, not in a role')
        self._states.append(_PLAYER)

    def endPlayer(self):
        if _PLAYER is not self._states.pop():
            raise mio.MIOException('Unexpected "endPlayer" event')

    def startScope(self):
        if self._states[-1] not in (_ASSOCIATION, _OCCURRENCE, _NAME, _VARIANT):
            raise mio.MIOException('Unexpected "startScope" event; not in an association, occurrence, name, or variant')
        self._states.append(_SCOPE)

    def endScope(self):
        if _SCOPE is not self._states.pop():
            raise mio.MIOException('Unexpected "endScope" event')

    def startTheme(self):
        if _SCOPE is not self._states[-1]:
            raise mio.MIOException('Unexpected "startTheme" event, not in scope')
        self._states.append(_THEME)

    def endTheme(self):
        if _THEME is not self._states.pop():
            raise mio.MIOException('Unexpected "endTheme" event')

    def _apply_iids(self, construct, iids):
        """\
        Adds the item identifiers ``iids`` to the specified ``construct``.
        """
        for iid in iids:
            construct.add_iid(iid)

    def _handle_topic(self, topic):
        """\
        Handles the ``topic`` context-sensitivily.
        """
        state = self._states[-1]
        tmc = self._constructs[-1]
        if _TYPE is state:
            tmc.type = topic
        elif _PLAYER is state:
            tmc.player = topic
        elif _ISA is state:
            tmc.add_type(topic)
        elif _THEME is state:
            tmc.add_theme(topic)
        elif _REIFIER is state:
            tmc.reifier = topic

    def _create_topic(self, (kind, iri)):
        """\
        Returns a topic by the specified identity.
        """
        if mio.SUBJECT_IDENTIFIER is kind:
            return self._tm.create_topic_by_sid(iri)
        elif mio.ITEM_IDENTIFIER is kind:
            return self._tm.create_topic_by_iid(iri)
        elif mio.SUBJECT_LOCATOR is kind:
            return self._tm.create_topic_by_slo(iri)
        raise mio.MIOException('Unknown identity type "%s"' % kind)

    def _merge(self, source, target):
        """\
        Merges the ``source`` topic with the ``target`` topic.
        """
        while source in self._constructs:
            self._constructs[self._constructs.index(source)] = target
        target.merge(source)
