import os
import argparse
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np
import tensorflow.compat.v1 as tf
import fixed_env as env
import a3c
import load_trace
import matplotlib.pyplot as plt
import get_qoe_by_chunk_for_video


VIDEO_NO = int(os.environ['VIDEO_NO'])
CHUNK_QOE = get_qoe_by_chunk_for_video.get_weights(VIDEO_NO)
TEST = os.environ['TEST'].lower()

S_INFO = 7  # bit_rate, buffer_size, next_chunk_size, bandwidth_measurement(throughput and time), chunk_til_video_end, do rebuffer
S_LEN = 8  # take how many frames in the past
A_DIM = 5
ACTOR_LR_RATE = 0.0001
CRITIC_LR_RATE = 0.001
VIDEO_BIT_RATE = [300, 750, 1200, 1850, 2850]  # Kbps
BUFFER_NORM_FACTOR = 10.0
# CHUNK_TIL_VIDEO_END_CAP = 48.0
CHUNK_TIL_VIDEO_END_CAP = 20
M_IN_K = 1000.0
REBUF_PENALTY = 4.3  # 1 sec rebuffering -> 3 Mbps
SMOOTH_PENALTY = 1

DEFAULT_QUALITY = 1  # default video quality without agent
RANDOM_SEED = 42
RAND_RANGE = 1000

QOE_PENALTY = 1

SUMMARY_DIR = './results'
LOG_FILE = './results/log_sim_rl'

# log in format of time_stamp bit_rate buffer_size rebuffer_time chunk_size download_time reward
# regular pensieve pre-trained model given by authors
NN_MODEL = './models/pretrain_linear_reward.ckpt'

# SENSEI-PENSIEVE models
VIDEO_NN_MODELS = ['./models/video0-10100.ckpt',
                   './models/video1-10900.ckpt',
                   './models/video2-11700.ckpt',
                   './models/video3-10700.ckpt',
                   './models/video4-14200.ckpt',
                   './models/video5-10100.ckpt',
                   './models/video6-10400.ckpt',
                   './models/video7-11100.ckpt']

