import os
import argparse
import subprocess
import shutil

import zipfile
import glob


import time
import psutil
from pathlib import Path
from run_hover_net import run_hover_net
from get_mask import generate_mask



def run_segment():
  img_formats = ['jpg', 'png', 'tiff']
  
  input_folder_path = os.path.join(os.sep, 'app', 'src', 'inputs')
  output_folder_path = os.path.join(os.sep, 'app', 'src', 'outputs')
  mask_folder_path = os.path.join(os.sep, 'app', 'src', 'outputs', 'mask')
  temp_folder_path = os.path.join(os.sep, 'app', 'src', 'temp')
  
  os.makedirs(input_folder_path, exist_ok=True)
  os.makedirs(output_folder_path, exist_ok=True)
  os.makedirs(temp_folder_path, exist_ok=True)
  os.makedirs(mask_folder_path, exist_ok=True)
  # Run hover net
  run_hover_net()
  
  input_files_path = glob.glob(os.path.join(input_folder_path, '*'))
  for file in input_files_path:
      if (Path(file).suffix[1:] in (img_formats)):
          # Generate masks for all image 
          generate_mask(file)
  shutil.rmtree(os.path.join(output_folder_path,'json'))
  shutil.rmtree(os.path.join(output_folder_path,'mat'))


def run_analyze(pipeline='features'):
  if pipeline=='features':
    pipeline_file = 'pipeline.cppipe'
  if pipeline=='features_nucleoli':
    pipeline_file = 'pipeline_nucleoli.cppipe'
  
  dir_study = os.path.join('/app', 'study')
  samples_all = os.listdir(dir_study)
  samples_pending = []
  for sample in samples_all:
    if('mat' not in os.listdir(os.path.join(dir_study, sample))): # if 'mat' present, segmentation incomplete
      if(pipeline not in os.listdir(os.path.join(dir_study, sample))): # if 'features' present, analysis already done
        samples_pending.append(sample)

  commands = []
  for sample in samples_pending:
    cmd = ['cellprofiler', '-c', '-r', '-p', pipeline_file, 
    '-i', os.path.join('/app', 'study', sample, "temp"), 
    '-o', os.path.join('/app', 'study', sample)]
    commands.append(' '.join(cmd))
  
  with open('/app/src/jobs_analysis.txt', 'w+') as f:
    for items in commands:
  	  f.write('%s\n' %items)
    f.close()
  
  os.system('cat /app/src/jobs_analysis.txt | parallel -j ' + args.threads)


if __name__ == '__main__':
  str_desc = '...'
  str_usage = 'python3 run_segment_analyze.py --action [segment|analyze] (--threads 8)'
  
  parser = argparse.ArgumentParser(description=str_desc, usage=str_usage)
  parser.add_argument('--action', dest='action', required=True, choices=['segment', 'analyze', 'nucleoli'])
  parser.add_argument('--threads', dest='threads', required=False, default='8')
  
  os.chdir('/app/src')
  args = parser.parse_args()
  print(args)
  if args.action=='segment':
    run_segment()
  if args.action=='analyze':
    run_analyze(pipeline='features')
  if args.action=='nucleoli':
    run_analyze(pipeline='features_nucleoli')
  
  
  
  
