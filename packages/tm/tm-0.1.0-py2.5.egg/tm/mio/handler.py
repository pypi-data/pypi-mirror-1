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
#     * Neither the name of the project nor the names of the contributors 
#       may be used to endorse or promote products derived from this 
#       software without specific prior written permission.
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
The PyTM MIO package.

This is more or less a straight port of the Java MIO package to Python.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 167 $ - $Date: 2009-06-26 14:13:53 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
from tm import mio, TMDM

class MapHandler(object):
    """\
    Handler which receives notifications about Topic Maps constructs.
    """
    __slots__ = []
    def startTopicMap(self):
        """\
        Notification about the beginning of a topic map.
        
        This method is only called once.

        This method MUST NOT be called if a parser acts as subparser (i.e. if
        another serialized topic map is included into the current topic map via
        a mergemap directive or include directive). 
        """

    def endTopicMap(self):
        """\
        Notification about the end of a topic map.
        
        This method is only called once.
        This method MUST be called by the parser even if it detects an 
        irrevocable error during processing a topic map.
        
        This method MUST NOT be called if a parser acts as subparser (i.e. if
        another serialized topic map is included into the current topic map via
        a mergemap directive or include directive). 
        """

    def startTopic(self, identity):
        """\
        Notification about the start of a topic.
        
        `identity`
            A tuple consisting of an identifier kind constant and an IRI.
        """

    def endTopic(self):
        """\
        Notification about the end of a topic declaration.
        """

    def topicRef(self, identity):
        """\
        Notification about a topic reference.
        
        The interpretation of the topic reference depends on the context (i.e.
        after a `startType`, `startPlayer`, or a `startTheme` event).
        
        `identity`
            A tuple consisting of an identifier kind constant and an IRI.
        """

    def subjectIdentifier(self, iri):
        """\
        Reports a subject identifier.
        
        The subject identifier is an absolute IRI which should be added to the
        currently processed topic.
        
        `iri`
            A string representing an absolute IRI.
        """

    def subjectLocator(self, iri):
        """\
        Reports a subject locator.
        
        The subject locator is an absolute IRI which should be added to the
        currently processed topic.
        
        `iri`
            A string representing an absolute IRI.
        """

    def itemIdentifier(self, iri):
        """\
        Reports an item identifier.
        
        The item identifier is an absolute IRI which should be added to the
        currently processed Topic Maps construct.
        
        `iri`
            A string representing an absolute IRI.
        """

    def startAssociation(self):
        """\
        Notification about the start of an association.
        """

    def endAssociation(self):
        """\
        Notification about the end of an association.
        """

    def startRole(self):
        """\
        Notification about the start of a role.
        """

    def endRole(self):
        """\
        Notification about the end of a role.
        """

    def startOccurrence(self):
        """\
        Notification about the start of an occurrence.
        """

    def endOccurrence(self):
        """\
        Notification about the end of an occurrence.
        """

    def startName(self):
        """\
        Notification about the start of a name.
        """

    def endName(self):
        """\
        Notification about the end of a name.
        
        If there was no ``startType`` .. ``endType`` event, the implementation
        MUST assume that the name has the default name type.
        """

    def startVariant(self):
        """\
        Notification about the start of a variant.
        
        The parser guarantees that the scope of the name has been parsed.
        The scope of the name is not part of the scope of the variant.
        """

    def endVariant(self):
        """\
        Notification about the end of a variant.
        
        If the scope of the variant is not the superset of the name to which
        the variant belongs, this method MUST throw a ``MIOException``.
        """

    def startScope(self):
        """\
        Notification about the start of scope processing.
        
        This method is either called once for a scoped construct or never.
        """

    def endScope(self):
        """\
        Notification about the end of scope processing.
        """

    def startTheme(self):
        """\
        Notification about the start of a theme declaration.
        """

    def endTheme(self):
        """\
        Notification about the end of a theme declaration.
        """

    def startType(self):
        """\
        Notification about the start of a type declaration.
        """

    def endType(self):
        """\
        Notification about the end of a type declaration.
        """

    def startPlayer(self):
        """\
        Notification about the start of a player declaration.
        """

    def endPlayer(self):
        """\
        Notification about the end of a player declaration.
        """

    def startReifier(self):
        """\
        Notification about the start of a reifier declaration.
        """

    def endReifier(self):
        """\
        Notification about the end of a reifier declaration.
        """

    def startIsa(self):
        """\
        Notification about the the start of ``type-instance`` relationships.
        
        After this event there may occurr at minimum one `topicRef` 
        or one `startTopic` (with the correspondending `endTopic`
        event.
        
        The reported topics after a `startIsa` event are meant as
        type of the currently parsed topic.
        
        Outside of a topic context, this notification is illegal.
        """

    def endIsa(self):
        """\
        Notification about the end of the ``type-instance`` relationships.
        """

    def value(self, string, datatype=None):
        """\
        Reports either a value for an occurrence, a name or a variant.
        
        If a value for a name is reported, the `datatype` MUST be ``None``.
        
        `string`
            The value.
        `datatype`
            The datatype IRI or ``None`` if a name value is reported.
        """

