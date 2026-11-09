# Init and Tutorials

## Help Option

Use  -h
ex: $ pypeit_setup -h

## Download the example Files

This branch serves to reporduces the steps given as tutorials and examples by the PypeIt website.

git clone https://github.com/pypeit/PypeIt-development-suite.git
export PYPEIT_DEV=/Users/noah/GTC/PypeIt-development-suite

cd $PYPEIT_DEV             
ln -s ~/Library/CloudStorage/GoogleDrive-noah.bensoussann@gmail.com/My\ Drive/PypeIt-development-suite/RAW_DATA  RAW_DATA
ln -s ~/Library/CloudStorage/GoogleDrive-noah.bensoussann@gmail.com/My\ Drive/PypeIt-development-suite/CALIBS  CALIBS

### Run test

$PYPEIT_DEV/pypeit_test all


## Run Shane-Kast HOWTO

mkdir SHANE_KAST_RD
export RAW_PATH=/Users/noah/GTC/PypeIt-development-suite/RAW_DATA/shane_kast_blue/600_4310_d55

cd SHANE_KAST_RD   # this is usually *not* the raw data folder
pypeit_setup -r $RAW_PATH/b -s shane_kast_blue -c A # There is only one instrument configuration for this dataset, meaning using --c A and -c all are equivalent

cd shane_kast_blue_A
run_pypeit shane_kast_blue_A.pypeit #If need to re-run the code: use the -o option to ensure the code overwrites any existing output files (excluding processed calibration frames). 
    #If need to re-build the calibrations, it’s best to remove the relevant (or all) files from the Calibrations/ directory instead of using the -m option

### verifications

ginga Calibrations/Bias_A_0_DET01.fits #view a frame
pypeit_chk_edges Calibrations/Edges_A_0_DET01.fits.gz #view edges
pypeit_chk_tilts Calibrations/Tilts_A_0_DET01.fits.gz #script so assess the arcline traces against the image
pypeit_chk_flats Calibrations/Flat_A_0_DET01.fits #view flats

pypeit_show_2dspec Science/spec2d_b27-J1217p3905_KASTb_20150520T045733.560.fits #view 2D spectra with yellow lines for the object traces
pypeit_show_1dspec Science/spec1d_b27-J1217p3905_KASTb_20150520T045733.560.fits #view 1D spectra with lines

#generate sensitivity file from standard reduced star spectrum
pypeit_sensfunc Science/spec1d_b24-Feige66_KASTb_20150520T041246.960.fits -o Kastb_feige66_sens.fits

## Run Keck-DEIMOS HOWTO

Contains more than one mask or observations with various gratings. Must include all of the calibrations for each.

naming:If your files included more than one setup (including multiple masks), then you may wish to replace A in the call to pypeit_setup with B or some other setup indicator. Inspect the *.sorted file in the setup_files/ folder to see all the options.

It is the user’s responsibility to remove any bad (or undesired) calibration or science frames from the list. Either delete them altogether or comment out with a #.

PypeIt can construct image mosaics for detectors separated along the dispersion axis.


mkdir KECK_DEIMOS_RD
export RAW_PATH=/Users/noah/GTC/PypeIt-development-suite/RAW_DATA/keck_deimos/1200G_M_7750

cd KECK_DEIMOS_RD
pypeit_setup -r $RAW_PATH/DE. -s keck_deimos -c A

###edit in the pypeit file to only view one detector (number 7)
#User-defined execution parameters
[rdx]
spectrograph = keck_deimos
detnum = 7 #For more than one detector, use a list for detnum (e.g. detnum = 3,7)
###.

cd keck_deimos_A
run_pypeit keck_deimos_A.pypeit -o #-o indicates that any existing output files should be overwritten

### Check Spectra

#### summary of the slits successfully reduced by PypeIt
pypeit_parse_slits Science/spec2d_DE.20170425.50487-dra11_DEIMOS_2017Apr25T140121.014.fits #prints, detector by detector, the SpatID (internal PypeIt name), MaskID (user ID), and Flags for each slit. Those with None have been successfully reduced

