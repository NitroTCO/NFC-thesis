if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <trace-file> <sample-frequency>"
fi

rm smoothed_signal.txt
touch smoothed_signal.txt
make
echo "=== filtering ==="
time python mfdes_demodulate.py -f -t $1 -s $2
echo "=== ./main ==="
time ./main -s $2