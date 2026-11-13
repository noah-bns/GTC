BADSKYSUB boxcar extraction for GTC/OSIRIS
=========================================

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

Add the following to the ``gtc_osiris_plus`` PypeIt file to enable it::

    [reduce]
        [[extraction]]
            extract_badskysub = True

This produces an unsky-subtracted spectrum, not a recovered sky-subtracted
spectrum. Sky emission and residual background remain in the extracted counts;
inspect the 2D data and use the result only when that limitation is acceptable.