class DelegatingMapHandler(MapHandler):
    """\
    A ``MapHandler`` implementation that does nothing but delegates all events 
    to an underlying ``MapHandler`` instance.
    """
    __slots__ = ['_handler']
    
    def __init__(self, handler):
        super(DelegatingMapHandler, self).__init__()
        self._handler = handler

    def startTopicMap(self):
        self._handler.startTopicMap()

    def endTopicMap(self):
        self._handler.endTopicMap()

    def startTopic(self, identity):
        self._handler.startTopic(identity)

    def endTopic(self):
        self._handler.endTopic()

    def topicRef(self, identity):
        self._handler.topicRef(identity)

    def subjectIdentifier(self, iri):
        self._handler.subjectIdentifier(iri)

    def subjectLocator(self, iri):
        self._handler.subjectLocator(iri)

    def itemIdentifier(self, iri):
        self._handler.itemIdentifier(iri)

    def startAssociation(self):
        self._handler.startAssociation()

    def endAssociation(self):
        self._handler.endAssociation()

    def startRole(self):
        self._handler.startRole()

    def endRole(self):
        self._handler.endRole()

    def startOccurrence(self):
        self._handler.startOccurrence()

    def endOccurrence(self):
        self._handler.endOccurrence()

    def startName(self):
        self._handler.startName()

    def endName(self):
        self._handler.endName()

    def startVariant(self):
        self._handler.startVariant()

    def endVariant(self):
        self._handler.endVariant()

    def startScope(self):
        self._handler.startScope()

    def endScope(self):
        self._handler.endScope()

    def startTheme(self):
        self._handler.startTheme()

    def endTheme(self):
        self._handler.endTheme()

    def startType(self):
        self._handler.startType()

    def endType(self):
        self._handler.endType()

    def startPlayer(self):
        self._handler.startPlayer()

    def endPlayer(self):
        self._handler.endPlayer()

    def startReifier(self):
        self._handler.startReifier()

    def endReifier(self):
        self._handler.endReifier()

    def startIsa(self):
        self._handler.startIsa()

    def endIsa(self):
        self._handler.endIsa()

    def value(self, val, datatype=None):
        self._handler.value(val, datatype)

#pylint: disable-msg=W0622,W0221
class SimpleMapHandler(DelegatingMapHandler):
    """\
    A ``MapHandler`` implementation that adds some methods which cover common
    use cases.
    
    This class may be used to wrap an ordinary ``MapHandler`` implementation.
    """
    __slots__ = []
    _SUPERTYPE_SUBTYPE = mio.SUBJECT_IDENTIFIER, TMDM.supertype_subtype
    _SUPERTYPE = mio.SUBJECT_IDENTIFIER, TMDM.supertype
    _SUBTYPE = mio.SUBJECT_IDENTIFIER, TMDM.subtype
    
    def __init__(self, handler):
        super(SimpleMapHandler, self).__init__(handler)

    def topic(self, identity):
        """\
        Generates a `startTopic` and a `endTopic` event.
        """
        self.startTopic(identity)
        self.endTopic()

    def isa(self, identity):
        """\
        Generates a `startIsa`, `topicRef` and a `endIsa` event.
        """
        self.startIsa()
        self.topicRef(identity)
        self.endIsa()

    def ako(self, subtype, supertype):
        """\
        Generates a supertype-subtype association.
        """
        self.startAssociation(SimpleMapHandler._SUPERTYPE_SUBTYPE)
        self.startRole(SimpleMapHandler._SUBTYPE)
        self.player(subtype)
        self.endRole()
        self.startRole(SimpleMapHandler._SUPERTYPE)
        self.player(supertype)
        self.endRole()
        self.endAssociation()

    def type(self, identity):
        """\
        Generates a `startType`, `topicRef` and `endType` event.
        """
        self.startType()
        self.topicRef(identity)
        self.endType()

    def theme(self, identity):
        """\
        Generates a `startTheme`, `topicRef` and `endTheme` event.
        """
        self.startTheme()
        self.topicRef(identity)
        self.endTheme()

    def player(self, identity):
        """\
        Generates a `startPlayer`, `topicRef` and `endPlayer` event.
        """
        self.startPlayer()
        self.topicRef(identity)
        self.endPlayer()

    def reifier(self, identity):
        """\
        Generates a `startReifier`, `topicRef` and `endReifier` event 
        iff `identity` is provided.
        """
        if identity:
            self.startReifier()
            self.topicRef(identity)
            self.endReifier()

    def startAssociation(self, type=None):
        """\
        Generates a `startAssociation` and iff the `type` is specified, a `startType`,
        `topicRef`, and `endType` event.
        """
        super(SimpleMapHandler, self).startAssociation()
        if type is not None:
            self.type(type)

    def startRole(self, type=None):
        """\
        Generates a `startRole` and iff the `type` is specified, a `startType`,
        `topicRef`, and `endType` event.
        """
        super(SimpleMapHandler, self).startRole()
        if type is not None:
            self.type(type)

    def startOccurrence(self, type=None):
        """\
        Generates a `startOccurrence` and iff the `type` is specified, a `startType`,
        `topicRef`, and `endType` event.
        """
        super(SimpleMapHandler, self).startOccurrence()
        if type is not None:
            self.type(type)

    def startName(self, type=None):
        """\
        Generates a `startName` and iff the `type` is specified, a `startType`,
        `topicRef`, and `endType` event.
        """
        super(SimpleMapHandler, self).startName()
        if type is not None:
            self.type(type)

