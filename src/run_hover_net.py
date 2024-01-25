import torch
import logging
import os
import copy
import sys
sys.path.append('/app/hover_net')

from misc.utils import log_info
#-------------------------------------------------------------------------------------------------------

def run_hover_net():

    # ! TODO: where to save logging
    logging.basicConfig(
        level=logging.INFO,
        format='|%(asctime)s.%(msecs)03d| [%(levelname)s] %(message)s',datefmt='%Y-%m-%d|%H:%M:%S',
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

    args = {"gpu":"0", "nr_types":0, "type_info_path":"", 
            "model_path":"../hovernet_model/hovernet_original_kumar_notype_tf2pytorch.tar", 
            "model_mode": "original",
            "nr_inference_workers":1,
            "nr_post_proc_workers":16,
            "batch_size":32,
            }
    
    sub_args = {"input_dir": "inputs",
                "output_dir":"outputs",
                "mem_usage":0.2,
                "draw_dot":True,
                "save_qupath":False,
                "save_raw_map":False}

    gpu_list = args.pop('gpu')
    os.environ['CUDA_VISIBLE_DEVICES'] = gpu_list

    nr_gpus = torch.cuda.device_count()
    log_info('Detect #GPUS: %d' % nr_gpus)

    if args['model_path'] == None:
        raise Exception('A model path must be supplied as an argument with --model_path.')

    nr_types = int(args['nr_types']) if int(args['nr_types']) > 0 else None
    method_args = {
        'method' : {
            'model_args' : {
                'nr_types'   : nr_types,
                'mode'       : args['model_mode'],
            },
            'model_path' : args['model_path'],
        },
        'type_info_path'  : None if args['type_info_path'] == '' \
                            else args['type_info_path'],
    }

    # ***
    run_args = {
        'batch_size' : int(args['batch_size']) * nr_gpus,

        'nr_inference_workers' : int(args['nr_inference_workers']),
        'nr_post_proc_workers' : int(args['nr_post_proc_workers']),
    }

    if args['model_mode'] == 'fast':
        run_args['patch_input_shape'] = 256
        run_args['patch_output_shape'] = 164
    else:
        run_args['patch_input_shape'] = 270
        run_args['patch_output_shape'] = 80

    run_args.update({
        'input_dir'      : sub_args['input_dir'],
        'output_dir'     : sub_args['output_dir'],

        'mem_usage'   : float(sub_args['mem_usage']),
        'draw_dot'    : sub_args['draw_dot'],
        'save_qupath' : sub_args['save_qupath'],
        'save_raw_map': sub_args['save_raw_map'],
    })
    

    from infer.tile import InferManager
    infer = InferManager(**method_args)
    infer.process_file_list(run_args)