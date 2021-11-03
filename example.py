import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from uma import *

status = ステータス(
    スピード=1200.0,
    スタミナ=900.0,
    パワー=1200.0,
    根性=350.0,
    賢さ=1200.0,
    脚質=先行,
    脚質適性=A,
    距離適性=A,
    バ場適性=A,
)
tokyo = コース(
    距離=2000, バ場種類='芝', バ場状態='重',
    アップダウン=[
        高低(2000, 0),
        高低(1900, 0),
        高低(1290, -1.90),
        高低(1200, -0.20),
        高低(1120, -0.20),
        高低(890,  -2.9),
        高低(440,  -2.0),
        高低(300,  0),
        高低(0,    0),
    ])
yaruki = 絶好調
kaifuku = 5.5 # マエストロ

result = simulate(status, tokyo, yaruki, kaifuku)

t = np.arange(len(result.残り距離)) / FPS
dist = np.array(result.残り距離)
hp = np.array(result.残りHP)
vel = np.array(result.速度)
acc = np.array(result.加速度)

plt.style.use('seaborn-dark')
plt.rcParams['font.family'] = "Noto Sans JP"

fig = plt.figure(figsize=(8, 7), dpi=100)

suptitle = '\n'.join([
    '{}/{}/{}/{}/{} {}/{}/{}/{} ({})'.format(
        int(status.スピード), int(status.スタミナ), int(status.パワー), int(status.根性), int(status.賢さ),
        status.脚質, status.脚質適性, status.距離適性, status.バ場適性, yaruki,
    ),
    '{}m {} {}'.format(tokyo.距離, tokyo.バ場種類, tokyo.バ場状態),
    'タイム={:.2f}秒, 残りHP={:.0f}'.format(t[-1], hp[-1]),
])
fig.suptitle(suptitle, fontsize=10)

ax_dist = fig.add_subplot(4, 1, 1)
ax_dist.set_title("残り距離[m]", fontsize=8)
ax_dist.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(400))

ax_hp = fig.add_subplot(4, 1, 2)
ax_hp.set_title("残りHP", fontsize=8)
ax_hp.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

ax_vel = fig.add_subplot(4, 1, 3)
ax_vel.set_title("速度－基準速度[m/s]  (基準速度={}m/s)".format(基準速度(tokyo)), fontsize=8)
ax_vel.set_ylim(-1.0, 5.0)
ax_vel.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))

ax_acc = fig.add_subplot(4, 1, 4)
ax_acc.set_title("加速度[m/s^2]", fontsize=8)
ax_acc.set_ylim(0.0, 0.50)
ax_acc.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.1))

for ax in [ax_dist, ax_hp, ax_vel, ax_acc]:
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(matplotlib.ticker.FixedLocator(np.array(result.フェーズ境界) / FPS))
    ax.grid(which='major', axis='x')
    ax.grid(which='minor', axis='x', linestyle='--')
    ax.grid(which='major', axis='y')

fig.tight_layout()

ax_dist.plot(t, dist)

ax_hp.plot(t, hp)

ax_vel.plot(t, vel - 基準速度(tokyo))

ax_acc.plot(t, acc)

fig.savefig('out/fig.png')
