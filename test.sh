rm -rf done/* tars/* status/* scan/* jobs/*

name="jobbo"

mkdir -p "jobs"
echo $name > jobs/$name

mkdir -p "scan"
for i in `seq 32 43`;
      do
		mkdir scan/scan$i
		for l in `seq 52 63`;
		do
			echo "test $i $l" > scan/scan$i/file$l
		done
		echo "scan/scan$i" >> jobs/$name
      done    	

python26 finalizer.py
tar -tvf tars/$name.tar
