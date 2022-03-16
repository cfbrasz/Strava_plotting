
folder='exported_data/activities'

# Deletes whitespace on the first line before the xml tag
# If we don't, the whitespace prevents the tcx conversion from working
for i in $folder/*.tcx; do
  sed '1 s/^[ \t]*//' -i $i
done