del TMDM

def simplify(handler):
    """\
    Returns a `SimpleMapHandler` which wraps the specified `handler` iff
    it is not already a `SimpleMapHandler`
    """
    if isinstance(handler, SimpleMapHandler):
        return handler
    return SimpleMapHandler(handler)

_java_compatible = False

#pylint: disable-msg=F0401
import sys
if sys.platform[:4] == 'java':
    _java_compatible = True
    try:
        import com.semagia.mio as jmio
        import com.semagia.mio.helpers as jmio_helpers
    except ImportError:
        _java_compatible = False
del sys

if _java_compatible:
    class MIOHandlerToJava(SimpleMapHandler):
        """\
        A ``MapHandler`` implementation that delegates all Python MIO events to
        a Java implementation of ``com.semagia.mio.IMapHandler``.
        
        All ``SimpleMapHandler`` methods are available as well.
        """
        __slots__ = []
        def __init__(self, handler):
            super(MIOHandlerToJava, self).__init__(handler)

        def startTopic(self, identity):
            super(MIOHandlerToJava, self).startTopic(_create_ref(identity))

        def topicRef(self, identity):
            super(MIOHandlerToJava, self).topicRef(_create_ref(identity))

        def value(self, value, datatype=None):
            # Necessary to let Jython decide which method should be called.
            if datatype is None:
                self._handler.value(value)
            else:
                self._handler.value(value, datatype)

    def _create_ref((kind, iri)):
        """\
        Returns a IRef implementation from the specified ``(kind, iri)`` tuple.
        """
        if mio.ITEM_IDENTIFIER is kind:
            return jmio_helpers.Ref.createItemIdentifier(iri)
        elif mio.SUBJECT_IDENTIFIER is kind:
            return jmio_helpers.Ref.createSubjectIdentifier(iri)
        elif mio.SUBJECT_LOCATOR is kind:
            return jmio_helpers.Ref.createSubjectLocator(iri)
        raise jmio.MIOException('Unknown identity kind "%s"' % kind)


    class MIOHandlerFromJava(jmio.IMapHandler, DelegatingMapHandler):
        """\
        Implements the ``com.semagia.mio.IMapHandler`` interface and 
        translates the events to the Python equivalent. 
        """
        def startTopic(self, ref):
            self._handler.startTopic(_create_identity(ref))

        def topicRef(self, ref):
            self._handler.topicRef(_create_identity(ref))

    def _create_identity(ref):
        """\
        Returns a identity tuple ``(kind, iri)`` from the specified Java mio.IRef.
        """
        kind, iri = ref.getType(), ref.getIRI()
        if jmio.IRef.ITEM_IDENTIFIER == kind:
            return mio.ITEM_IDENTIFIER, iri
        elif jmio.IRef.SUBJECT_IDENTIFIER == kind:
            return mio.SUBJECT_IDENTIFIER, iri
        elif jmio.IRef.SUBJECT_LOCATOR == kind:
            return mio.SUBJECT_LOCATOR, iri
        raise jmio.MIOException('Unknown reference type "%s"' % kind)
