set size 1.0, 0.6
set terminal postscript portrait enhanced color  lw 2 "Helvetica" 14 
set output "stats-plot.ps"

set timestamp
set log xy
set xlabel 'catalog entries [#]'
set ylabel 'ratio [Atomic/Composite]'
set xrange [0.1:10000000]  
set yrange [0.1:200]
#set title 'Ratio of Calculation Time bet. Atomic- and Composite-Index Queries'
plot "stat.dat" using ($1):($2/$3) title '2 attributes query' w linespoints , "stat.dat" using ($1):($4/$5) title '3 attributes query' w linespoints

