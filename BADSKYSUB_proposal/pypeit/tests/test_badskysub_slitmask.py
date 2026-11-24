# VERSION HISTORY
# --------------------------------
# v3.1 + Noah Bensoussan, 17/11/2026
# - NEW: Verify opt-in extraction slitmask selection includes eligible
#   BADSKYSUB slits while preserving other blocking-flag exclusions.

from types import SimpleNamespace

import numpy as np

from pypeit.extraction import Extract
from pypeit.slittrace import SlitTraceBitMask


class _Slits:
    def __init__(self, mask, bitmask):
        self.mask = mask
        self.bitmask = bitmask
        self.spat_id = np.array([137, 300, 555])
        self.slit_img_args = None

    def select_edges(self, initial=False, flexure=None):
        return np.zeros((2, 3)), np.ones((2, 3)), None

    def slit_img(self, initial=False, flexure=None, slitidx=None, exclude_flag=None):
        self.slit_img_args = {
            'initial': initial,
            'flexure': flexure,
            'slitidx': slitidx,
            'exclude_flag': exclude_flag
        }
        slitmask = np.full((2, 3), -1, dtype=int)
        if slitidx is not None:
            for idx in slitidx:
                slitmask[:, idx] = self.spat_id[idx]
        return slitmask


def _extract_eligibility(mask, bitmask, allow_badskysub):
    extraction_mask = mask.copy()
    if allow_badskysub:
        extraction_mask = bitmask.turn_off(extraction_mask, 'BADSKYSUB')
    return bitmask.flagged(
        extraction_mask, and_not=bitmask.exclude_for_reducing)


def test_opted_in_slitmask_uses_extract_eligible_slit_indices():
    bitmask = SlitTraceBitMask()
    mask = np.zeros(3, dtype=np.int64)
    mask[0] = bitmask.turn_on(mask[0], 'BADSKYSUB')
    mask[1] = bitmask.turn_on(mask[1], ['BADSKYSUB', 'BADWVCALIB'])
    mask[2] = bitmask.turn_on(mask[2], 'SKIPFLATCALIB')
    extract_bpm = _extract_eligibility(mask, bitmask, allow_badskysub=True)
    assert extract_bpm.tolist() == [False, True, False]

    slits = _Slits(mask, bitmask)
    extractor = SimpleNamespace(
        sciImg=SimpleNamespace(update_mask_slitmask=lambda slitmask: None),
        spat_flexure_shift=None,
        extract_badskysub=True,
        extract_bpm=extract_bpm)

    Extract.initialize_slits(extractor, slits)

    assert slits.slit_img_args['slitidx'].tolist() == [0, 2]
    assert slits.slit_img_args['exclude_flag'] is None
    assert 137 in np.unique(extractor.slitmask)
    assert 300 not in np.unique(extractor.slitmask)


def test_disabled_option_keeps_existing_slitmask_selection():
    bitmask = SlitTraceBitMask()
    mask = np.zeros(1, dtype=np.int64)
    slits = _Slits(mask, bitmask)
    extractor = SimpleNamespace(
        sciImg=SimpleNamespace(update_mask_slitmask=lambda slitmask: None),
        spat_flexure_shift=None,
        extract_badskysub=False,
        extract_bpm=np.array([False]))

    Extract.initialize_slits(extractor, slits)

    assert slits.slit_img_args['slitidx'] is None
    assert slits.slit_img_args['exclude_flag'] == bitmask.exclude_for_reducing
