
# Clean
echo "Cleaning build files and/or folders"
rm -rf extensions

# Build
echo "Building extensions..."
mkdir extensions
cp ./dxf_input.py ./extensions/
cp ./dxf_input.inx ./extensions/
cp ./laser.py ./extensions/
cp ./laser.inx ./extensions/
cp ./png.py ./extensions/
cp ./raster2laser_gcode.inx ./extensions/
cp ./raster2laser_gcode.py ./extensions/
cp ./tugas_akhir.inx ./extensions/
cp ./tugas_akhir.py ./extensions/

# copy
echo "Copying To Directory..."
#z="$(inkscape -x)"
#cp extensions/* $z
mkdir -p ~/snap/inkscape/5874/extensions/         # Change this Accordingly
cp extensions/* ~/snap/inkscape/5874/extensions/  # Also This needs to be changed accordingly

#inkscape | tee dev.inkscape.log