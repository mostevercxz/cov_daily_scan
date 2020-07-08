#!/bin/bash
set -x
set -e

# get date of today in format "%Y%m%d"
today_datestr=`date +"%Y%m%d"`
UNAME=your_user_name
HOST=192.168.12.136
PASSWORD=your_password



## Step 1: make working directory
work_dir="/home/your_user_name/cov_work_"$today_datestr
if [ -d $work_dir ]; then
	rm -rf $work_dir
fi
mkdir $work_dir
result_dir=$work_dir/result/
## Step 2: svn up, update resource, generate proto.pb.cc
cd /home/your_user_name/Game && svn up && ./update_res all
## Step 2: cov-build
cov-build --dir $result_dir /home/your_user_name/Game/build.sh
## Step 3: cov-analyze
# 增强扫描
#cov-analyze --aggressiveness-level high --dir $result_dir
cov-analyze --dir $result_dir
## Step 4: cov-format-errors
cd $work_dir && cov-format-errors --dir $result_dir --html-output  $today_datestr/
## Step 5: Filter html result
html_dir=$work_dir/$today_datestr
cp /home/your_user_name/Game/cov.py $html_dir && cd $html_dir && python cov.py
## Step 6: Scp all the results to 192.168.12.136 server
sshpass -p $PASSWORD scp -o StrictHostKeyChecking=no -r $html_dir $UNAME@$HOST:/home/$UNAME/scan_results/converity
## Step 7: Generate summary index.html file
sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no $UNAME@$HOST "cd /home/$UNAME/scan_results/converity && python generate_index.py"
