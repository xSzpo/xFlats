#!/bin/bash
cd /Users/xszpo/GoogleDrive/DataScience/Projects/201907_xFlat_AWS_Scrapy/app_mlmodel/DEVELOP_MODEL/nni/.
export NNI_PLATFORM=local
export NNI_EXP_ID=WMYbCwC9
export NNI_SYS_DIR=/Users/xszpo/nni/experiments/WMYbCwC9/trials/V6PAz
export NNI_TRIAL_JOB_ID=V6PAz
export NNI_OUTPUT_DIR=/Users/xszpo/nni/experiments/WMYbCwC9/trials/V6PAz
export NNI_TRIAL_SEQ_ID=20
export MULTI_PHASE=false
export CUDA_VISIBLE_DEVICES=-1
eval python main.py 2>/Users/xszpo/nni/experiments/WMYbCwC9/trials/V6PAz/stderr
echo $? `date +%s999` >/Users/xszpo/nni/experiments/WMYbCwC9/trials/V6PAz/.nni/state