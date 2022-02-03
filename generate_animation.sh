
# Slow movies here:
#ffmpeg -framerate 30 -i plots/vary_N/routes_boston_N%d.png boston_animation.mp4
#ffmpeg -framerate 30 -i plots/vary_N_zoom/routes_boston_N%d.png boston_animation_zoom.mp4

# Speed up 10x by only including files that end in 0
# (20 fps instead of 30 fps makes it 6.6x actually)
ffmpeg -framerate 20 -i plots/vary_N/routes_boston_N%d0.png boston_animation_10x.mp4
ffmpeg -framerate 20 -i plots/vary_N_zoom/routes_boston_N%d0.png boston_animation_zoom_10x.mp4

#additional option to hold last frame for 2 seconds
#ffmpeg -framerate 20 -i plots/vary_N/routes_boston_N%d0.png -vf tpad=stop_mode=clone:stop_duration=2  boston_animation_10x.mp4
