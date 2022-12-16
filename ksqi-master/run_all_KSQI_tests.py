import os
import subprocess

VIDEOS = 8


def run_BBA():
    os.environ['ABR'] = 'BBA'
    os.environ['VIDEO_NO'] = '0'
    command = ["python3",
               "main.py",
               "--set",
               "MODE", "test",
               "DATASET", "custom_data",
               "INPUT_DIR", "data/custom_data/bba/",
               "MODEL", "KSQI",
               ]
    subprocess.run(command)
    return


def run_pensieve():
    os.environ['ABR'] = 'pensieve'
    os.environ['VIDEO_NO'] = '0'
    command = ["python3",
               "main.py",
               "--set",
               "MODE", "test",
               "DATASET", "custom_data",
               "INPUT_DIR", "data/custom_data/pensieve/",
               "MODEL", "KSQI",
               ]
    subprocess.run(command)
    return


def run_sensei():
    os.environ['ABR'] = 'sensei'
    for i in range(0, 8):
        os.environ['VIDEO_NO'] = str(i)
        command = ["python3",
                   "main.py",
                   "--set",
                   "MODE", "test",
                   "DATASET", "custom_data",
                   "INPUT_DIR", "data/custom_data/sensei/video" + str(i) + "/",
                   "MODEL", "KSQI:SENSEI_KSQI:P1203:Bentaleb2016QoE",
                   ]
        subprocess.run(command)
    return


def run_sensei_all():
    os.environ['ABR'] = 'sensei-all'
    os.environ['VIDEO_NO'] = '0'
    command = ["python3",
               "main.py",
               "--set",
               "MODE", "test",
               "DATASET", "custom_data",
               "INPUT_DIR", "data/custom_data/sensei-all/",
               "MODEL", "KSQI:SENSEI_KSQI:P1203:Bentaleb2016QoE",
               ]
    subprocess.run(command)
    return


def main():
    run_BBA()
    run_pensieve()
    run_sensei()
    run_sensei_all()
    return


if __name__ == '__main__':
    main()
