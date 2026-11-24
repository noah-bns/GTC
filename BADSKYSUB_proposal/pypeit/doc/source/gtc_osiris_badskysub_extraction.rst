BADSKYSUB boxcar extraction for GTC/OSIRIS
=========================================

.. VERSION HISTORY
   --------------------------------
   v3.1 + Noah Bensoussan, 17/11/2026
   - CLARIFICATION: Object finding precedes BADSKYSUB flagging in the normal
     reduction flow; the proposal only extracts objects already found.
   - CHANGE: Documented the extraction-time slitmask inclusion needed for
     opted-in BADSKYSUB slits, without relaxing other blocking flags.

PypeIt normally excludes a slit flagged ``BADSKYSUB`` from extraction. The
``extract_badskysub`` option is an opt-in exception for
``gtc_osiris_plus``. It defaults to ``False``, so existing reductions retain
their current behavior unless the option is enabled in the PypeIt file.

When enabled, a slit flagged ``BADSKYSUB`` is extracted with a boxcar aperture
directly from the processed science image. Neither the global nor local sky
model is subtracted for that slit. Only ``BADSKYSUB`` is removed from the
extraction eligibility check; other slit flags retain their existing PypeIt
behavior. The original ``BADSKYSUB`` flag remains in the 2D product for later
inspection. The reduction log also warns when this path is used.

Flexure behavior
----------------

The opt-in extraction exception does not make a ``BADSKYSUB`` slit eligible
for PypeIt's spectral-flexure measurement. The proposal keeps these slits in
the flexure mask, so they are excluded from both the global sky-line flexure
measurement and the per-object local spectral-flexure correction. Their
extraction therefore uses no slit-specific spectral-flexure shift measured
by those steps; the wavelength solution can retain a residual wavelength
offset.

This does not disable all flexure-related handling. Spatial flexure correction
and the later wavelength reference-frame correction (when configured) remain
separate steps and are not disabled by this option.

Object-finding behavior
-----------------------

The normal reduction order runs object finding before the final global sky
subtraction. The ``BADSKYSUB`` flag is applied after that sky-subtraction
attempt, so this proposal does not change object-finding thresholds or create
replacement objects. Extraction only considers ``SpecObj`` entries that
object finding already returned. If no object was found on a flagged slit,
there is no spectrum to extract from that slit.

In one diagnostic run, the local loop reached ``slit_spat = 137`` after its
check for a matching object, but 137 was absent from ``np.unique(self.slitmask)``.
That indicates an object was already found for slit 137, while the extraction
pixel mask contained no pixels assigned to that slit. It is consistent with
the extraction-time mask excluding BADSKYSUB; it does not by itself indicate
that ``spat_id`` values use a different ID convention.

At extraction time, the proposal builds the pixel slitmask from the same
eligibility mask used for extraction. When the option is enabled, this lets
pixels belonging to an otherwise eligible ``BADSKYSUB`` slit reach the
already-found object. If another blocking slit flag is also present, the slit
remains excluded.

Enabling the option
----------------

Add the following to the ``gtc_osiris_plus`` PypeIt file to enable it::

    [reduce]
        [[extraction]]
            extract_badskysub = True

This produces an unsky-subtracted spectrum, not a recovered sky-subtracted
spectrum. Sky emission and residual background remain in the extracted counts;
inspect the 2D data and use the result only when that limitation is acceptable.
