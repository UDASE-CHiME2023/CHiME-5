# CHiME 2023 challenge : Unsupervised domain adaptation for conversational speech enhancement

This repository contains instructions for retrieving the unlabeled data needed for this challenge.

You must first download the [CHiME data](https://spandh.dcs.shef.ac.uk//chime_challenge/CHiME5/download.html).

## Installation

```
# clone data repository
git clone https://github.com/UDASE-CHiME2023/data.git
cd unlabeled_data

# create CHiME conda environment
conda env create -f environment.yml
conda activate CHiME
```

## Extract audio segments

The audio segments are generated from the json files.

```
python create_audio_segments.py /path/to/chime/data/CHiME5 json_files /path/to/output/audio 
```

To get more informations: ```python create_audio_segments.py --help```

## Data informations

The audio segments were extracted for each microphone recording associated with a session Sxx and participant Pxx in the CHiME data as follows:
* **Train data:** 
    - [unlabeled] we extract all segments where Pxx is not active (by default);
    - [unlabeled_10s] we extract all segments where Pxx is not active and split them into consecutive chunks of maximum 10s (with options: ```python create_audio_segments.py --train_10s```);
    - [unlabeled_vad] we extract all segments where Pxx is not active and where Brouhaha VAD detects voice (with options: ```python create_audio_segments.py --train_vad```);
    - [unlabeled_vad_10s] we extract all segments where Pxx is not active and where Brouhaha VAD detects voice, and split them into consecutive chunks of maximum 10s (with options: ```python create_audio_segments.py --train_10s --train_vad```);
* **Dev data:** 
    - [0] we extract all segments where no speaker is active;
    - [1] we extract all segments that were not extracted before and with at most one active speaker (the active speaker might change in a segment, but we do not have overlap between different speakers);
    - [2] we extract all segments that were not extracted before and with at most two simultaneously active speakers (again, the active speakers might change in a segment, we care only about the max number of simultaneously active speakers);
    - [3] we extract all segments that were not extracted before and with at most three simultaneously active speakers.

**Notes:**
- by default, only the right channel is extracted. The ```--extract_stereo``` option allows to extract both left and right channel. Note that ththe right channel works correctly in all extracted audio segments, unlike the left channel. The working state of the microphones is indicated in the json files;
- the option ```--train_only``` allow to save only the train segments;
- we remove the parts of the audio where the participant wearing the microphone is talking (according to the manual transcription);
- manual transcription is also used to split the dev data into [0], [1], [2] and [3];
- the retained segments have a duration greater than 3 seconds;
- recordings with both defective microphones were not extracted, but those with only one defective microphone were (Note: the defective microphones are indicated in the json files);
- unlike the repartition of the CHiME data, we put the S07 and S17 sessions (initially in the train dataset) in the dev dataset in order to increase the noise data [0] duration which was insufficient;
- [Brouhaha VAD](https://github.com/marianne-m/brouhaha-vad) was used to clean the audio segments and estimate the SNR (feel free to use the results when participating to the challenge!):
    - for dev/0 data: an audio segment is not included when speech is detected in at least 3 recordings (among the 4 microphones placed on each participant), when the average SNR of these recordings is greater than 0 and when the average percentage of speech (vs. silence) is greater than 10%;
    - for dev/1 data: an audio segment is not included when no speech is detected.
    - ```brouhaha_vad_snr.csv``` in [brouhaha_vad_snr.zip](metrics/brouhaha/brouhaha_vad_snr.zip) contains the SNR and VAD output for each audio files with a frame rate of 16.875 ms;
    - [brouhaha_mean_results.csv](metrics/brouhaha/brouhaha_results.csv) contains Brouhaha mean outputs metrics (mean SNR, speech duration, speech percentage, etc.).
    - [brouhaha_results.csv](metrics/brouhaha/brouhaha_results.csv) contains Brouhaha outputs used when cleaning the audio files.
    - you will find more informations on Brouhaha results in [load_brouhaha_results.ipynb](load_brouhaha_results.ipynb).
- [DNS-MOS](https://github.com/UDASE-CHiME2023/baseline/blob/main/metrics/dnnmos_metric.py) was computed on dev/1 and are available in [dnsmos.csv](metrics/dnsmos/dnsmos.csv). 


