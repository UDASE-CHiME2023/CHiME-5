# CHiME-5 data preprocessing

This repository contains instructions for retrieving the unlabeled data needed for the UDASE task of the CHiME-7 challenge.

You must first download the [CHiME-5 data](https://www.chimechallenge.org/datasets/chime5).

If you use this code in your research, please cite:
> Leglaive, S., Borne, L., Tzinis, E., Sadeghi, M., Fraticelli, M., Wisdom, S., Pariente, M., Pressnitzer, D., & Hershey, J. R. (2023). The CHiME-7 UDASE task: Unsupervised domain adaptation for conversational speech enhancement. In 7th International Workshop on Speech Processing in Everyday Environments (CHiME).

## Installation

```
# clone data repository
git clone https://github.com/UDASE-CHiME2023/CHiME-5.git
cd CHiME-5

# create CHiME conda environment
conda env create -f environment.yml
conda activate CHiME
```

## Extract audio segments

To extract the audio segments from the provided json files, you have to run:

```
python create_audio_segments.py /path/to/chime/data/CHiME5 json_files /path/to/output/audio 
```

To get more informations: ```python create_audio_segments.py --help```

## Data information

The audio segments were extracted for each binaural microphone recording associated with a session Sxx and a participant Pxx in the CHiME-5 data as follows:
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
* **Eval data:** 
    - [0/1/2/3] we extract segments using the same method as for the dev data;
    - [listening_test] we extract segments used for the listening tests.

**Notes:**
- by default, only the right channel is extracted. The ```--extract_stereo``` option allows to extract both left and right channels. Note that the right channel works correctly in all extracted audio segments, unlike the left channel. The working state of the microphones is indicated in the json files;
- the options ```--train_only``` and ```--eval_only``` allow to save only the train and the eval segments respectively;
- we remove the parts of the audio where the participant wearing the microphone is talking (according to the manual transcription);
- manual transcription is also used to split the dev data into [0], [1], [2] and [3];
- the retained segments have a duration greater than 3 seconds;
- recordings with both defective microphones were not extracted, but those with only one defective microphone were (Note: the defective microphones are indicated in the json files);
- unlike the repartition of the original CHiME-5 data, we put the S07 and S17 sessions (initially in the train dataset) in the dev dataset in order to increase the noise data [0] duration which was insufficient;
- [Brouhaha VAD](https://github.com/marianne-m/brouhaha-vad) was used to clean the audio segments and estimate the SNR (feel free to use the results when participating to the task!):
    - ```brouhaha_vad_snr.csv``` in [brouhaha_vad_snr.zip](metrics/brouhaha/brouhaha_vad_snr.zip) contains the SNR and VAD output for each audio file with a sampling period of 16.875 ms;
    - [brouhaha_mean_results.csv](metrics/brouhaha/brouhaha_results.csv) contains Brouhaha mean output metrics (mean SNR, speech duration, speech percentage, etc.).
    - [brouhaha_results.csv](metrics/brouhaha/brouhaha_results.csv) contains Brouhaha outputs used when cleaning the audio files.
    - you will find more informations on Brouhaha results in [load_brouhaha_results.ipynb](load_brouhaha_results.ipynb).

