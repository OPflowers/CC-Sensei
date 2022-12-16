import os
import subprocess

VIDEOS = 8


def create_bba_traces():
    os.environ['VIDEO_NO'] = '0'
    os.environ['TEST'] = "bba"
    command = ["python3", "bb.py"]
    subprocess.run(command)


def create_sensei_traces():
    # run rl_no_training.py for all sensei
    # each trace has their own individual model
    for i in range(0, VIDEOS):
        os.environ['VIDEO_NO'] = str(i)
        os.environ['TEST'] = "sensei"
        command = ["python3", "rl_no_training.py", "-t", "sensei"]
        subprocess.run(command)


def create_pensieve_traces():
    # run rl_no_training.py for all pensieve
    # run using linear weight, 25000 repetitions
    os.environ['VIDEO_NO'] = '0'
    os.environ['TEST'] = "pensieve"
    command = ["python3", "rl_no_training.py", "-t", "pensieve"]
    subprocess.run(command)


def main():
    create_bba_traces()
    create_sensei_traces()
    create_pensieve_traces()


if __name__ == "__main__":
    main()