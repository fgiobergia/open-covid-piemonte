# periodically check for new data
# (and push to git repository if 
# something new is found
while [ 1 ] ; do
    python fetch.py
    if [ $? == 0 ]; then
        # a particularly dirty solution, but bash is seldom clean
        fname=$(git status | grep csv | head -n 1 | tr -d "\t")
        git add $fname # hopefully we are getting this right!
        git commit -m "added $fname"
        git push
        echo "added $fname"
    fi
    sleep 3600 # check back in 1 hour
done
