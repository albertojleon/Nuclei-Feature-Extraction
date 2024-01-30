import os
import subprocess
import pandas as pd


study = 'TCGA-SKCM'

samples_all = os.listdir(os.path.join('/data', 'countic', 'tiles_selected', study))
samples_done = os.listdir(os.path.join('/data', 'countic', 'nuclei-feature-extraction', study))
samples_pending = [sample for sample in samples_all if sample not in samples_done]

#samples_pending = samples_pending[1::2] ############################################################## TEMPORARY sub-sampling!!!


docker_img = 'nuclei-feature-extraction:01'

for sample in samples_pending:
  dir_in = os.path.join('/data', 'countic', 'tiles_selected', study, sample)
  dir_out = os.path.join('/data', 'countic', 'nuclei-feature-extraction', study, sample)
  os.makedirs(dir_out, exist_ok=True)
  cmd_inner = ['cd /app/src;', 'python3', '/app/src/run_segment_analyze.py', "--action", "segment"]
  cmd_docker = ['docker', 'run', '--rm', '--gpus \'"device=0"\'',
                '--name', docker_img.split(':')[0] + '_' + sample,
                '-v', dir_in + ':/app/src/inputs',
                '-v', dir_out + ':' + '/app/src/outputs',
                '-v', dir_out + '/temp:' + '/app/src/temp',
                '-v', '/data/docker/Nuclei-Feature-Extraction/src:/app/src', # for DEV only!!!
                '--entrypoint', 'bash',
                docker_img]
  cmd = ' '.join(cmd_docker) + ' -c \"' + ' '.join(cmd_inner) + '\"'
  print(cmd)
  os.system(cmd)





cmd_docker = ['docker', 'run', '--rm',
              '--name', docker_img.split(':')[0] + '_analyze',
              '-v', os.path.join('/data', 'countic', 'nuclei-feature-extraction', study) + ':/app/study',
              '-v', '/data/docker/Nuclei-Feature-Extraction/src:/app/src', # for DEV only!!!
              '--entrypoint', 'bash', 
              docker_img,
              '-c', '"python3 /app/src/run_segment_analyze.py --action=analyze --threads=16"']
cmd = ' '.join(cmd_docker) 
print(cmd)
os.system(cmd)


