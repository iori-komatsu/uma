import numpy as np
import matplotlib.pyplot as plt
from uma import *

status = ステータス(
    スピード=1000.0,
    スタミナ=900.0,
    パワー=800.0,
    根性=350.0,
    賢さ=500.0,
    脚質=差し,
    脚質適性=A,
    距離適性=A,
    バ場適性=A,
)
tokyo = コース(距離=2000, バ場種類='芝', バ場状態='重')

result = simulate(status, tokyo, 普通)

dist = np.array(result.残り距離)
hp = np.array(result.残りHP)
vel = np.array(result.速度)
acc = np.array(result.加速度)

fig, axes = plt.subplots(4, 1)
axes[0].plot(dist)
axes[1].plot(hp)
axes[2].plot(vel)
axes[3].plot(acc)
fig.savefig('out/fig.png')
