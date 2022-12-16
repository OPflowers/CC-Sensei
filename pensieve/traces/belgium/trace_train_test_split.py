import shutil
import os
import random
train_test_split_proportion = 0.8

in_path = "./converted_traces/"

out_path_train = "../../sim/cooked_traces/"
out_path_test = "../../sim/cooked_test_traces/"

if os.path.exists(out_path_train):
    shutil.rmtree(out_path_train)

if os.path.exists(out_path_test):
    shutil.rmtree(out_path_test)


os.mkdir(out_path_train)
os.mkdir(out_path_test)

for file in os.listdir(in_path):
    rand = random.random()
    if rand < train_test_split_proportion:
        shutil.copy(in_path + file, out_path_train)
    else:
        shutil.copy(in_path + file, out_path_test)