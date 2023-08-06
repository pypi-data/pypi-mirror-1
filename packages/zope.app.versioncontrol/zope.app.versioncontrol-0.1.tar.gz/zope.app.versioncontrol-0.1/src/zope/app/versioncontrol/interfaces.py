##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Version Control Interfaces

$Id: interfaces.py 82376 2007-12-20 21:27:45Z ccomb $
"""
import persistent.interfaces
import zope.interface
import zope.schema
import zope.component.interfaces
import zope.annotation.interfaces

from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope.app.versioncontrol')

class VersionControlError(Exception):
    pass


class IRepository(zope.interface.Interface):
    """Main API for version control operations.

    This interface hides most of the details of version data storage
    and retrieval.

    In Zope 3, the version control interface will probably be
    implemented by a version control utility. In the meantime, it may
    be implemented directly by repository implementations (or other
    things, like CMF tools).

    The goal of this version of the version control interface is to
    support simple linear versioning with support for labelled
    versions.  Future versions or extensions of this interface will
    likely support more advanced version control features such as
    concurrent lines of descent (activities) and collection
    versioning.
    """

    def isResourceUpToDate(object, require_branch=False):
        """
        Returns true if a resource is based on the latest version. Note
        that the latest version is in the context of any branch.

        If the require_branch flag is true, this method returns false if
        the resource is updated to a particular version, label, or date.
        Useful for determining whether a call to checkoutResource()
        will succeed.
        """

    def isResourceChanged(object):
        """
        Return true if the state of a resource has changed in a transaction
        *after* the version bookkeeping was saved. Note that this method is 
        not appropriate for detecting changes within a transaction!
        """

    def getVersionInfo(object):
        """
        Return the VersionInfo associated with the given object.

        The VersionInfo object contains version control bookkeeping
        information.  If the object is not under version control, a
        VersionControlError will be raised.
        """

    def applyVersionControl(object, message=None):
        """
        Place the given object under version control. A VersionControlError
        will be raised if the object is already under version control.

        After being placed under version control, the resource is logically
        in the 'checked-in' state.

        If no message is passed the 'Initial checkin.' message string is 
        written as the message log entry.
        """

    def checkoutResource(object):
        """
        Put the given version-controlled object into the 'checked-out'
        state, allowing changes to be made to the object. If the object is
        not under version control or the object is already checked out, a
        VersionControlError will be raised.
        """

    def checkinResource(object, message=''):
        """
        Check-in (create a new version) of the given object, updating the
        state and bookkeeping information of the given object. The optional
        message should describe the changes being committed. If the object
        is not under version control or is already in the checked-in state,
        a VersionControlError will be raised.
        """

    def uncheckoutResource(object):
        """
        Discard changes to the given object made since the last checkout.
        If the object is not under version control or is not checked out,
        a VersionControlError will be raised.
        """

    def updateResource(object, selector=None):
        """
        Update the state of the given object to that of a specific version
        of the object. The object must be in the checked-in state to be
        updated. The selector must be a string (version id, branch id,
        label or date) that is used to select a version from the version
        history.
        """

    def copyVersion(object, selector):
        """Copy data from an old version to a checked out object

        The object's data are updated and it remains checked out and
        modified.
        """

    def labelResource(object, label, force=None):
        """
        Associate the given resource with a label. If force is true, then
        any existing association with the given label will be removed and
        replaced with the new association. If force is false and there is
        an existing association with the given label, a VersionControlError
        will be raised.
        """

    def getVersionOfResource(history_id, selector):
        """
        Given a version history id and a version selector, return the
        object as of that version. Note that the returned object has no
        acquisition context. The selector must be a string (version id,
        branch id, label or date) that is used to select a version
        from the version history.
        """

    def getVersionIds(object):
        """
        Return a sequence of the (string) version ids corresponding to the
        available versions of an object. This should be used by UI elements
        to populate version selection widgets, etc.
        """

    def getLabelsForResource(object):
        """
        Return a sequence of the (string) labels corresponding to the
        versions of the given object that have been associated with a
        label. This should be used by UI elements to populate version
        selection widgets, etc.
        """

    def getLogEntries(object):
        """
        Return a sequence of LogEntry objects (most recent first) that
        are associated with a version-controlled object.
        """

    def makeBranch(object):
        """Create a new branch, returning the branch id.

        The branch is created from the object's version.

        A branch id is computed and returned.
        """

CHECKED_OUT = 0
CHECKED_IN = 1

class IVersionInfo(zope.interface.Interface):
    """Version control bookkeeping information."""

    # TODO: This *should* be a datetime, but we don't yet know how it's used.
    timestamp = zope.schema.Float(
        description=_("time value indicating"
                      " when the bookkeeping information was created"),
        required=False)

    # TODO: This *should* be an ASCIILine, but there isn't one (yet).
    history_id = zope.schema.ASCII(
        description=_("""
        Id of the version history related to the version controlled resource.

        If this isn't set (is None), 
        """),
        required=False)

    # TODO: This *should* be an ASCIILine, but there isn't one (yet).
    version_id = zope.schema.ASCII(
        description=_(
        "version id that the version controlled resource is based upon"))

    status = zope.schema.Choice(
        description=_("status of the version controlled resource"),
        vocabulary=SimpleVocabulary.fromItems([
            (_("Checked out"), CHECKED_OUT),
            (_("Checked in"), CHECKED_IN)]))

    sticky = zope.interface.Attribute(
        "tag information used internally by the version control implementation"
        )

    user_id = zope.schema.TextLine(
        description=_("id of the effective user at the time the bookkeeping"
                      " information was created"))


ACTION_CHECKOUT = 0
ACTION_CHECKIN = 1
ACTION_UNCHECKOUT = 2
ACTION_UPDATE = 3

class ILogEntry(zope.interface.Interface):
    """The ILogEntry interface provides access to the information in an
    audit log entry."""

    timestamp = zope.schema.Float(
        description=_("time that the log entry was created"))

    version_id = zope.schema.ASCII(
        description=_("version id of the resource related to the log entry"))

    action = zope.schema.Choice(
        description=_("the action that was taken"),
        vocabulary=SimpleVocabulary.fromItems(
        [(_("Checkout"), ACTION_CHECKOUT),
         (_("Checkin"), ACTION_CHECKIN),
         (_("Uncheckout"), ACTION_UNCHECKOUT),
         (_("Update"), ACTION_UPDATE)]))

    message = zope.schema.Text(
        description=_("Message provided by the user at the time of the"
                      " action.  This may be empty."))

    user_id = zope.schema.TextLine(
        description=_("id of the user causing the audited action"))

    path = zope.schema.TextLine(
        description=_("path to the object upon which the action was taken"))


class INonVersionedData(zope.interface.Interface):
    """Controls what parts of an object fall outside version control.

    Containerish objects implement this interface to allow the items they
    contain to be versioned independently of the container.
    """

    def listNonVersionedObjects():
        """Returns a list of subobjects that should not be pickled.

        The objects in the list must not be wrapped, because only the
        identity of the objects will be considered.  The version
        repository uses this method to avoid cloning subobjects that
        will soon be removed by removeNonVersionedData.
        """

    def removeNonVersionedData():
        """Removes the non-versioned data from this object.

        The version repository uses this method before storing an
        object in the version repository.
        """

    def getNonVersionedData():
        """Returns an opaque object containing the non-versioned data.

        The version repository uses this method before reverting an
        object to a revision.
        """

    def restoreNonVersionedData(data):
        """Restores non-versioned data to this object.

        The version repository uses this method after reverting an
        object to a revision.  `data` is a value provided by the
        `getNonVersionedData()` method of this instance.

        ??? question:
        This should not overwrite data that exists in the object but
        that is included in the passed-in data.  

        """

# TODO: figure out if we can get rid of this
IVersionedContainer = INonVersionedData



class IVersionable(persistent.interfaces.IPersistent,
                   zope.annotation.interfaces.IAnnotatable):
    """Version control is allowed for objects that provide this."""

class IVersioned(IVersionable):
    """Version control is in effect for this object."""

class ICheckedIn(IVersioned):
    """Object that has been checked in.

    Changes should not be allowed.

    An object may be ICheckedIn or ICheckedOut, but not both,
    """

class ICheckedOut(IVersioned):
    """Object that has been checked out.

    Changes should be allowed.

    An object may be ICheckedIn or ICheckedOut, but not both,
    """

# Events that are raised for interesting occurances:

class IVersionEvent(zope.component.interfaces.IObjectEvent):
    """Base interface for all version-control events."""

    info = zope.interface.Attribute("Version info (IVersionInfo)")

class IVersionControlApplied(IVersionEvent):
    """Event fired when version control is initially applied to an object."""

    message = zope.schema.Text(
        title=_("Message"),
        description=_("Message text passed to applyVersionControl()"
                      " for the object."),
        )

    info = zope.interface.Attribute(
        "VersionInfo object reflecting the action.")


class IVersionCheckedIn(IVersionEvent):
    """Event fired when an object is checked in."""

    message = zope.schema.Text(
        title=_("Checkin Message"),
        )

class IVersionCheckedOut(IVersionEvent):
    """Event fired when an object is checked out."""


class IVersionReverted(IVersionEvent):
    """Event fired when a checked-out object is reverted.

    (Fired by the uncheckoutResource() repository method.)
    """


class IVersionUpdated(IVersionEvent):
    """Event fired when an object is updated to the latest version."""


class IVersionRetrieved(IVersionEvent):
    """Event fired when a versioned object is retrieved from the repository."""


class IVersionLabelled(IVersionEvent):
    """Event fired when a label is attached to a version."""

    # TODO: should be ASCIILine
    label = zope.schema.ASCII(
        title=_("Label"),
        description=_("Label applied to the version."),
        )


class IBranchCreated(IVersionEvent):
    """Event fired when a new branch is created."""

    # TODO: should be ASCIILine
    branch_id = zope.schema.ASCII(
        title=_("Branch Id"),
        description=_("Identifier for the new branch."),
        )
