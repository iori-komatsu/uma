import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from uma import *

status = ステータス(
    スピード=1000.0,
    スタミナ=900.0,
    パワー=800.0,
    根性=350.0,
    賢さ=500.0,
    脚質=先行,
    脚質適性=A,
    距離適性=A,
    バ場適性=A,
)
tokyo = コース(距離=2000, バ場種類='芝', バ場状態='重')
yaruki = 絶好調

result = simulate(status, tokyo, yaruki)

dist = np.array(result.残り距離)
hp = np.array(result.残りHP)
vel = np.array(result.速度)
acc = np.array(result.加速度)

plt.style.use('seaborn-dark')
plt.rcParams['font.family'] = "Noto Sans JP"

fig = plt.figure(figsize=(5, 7), dpi=100)

suptitle = '{}/{}/{}/{}/{} {}/{}/{}/{} ({})\n'.format(
    int(status.スピード), int(status.スタミナ), int(status.パワー), int(status.根性), int(status.賢さ),
    status.脚質, status.脚質適性, status.距離適性, status.バ場適性, yaruki,
) + '{}m {} {}'.format(tokyo.距離, tokyo.バ場種類, tokyo.バ場状態)
fig.suptitle(suptitle, fontsize=10)

ax_dist = fig.add_subplot(4, 1, 1)
ax_dist.set_title("距離[m]", fontsize=8)
ax_dist.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2000.0 / 3.0))

ax_hp = fig.add_subplot(4, 1, 2)
ax_hp.set_title("HP", fontsize=8)
ax_hp.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

ax_vel = fig.add_subplot(4, 1, 3)
ax_vel.set_title("速度[m/s]", fontsize=8)
ax_vel.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))

ax_acc = fig.add_subplot(4, 1, 4)
ax_acc.set_title("加速度[m/s^2]", fontsize=8)
ax_acc.set_ylim(0.35, 0.45)
ax_acc.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.025))

for ax in [ax_dist, ax_hp, ax_vel, ax_acc]:
    ax.set_xticks(result.フェーズ境界)
    ax.grid(which='major', axis='x')
    ax.grid(which='major', axis='y')


fig.tight_layout()

ax_dist.plot(dist)

ax_hp.plot(hp)

ax_vel.plot(vel)

ax_acc.plot(acc)

fig.savefig('out/fig.png')
