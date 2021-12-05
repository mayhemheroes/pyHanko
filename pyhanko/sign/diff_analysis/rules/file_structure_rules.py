from typing import Iterable, Tuple

from pyhanko.pdf_utils import generic
from pyhanko.pdf_utils.generic import Reference
from pyhanko.pdf_utils.reader import HistoricalResolver, RawPdfPath

from ..commons import compare_dicts
from ..constants import ROOT_EXEMPT_STRICT_COMPARISON
from ..policy_api import ModificationLevel
from ..rules_api import QualifiedWhitelistRule, ReferenceUpdate, WhitelistRule

__all__ = [
    'CatalogModificationRule', 'ObjectStreamRule',
    'XrefStreamRule'
]


class CatalogModificationRule(QualifiedWhitelistRule):
    """
    Rule that adjudicates modifications to the document catalog.

    :param ignored_keys:
        Values in the document catalog that may change between revisions.
        The default ones are ``/AcroForm``, ``/DSS``, ``/Extensions``,
        ``/Metadata``, ``/MarkInfo`` and ``/Version``.

        Checking for ``/AcroForm``, ``/DSS`` and ``/Metadata`` is delegated to
        :class:`.FormUpdatingRule`, :class:`.DSSCompareRule` and
        :class:`.MetadataUpdateRule`, respectively.
    """

    def __init__(self, ignored_keys=None):
        self.ignored_keys = (
            ignored_keys if ignored_keys is not None
            else ROOT_EXEMPT_STRICT_COMPARISON
        )

    def apply_qualified(self, old: HistoricalResolver,
                        new: HistoricalResolver) \
            -> Iterable[Tuple[ModificationLevel, Reference]]:

        old_root = old.root
        new_root = new.root
        # first, check if the keys in the document catalog are unchanged
        compare_dicts(old_root, new_root, self.ignored_keys)

        # As for the keys in the root dictionary that are allowed to change:
        #  - /Extensions requires no further processing since it must consist
        #    of direct objects anyway.
        #  - /MarkInfo: if it's an indirect reference (probably not) we can
        #    whitelist it if the key set makes sense. TODO do this
        #  - /DSS, /AcroForm and /Metadata are dealt with by other rules.
        yield ModificationLevel.LTA_UPDATES, ReferenceUpdate(
            new.root_ref, paths_checked=RawPdfPath('/Root'),
            # Things like /Data in a MDP policy can point to root
            # and since we checked with compare_dicts, doing a blanket
            # approval is much easier than figuring out all the ways
            # in which /Root can be cross-referenced.
            blanket_approve=True
        )


class ObjectStreamRule(WhitelistRule):
    """
    Rule that allows object streams to be added.

    Note that this rule only whitelists the object streams themselves (provided
    they do not override any existing objects, obviously), not the objects
    in them.
    """

    def apply(self, old: HistoricalResolver, new: HistoricalResolver) \
            -> Iterable[Reference]:
        # object streams are OK, but overriding object streams is not.
        for objstream_ref in new.object_streams_used():
            if old.is_ref_available(objstream_ref):
                yield ReferenceUpdate(objstream_ref)


class XrefStreamRule(WhitelistRule):
    """
    Rule that allows new cross-reference streams to be defined.
    """

    def apply(self, old: HistoricalResolver, new: HistoricalResolver) \
            -> Iterable[Reference]:
        xref_start, _ = new.reader.xrefs.get_xref_container_info(new.revision)
        if isinstance(xref_start, generic.Reference) \
                and old.is_ref_available(xref_start):
            yield ReferenceUpdate(xref_start)