def main():
    if TEST == "sensei":
        SUMMARY_DIR = './results/sensei/'
        LOG_FILE = './results/sensei/video' + str(VIDEO_NO) + '-log_sim_rl'
        NN_MODEL = VIDEO_NN_MODELS[VIDEO_NO]
    else:
        SUMMARY_DIR = './results/pensieve/'
        LOG_FILE = './results/pensieve/log_sim_rl'
        NN_MODEL = './models/pensieve-25000.ckpt'

    np.random.seed(RANDOM_SEED)

    assert len(VIDEO_BIT_RATE) == A_DIM

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    all_cooked_time, all_cooked_bw, all_file_names = load_trace.load_trace()

    net_env = env.Environment(all_cooked_time=all_cooked_time,
                              all_cooked_bw=all_cooked_bw)

    log_path = LOG_FILE + '_' + all_file_names[net_env.trace_idx]
    log_file = open(log_path, 'w')

    with tf.Session() as sess:

        actor = a3c.ActorNetwork(sess,
                                 state_dim=[S_INFO, S_LEN], action_dim=A_DIM,
                                 learning_rate=ACTOR_LR_RATE)

        critic = a3c.CriticNetwork(sess,
                                   state_dim=[S_INFO, S_LEN],
                                   learning_rate=CRITIC_LR_RATE)

        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()  # save neural net parameters

        # restore neural net parameters
        nn_model = NN_MODEL
        if nn_model is not None:  # nn_model is the path to file
            saver.restore(sess, nn_model)
            print("Model restored.")

        time_stamp = 0

        last_bit_rate = DEFAULT_QUALITY
        bit_rate = DEFAULT_QUALITY

        action_vec = np.zeros(A_DIM)
        action_vec[bit_rate] = 1

        s_batch = [np.zeros((S_INFO, S_LEN))]
        a_batch = [action_vec]
        r_batch = []
        entropy_record = []

        video_count = 0

        while True:  # serve video forever
            # the action is from the last decision
            # this is to make the framework similar to the real
            delay, sleep_time, buffer_size, rebuf, \
            video_chunk_size, next_video_chunk_sizes, \
            end_of_video, video_chunk_remain, future_chunk_weight, do_rebuffer = \
                net_env.get_video_chunk(bit_rate)

            time_stamp += delay  # in ms
            time_stamp += sleep_time  # in ms

            # sensei reward; includes future chunk weights
            if TEST == 'sensei':
                current_weight = CHUNK_QOE[int(CHUNK_TIL_VIDEO_END_CAP - video_chunk_remain - 1)]
                reward = (VIDEO_BIT_RATE[bit_rate] / M_IN_K - REBUF_PENALTY * rebuf - SMOOTH_PENALTY * np.abs(
                    VIDEO_BIT_RATE[bit_rate] - VIDEO_BIT_RATE[
                        last_bit_rate]) / M_IN_K - future_chunk_weight * QOE_PENALTY) * current_weight

            # pensieve linear reward
            else:
                # reward is video quality - rebuffer penalty - smoothness
                reward = VIDEO_BIT_RATE[bit_rate] / M_IN_K \
                         - REBUF_PENALTY * rebuf \
                         - SMOOTH_PENALTY * np.abs(VIDEO_BIT_RATE[bit_rate] -
                                                   VIDEO_BIT_RATE[last_bit_rate]) / M_IN_K

            last_bit_rate = bit_rate

            # log time_stamp, bit_rate, buffer_size, reward, do_rebuffer
            log_file.write(str(time_stamp / M_IN_K) + '\t' +
                           str(VIDEO_BIT_RATE[bit_rate]) + '\t' +
                           str(buffer_size) + '\t' +
                           str(rebuf) + '\t' +
                           str(video_chunk_size) + '\t' +
                           str(delay) + '\t' +
                           str(reward) + '\t' +
                           str(do_rebuffer) + '\n')
            log_file.flush()
            # print(rebuf)
            # retrieve previous state
            if len(s_batch) == 0:
                state = [np.zeros((S_INFO, S_LEN))]
            else:
                state = np.array(s_batch[-1], copy=True)

            # dequeue history record
            state = np.roll(state, -1, axis=1)
            if do_rebuffer > 0 and TEST == 'sensei':
                state[1, -1] += 1000  # len of chunk in milliseconds
                state[6, -1] = 1
                continue
            else:
                r_batch.append(reward)

                # this should be S_INFO number of terms
                state[0, -1] = VIDEO_BIT_RATE[bit_rate] / float(np.max(VIDEO_BIT_RATE))  # last quality
                state[1, -1] = buffer_size / BUFFER_NORM_FACTOR  # 10 sec
                state[2, -1] = float(video_chunk_size) / float(delay) / M_IN_K  # kilo byte / ms
                state[3, -1] = float(delay) / M_IN_K / BUFFER_NORM_FACTOR  # 10 sec
                state[4, :A_DIM] = np.array(next_video_chunk_sizes) / M_IN_K / M_IN_K  # mega byte
                state[5, -1] = np.minimum(video_chunk_remain, CHUNK_TIL_VIDEO_END_CAP) / float(
                    CHUNK_TIL_VIDEO_END_CAP)
                state[6, -1] = 0  # buffer change

            action_prob = actor.predict(np.reshape(state, (1, S_INFO, S_LEN)))
            action_cumsum = np.cumsum(action_prob)
            bit_rate = (action_cumsum > np.random.randint(1, RAND_RANGE) / float(RAND_RANGE)).argmax()
            # Note: we need to discretize the probability into 1/RAND_RANGE steps,
            # because there is an intrinsic discrepancy in passing single state and batch states

            s_batch.append(state)

            entropy_record.append(a3c.compute_entropy(action_prob[0]))

            if end_of_video:
                log_file.write('\n')
                log_file.close()

                last_bit_rate = DEFAULT_QUALITY
                bit_rate = DEFAULT_QUALITY  # use the default action here

                del s_batch[:]
                del a_batch[:]
                del r_batch[:]

                action_vec = np.zeros(A_DIM)
                action_vec[bit_rate] = 1

                s_batch.append(np.zeros((S_INFO, S_LEN)))
                a_batch.append(action_vec)
                entropy_record = []

                print("trace num", video_count + 1)
                video_count += 1

                if video_count >= len(all_file_names):
                    break

                log_path = LOG_FILE + '_' + all_file_names[net_env.trace_idx]
                log_file = open(log_path, 'w')


if __name__ == '__main__':
    main()