#### view specific spectra for detector 7
pypeit_show_2dspec Science/spec2d_DE.20170425.50487-dra11_DEIMOS_20170425T140121.014.fits --det 7 #can limit viewing to only a subset of the channels with the –channels option
#Yellow lines indicate sources that were auto-magically extracted based on the mask design (i.e. insufficient SNR)
#night sky and emission lines have been subtracted

#### summary of 1Dspectra
in the spec1d*.txt file

##### pypeit_show_1dspec options
pypeit_show_1dspec Science/spec1d_DE.20170425.50487-dra11_DEIMOS_20170425T140121.014.fits --list #smaller set of output using the –list option 

pypeit_show_1dspec Science/spec1d_DE.20170425.50487-dra11_DEIMOS_20170425T140121.014.fits --exten 23 #in red is the estimated error

### Flux calibration

#### Using archived sensitivity functions

######.
#Create a flux file (here names keck_deimos_1200g_m_7750.flux)
######.
[fluxcalib]
use_archived_sens = True

#User-defined fluxing parameters
flux read
  filename
  Science/spec1d_DE.20170425.50487-dra11_DEIMOS_20170425T140121.014.fits
flux end
######.
######.

#### Run and view with --flux
pypeit_flux_calib keck_deimos_1200g_m_7750.flux
pypeit_show_1dspec Science/spec1d_DE.20170425.50487-dra11_DEIMOS_20170425T140121.014.fits --exten 23 --flux

### Flexure correction
The default run performs a flexure correction, slit-by-slit based on analysis of the sky lines to impose a fixed pixel shift for each detector in the spectral dimension. For a more accurate solution, it may be preferred to perform flexure across both detectors.

## GTC Data Test

mkdir GTC_R2500I_RD
cd GTC_R2500I_RD

export RAW_PATH=/Users/noah/GTC/RAW_GTC/R2500I

pypeit_obslog gtc_osiris_plus -r RAW_PATH -k > obslog_keys.txt #save the key names
pypeit_obslog gtc_osiris_plus -r RAW_PATH -c all  > obslog_columns.txt #got the error "Unable to find any raw files for gtc_osiris_plus in RAW_PATH!" ????
pypeit_setup -r $RAW_PATH -s gtc_osiris_plus -c all
#then edit all standards to science

cd gtc_osiris_plus_A
run_pypeit gtc_osiris_plus_A.pypeit -o 

### Verify the mis detection

Look for Find Object lack

Look for Extraction issue:
pypeit_parse_slits Science/spec2d_0005546748-20250814-OSIRIS-OsirisMOS-red_box_OSIRIS_20250815T025930.142.fits
 
# Dissecting Steps

## Show option
ginga --modules=RC,SlitWavelength & #allow remote ginga control

## Run up to a Calib Step (if files missing)

Provide: 
(1) the PypeIt file, 
(2) the calibration step to re-run to, and 
(3) either the raw science file whose calibration file(s) you wish to re-run or the calib_group ID (and --det optionally)

Valid steps are: align, arc, bias, bpm, dark, flats, scattlight, slits, tiltimg, tilts, wv_calib

pypeit_run_to_calibstep shane_kast_blue_A.pypeit wv_calib --science_frame b28.fits.gz -s #-s shows lots of plots Requires remote control ginga session via "ginga --modules=RC,SlitWavelength &"

## Run each Processing step

### Step 1: Process the raw image
pypeit_reduce_by_step my_reduction.pypeit science_frame.fits process --det 1 --show

produces:
- Intermediate/sciImg_<basename>_<det>.fits: Processed science image
- Intermediate/bkgImg_<basename>_<det>.fits: Background image (if applicable)

### Step 2: Find objects
pypeit_reduce_by_step my_reduction.pypeit science_frame.fits findobj --det 1 --show

produces:
- Science/initsky_<basename>_<det>.fits: Initial sky model
- Science/spec1d_<basename>_<det>.fits: Object catalog with traces (no extractions)

### Step 3: Extract spectra
pypeit_reduce_by_step my_reduction.pypeit science_frame.fits extract --det 1 --show

Produces final products:
- Science/spec2d_<basename>.fits: 2D spectrum
- Science/spec1d_<basename>.fits: Extracted 1D spectra

### Step 4: Full integration
rm -rf Science/ Calibrations/ # Remove intermediate files to start fresh
run_pypeit my_reduction.pypeit # Run full reduction with optimized parameters
