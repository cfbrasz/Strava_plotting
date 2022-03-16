# Strava_plotting
Scripts for plotting Strava data

## Getting started

Download your Strava data with the Bulk Export option from https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export

To match the file paths I used, place the data in a subfolder of the repo and name it ```exported_data```

Install ```fit2gpx``` (for example with ```pip3 install fit2gpx``` if using pip) in case any of your activities in ```exported_data/activities/``` have ```.fit.gz``` file type. I got these when I started using a Garmin watch to log workouts rather than my phone. This package will convert ```fit``` files to ```gpx``` files -- see https://pypi.org/project/fit2gpx/.

Convert your ```fit``` files to ```gpx``` format by running ```convert_fit_files.py```. This is Use Case 3 from https://pypi.org/project/fit2gpx/

You now should have an ```exported_data/activities_gpx/``` folder with all your Strava activities. These gpx files are xml format, and to import them into Python, you'll need to install the package ```gpxpy```.

Once that package is installed, you should be able to run all the Python scripts in the repo and modify them for your own use.

You may also have ```tcx``` files depending on your device (I get them with a Samsung watch), and there's a ```tcx2gpx``` package that can similarly be downloaded with pip (see https://pypi.org/project/tcx2gpx/#description). To convert your ```tcx``` files, first run the bash script ```remove_leading_whitespace_from_tcx_files.sh```. (Without removing leading whitespace, the XML reader in the ```tcx2gpx``` package fails.) Then, run the Python script ```convert_tcx_files.py``` to find and convert each ```tcx``` file and copy the resulting ```gpx``` file to the ```activities_gpx``` folder.

## Other resources

I used https://towardsdatascience.com/data-science-for-cycling-how-to-read-gpx-strava-routes-with-python-e45714d5da23 to get started in getting my Strava data accessible in Python. The in-depth instructions there should help if anything above is unclear.

## Description of scripts

```plot_route.py``` is the simplest one, which plots the gps coordinates of a single activity file. You'll have to pick one out and modify the file to put in a valid file name, but it shows how you can use the ```gpxpy``` package.

```plot_mult_routes.py``` overlays many activities on top of each other on the same plot. By using partial transparency, a heat map is generated. The coordinates are set to the Cambridge/Somerville, MA area in the file. The script also ignores any activities where two consecutive gps points are too far away from each other, as these errant lines mess with the final map created. Different activity types are given different colors.

```plot_animation.py``` generates frames for an animation of cumulative heat maps starting from your first activity and progressing through to the last. The frames can be combined into an ```mp4``` movie with ```ffmpeg``` with the commands given in the ```bash``` script ```generate_animation.sh```.

## Example output
![routes_boston_N2229](https://user-images.githubusercontent.com/2495587/151738930-58fd8403-76ab-4158-b556-cf31bf543a4c.png)
![routes_boston_N2229_zoom](https://user-images.githubusercontent.com/2495587/151738935-953a437e-a095-454c-9549-e77e7b83344f.png)

