# These are commented out because we set them up before load'ing the script
#INPUT_FILE = "data.txt"
#OUTPUT_FILE = "graph.ps"

# Output to PDF
#set terminal pdf fname 'Helvetica' fsize 10 size 29.0cm,21.7cm
#set output "graph.pdf"

# Output to PS (in case gnuplot is compiled without PDF support)
#set terminal postscript landscape color size 29.0cm,21.7cm font "Helvetica" 10
set terminal postscript landscape enhanced color solid font "Helvetica" 10
set output OUTPUT_FILE

# Output to a PNG image
set terminal png size 640,480 enhanced
set output OUTPUT_FILE

set data style linespoints
set nokey
set grid

# Title
#set title "Ritardo treno 2513 - Giovedi' 8 gennaio 2009"
set title "Ritardo treno"

# X-Axis
set xlabel "Stazione"
set xtics rotate
set xzeroaxis linetype -1 linewidth .5

# Y-Axis
set ylabel "Ritardo (min)"
#set ydata time
#set timefmt "%M"


# Plot!
plot INPUT_FILE using 4:xtic(1)
