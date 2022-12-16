CS 6111 - Semester Project: SENSEI - Aligning Video Streaming Quality with Dynamic User Sensitivity, Xu Zhang and Yiyang Ou

***
For our plots in paper, run (with an editor that can open matplotlib graphs like PyCharm)
- cd ksqi-master/results/
- python3 plot_performance.py
***

The videos for the project (original and augmented) can be found in this Google Drive:
- https://drive.google.com/drive/u/0/folders/1vSZHNcQ0cvHzoAam_HV_3380Caa7WdRE
- place them inside their respective folders (phase 1 and phase 2) inside "Augmented Videos"

In this project, we test the following in SENSEI's methodology:
- SENSEI's weighted QoE modeling improvements, comparing to KSQI, P.1203
    - https://github.com/zduanmu/ksqi
- SENSEI's modified ABR algorithm, applied to Pensieve/Buffer Based Adaptation
    - https://github.com/hongzimao/pensieve
- SENSEI's performance metrics:
    - QoE Gain
    - Bandwidth Saving

To generate vmaf metrics, ffmpeg-vmaf is required. We used the pre-built ffmpeg with vmaf packaged installed here:
    - https://www.johnvansickle.com/ffmpeg/

Many of the other projects that we used code from used Python 2; we reconfigured them to work in Python 3 instead.

The differences in the software/initialization software/results are discussed in the paper.

Due to crowdsourcing constraints and lack of responses, we test SENSEI's methodology on the augmented videos used for crowdsourcing to determine how well it aligns with distorted videos. Our pipeline was as follows:
- Create first augmented videos, containing quality incidents in every 4 second chunk each. In this round also contains unbiased videos for a ground truth QoE sample.
- Create second round of augmented videos, containing quality incidents in every second of the most sensitive chunk from the first round
    - We chose to not select on chunks passing a sensitivity threshold like the original paper due to a lack of responses from the first round
- Reformat sample traces from Belgium's LTE bandwidth logs to be within 0.2-6 Mbps.
- Reformat augmented video information and pass through KSQI
- Use KSQI individual chunk QoE factor and the unbiased ground truth QoE video values in a linear regression to determine the video's sensitivity weights.
- Use the weights to create SENSEI-Pensieve for each video; retrain Pensieve's DNN with minor modifications
- Generate new traces stemming from sample traces using the ABR algorithms.
- Test performance of new traces using SENSEI-KSQI and graph its results.

Code order:
1. Videos can be found on the Google Drive; place into 'Augmented Videos' folder
2. Original sample traces can be found in 'pensieve/traces/belgium/belgium'
3. Get weights:
    - cd ksqi-master/data
    - python3 create_custom_data_from_videos.py -w True
    - cd ../
    - export ABR=sensei
    - export VIDEO_NO=0
    - python3 main.py --set MODE test DATASET custom_data INPUT_DIR data/custom_data/weights/ MODEL KSQI
    - python3 compute_weights.py
4. Retrain SENSEI-Pensieve (models already present in code)
    * We manually reset the environment variables because rerunning the DNNs took a long time. We also manually copied over the model results after training as well. Code for creating the training/test traces can be found in pensieve/traces/
    - export VIDEO_NO=[x]
    - export ABR='sensei'
    - cd Project/pensieve/sim
    - python3 multi_agent.py
5. Generate SENSEI-Pensieve output
    * for BBA/Pensieve, set ABR='bba'/'pensieve'
    - cd Project/pensieve/test/
    - python3 rl_no_learning.py
6. Generate augmented videos' traces using ABR output
    - cd Project/ksqi-master/data/
    - python3 create_custom_data_from_videos.py -w False
7. Run all QoE Models
    - cd Project/ksqi-master/
    - python3 run_all_KSQI_tests.py
8. With a python terminal that can open matplotlib graphs:
    - cd Project/ksqi-master/results/
    - python3 plot_performance.py or run in PyCharm




