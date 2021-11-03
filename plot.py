import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from uma import *

status = ステータス(
    スピード=900.0,
    スタミナ=650.0,
    パワー=800.0,
    根性=350.0,
    賢さ=400.0,
    脚質=差し,
    脚質適性=A,
    距離適性=A,
    バ場適性=A,
)
yaruki = 絶好調
kaifuku = 回復スキル累計(金=1, 白=0, 下位固有=0, 八方にらみ=0, 焦り=0)
skills = [
    スキル(
        名前='レッツ・アナボリック！',
        発動位置=2000.0/3.0,
        基礎持続時間=2.4,
        種類='加速度アップ',
        補正量=0.2,
    ),
    スキル(
        名前='差し切り体制',
        発動位置=2000.0/3.0,
        基礎持続時間=1.8,
        種類='加速度アップ',
        補正量=0.2,
    )
]

# ペースメーカーとしてスキルなしの差しアグネスタキオンを想定(中距離S)
# 評価値は8191, 不調のとき残りHPが0.04となる。
pacemaker_status = ステータス(
    スピード=1050.0,
    スタミナ=675.0,
    パワー=1040.0,
    根性=350.0,
    賢さ=345.0,
    脚質=差し,
    脚質適性=A,
    距離適性=S,
    バ場適性=A,
)
pacemaker_yaruki = 絶好調
pacemaker_kaifuku = 回復スキル累計(金=1, 白=0, 下位固有=0, 八方にらみ=0, 焦り=0)

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
    ],
    最終直線位置=525.0,
    最終コーナー位置=750.0,
)

result = simulate(status, tokyo, yaruki, kaifuku, skills)
pacemaker_result = simulate(pacemaker_status, tokyo, pacemaker_yaruki, pacemaker_kaifuku, [])

log(result.最終コーナー突入F / FPS, "最終コーナー突入[秒]")
log(result.フェーズ境界[1] / FPS, "ラストスパート開始[秒]")
log(result.最終直線突入F / FPS, "最終直線突入[秒]")
log(result.ラストスパート加速完了F / FPS, "ラストスパート加速完了[秒]")
log(result.残り200m通過F / FPS, "残り200m通過[秒]")

t = np.arange(len(result.残り距離)) / FPS
dist = np.array(result.残り距離)
hp = np.array(result.残りHP)
vel = np.array(result.速度)
acc = np.array(result.加速度)

log(pacemaker_result.残りHP[-1], "ペースメーカー残りHP")
log(len(pacemaker_result.残りHP) / FPS, "ペースメーカータイム[秒]")
pacemaker_dist = np.array(pacemaker_result.残り距離)
if len(pacemaker_dist) < len(dist):
    pacemaker_dist = np.concatenate((pacemaker_dist, np.zeros(len(dist) - len(pacemaker_dist))))
if len(pacemaker_dist) > len(dist):
    pacemaker_dist = pacemaker_dist[:len(dist)]

plt.style.use('seaborn-dark')
plt.rcParams['font.family'] = "Noto Sans JP"

fig = plt.figure(figsize=(10, 9), dpi=100)

suptitle = '\n'.join([
    '{}/{}/{}/{}/{} {}/{}/{}/{} ({}) スキル回復{}%'.format(
        int(status.スピード), int(status.スタミナ), int(status.パワー), int(status.根性), int(status.賢さ),
        status.脚質, status.脚質適性, status.距離適性, status.バ場適性, yaruki, kaifuku,
    ),
    '{}m {} {}'.format(tokyo.距離, tokyo.バ場種類, tokyo.バ場状態),
    'タイム={:.2f}秒, 残りHP={:.0f}'.format(t[-1], hp[-1]),
])
fig.suptitle(suptitle, fontsize=10)

ax_dist = fig.add_subplot(5, 1, 1)
ax_dist.set_title("残り距離[m]", fontsize=8)
ax_dist.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(400))

ax_diff = fig.add_subplot(5, 1, 2)
ax_diff.set_title("ペースメーカーとの相対位置[m]", fontsize=8)
ax_diff.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1.5))

ax_vel = fig.add_subplot(5, 1, 3)
ax_vel.set_title("速度－基準速度[m/s]  (基準速度={}m/s)".format(基準速度(tokyo)), fontsize=8)
ax_vel.set_ylim(-1.5, 5.0)
ax_vel.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))

ax_acc = fig.add_subplot(5, 1, 4)
ax_acc.set_title("加速度[m/s^2]", fontsize=8)
ax_acc.set_ylim(0.0, 1.0)
ax_acc.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2))

ax_hp = fig.add_subplot(5, 1, 5)
ax_hp.set_title("残りHP", fontsize=8)
ax_hp.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

for ax in [ax_diff, ax_dist, ax_hp, ax_vel, ax_acc]:
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.grid(which='major', axis='x')
    ax.grid(which='major', axis='y')
    ax.axvline(x=result.最終コーナー突入F / FPS, c='tomato', linestyle=':')
    ax.axvline(x=result.最終直線突入F / FPS, c='tomato', linestyle=':')
    ax.axvline(x=result.残り200m通過F / FPS, c='tomato', linestyle=':')
    for frame in result.フェーズ境界:
        ax.axvline(x=frame / FPS, c='plum', linestyle='-')

fig.tight_layout()

ax_diff.plot(t, pacemaker_dist - dist)
ax_hp.plot(t, hp)
ax_vel.plot(t, vel - 基準速度(tokyo))
ax_acc.plot(t, acc)
ax_dist.plot(t, dist)

fig.savefig('out/fig.png')
