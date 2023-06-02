#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import soundfile as sf
import argparse
from pathlib import Path
from tqdm import tqdm
import glob


def time_str_to_sec(time):
    """
    Parameters
    ----------
    time : string H:M:S.cent

    Returns 
    -------
    conversion in seconds

    """
    HMS = time.split('.')[0].split(':')
    cent = time.split('.')[1][:2]
    return float(HMS[0])*3600 + float(HMS[1])*60 + float(HMS[2]) + float(cent)/100


def parse_args():
    parser=argparse.ArgumentParser(description=''' 
        For each audio segment described in the JSON files, the corresponding
        WAV file is extracted from the CHiME dataset.
        By default, only the right channel is extracted.
        ''')

    parser.add_argument("data_dir", help="CHiME data directory.", type=Path)
    parser.add_argument("json_dir", help="Directory storing the json files.", type=Path)
    parser.add_argument("audio_dir", help="Output directory to store the processed audio segments.", type=Path)
    parser.add_argument("--extract_stereo", help="Extract left and right channels.", action='store_true')
    parser.add_argument("--train_10s", help="Slice the train unlabeled audio segments in chunks of 10s.", action='store_true')
    parser.add_argument("--train_vad", help="Only extract audio segments in train where voice has been detected by Brouhaha VAD.", action='store_true')
    parser.add_argument("--train_only", help="Only extract audio segments in train (not dev).", action='store_true')
    parser.add_argument("--eval_only", help="Only extract audio segments in eval.", action='store_true')

    args=parser.parse_args()
    return args

def main():
    # load arguments
    args = parse_args()
    print(args)
    orig_data_path = args.data_dir
    if not orig_data_path.exists():
        raise ValueError("data_dir doesn't exist.")
    proc_data_path = args.audio_dir
    json_path = args.json_dir 
    if not json_path.exists():
        raise ValueError("json_dir doesn't exist.")
    extract_stereo = args.extract_stereo

    # search json files
    file_list = []
    for root, dirs, files in os.walk(json_path):
        for file in files:
            if file.endswith('.json'):
                file_list.append(os.path.join(root, file))
    
    # extract audio segments
    for file_path in file_list:
        
        head, tail = os.path.split(file_path)
        session = tail[:3] # session ID
        ref_spk = tail[4:7] # ref speaker
        num_active_spk = tail[8:-5] # max number of active speakers
        split = os.path.basename(head) # train, dev or eval

        if args.train_only and split != 'train':
            continue
        
        if args.eval_only and split != 'eval':
            continue

        audio_paths = glob.glob(f'{orig_data_path}/audio/*/{session}_{ref_spk}.wav')
        assert len(audio_paths) == 1
        audio_path = audio_paths[0]
        
        audio_session, sr = sf.read(audio_path)
        if not extract_stereo:
            audio_session = audio_session[:,1:]
        
        output_path = os.path.join(proc_data_path, split, num_active_spk)
        if split == 'train':
            if args.train_vad:
                output_path += '_vad'
            if args.train_10s:
                output_path += '_10s'

        if not os.path.isdir(output_path):
            os.makedirs(output_path)
            
        with open(file_path) as f:  
            session_spk_set = json.load(f)
    
        print(split + ' ' + num_active_spk + ' ' + session + ' ' + ref_spk)
        
        for ind_seg, segment in tqdm(enumerate(session_spk_set)):

            mix_ind = segment['mix']
            output_filename = session + '_' + ref_spk + '_' + mix_ind

            if not os.path.exists(os.path.join(output_path, output_filename)):
                if split == 'dev':
                    assert segment['max_num_simultaneously_active_spk'] == int(num_active_spk)
                
                start_str = segment['start']
                end_str = segment['end']
                                
                start_time = time_str_to_sec(start_str)
                end_time = time_str_to_sec(end_str)
                
                start_ind = int(np.round(start_time*sr))
                end_ind = int(np.round(end_time*sr))
                
                audio_seg = audio_session[start_ind:end_ind,:]

                # use brouhaha VAD
                if split == 'train' and args.train_vad:
                    brouhaha_sr = 1/0.016875
                    vad = [int(i) for i in segment['brouhaha_vad']]
                    speech_start_ind = []
                    speech_end_ind = []
                    for i in range(len(vad)):
                        if vad[i] == 1:
                            if i == 0:
                                speech_start_ind.append(i)
                            elif i == len(vad)-1:
                                speech_end_ind.append(i)
                            else:
                                if vad[i-1] == 0:
                                    speech_start_ind.append(i)
                                if vad[i+1] == 0:
                                    speech_end_ind.append(i+1)
                    audios = []
                    for start, end in zip(speech_start_ind, speech_end_ind):
                        start_time = start/brouhaha_sr
                        end_time = end/brouhaha_sr
                        audios.append(audio_seg[int(np.round(start_time*sr)):int(np.round(end_time*sr))])
                else:
                    audios = [audio_seg]
                
                # save chunks of 10s
                chunk = 0
                for audio in audios:

                    duration = audio.shape[0]/sr
                    if duration < 3:
                        continue

                    if split == 'train' and args.train_10s:
                        max_chunk_time = 10
                        for i in range(int(np.ceil(duration/max_chunk_time))):

                            start_time = max_chunk_time*(i)
                            end_time = max_chunk_time*(i+1)
                            
                            audio_chunk = audio[int(np.round(start_time*sr)):int(np.round(end_time*sr))]

                            chunk_duration = audio_chunk.shape[0]/sr
                            if chunk_duration < 3:
                                continue

                            sf.write(os.path.join(output_path, f'{output_filename}_{chunk}.wav'), audio_chunk, sr, 'PCM_16')
                            chunk += 1
                    else:
                        if len(audios) == 1:
                            sf.write(os.path.join(output_path, f'{output_filename}.wav'), audio, sr, 'PCM_16')
                        else:
                            sf.write(os.path.join(output_path, f'{output_filename}_{chunk}.wav'), audio, sr, 'PCM_16')
                            chunk += 1
                            
if __name__ == '__main__':
    main()    

