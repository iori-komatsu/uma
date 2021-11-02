from uma import *

status = ステータス(
    スピード=1000.0,
    スタミナ=600.0,
    パワー=800.0,
    根性=350.0,
    賢さ=500.0,
    脚質=差し,
    脚質適性=A,
    距離適性=A,
    バ場適性=A,
)
tokyo = コース(距離=2000, バ場種類='芝', バ場状態='重')
modified_status = ステータス補正(status, 普通, tokyo)

state = 状態(
    現在速度=10,
    残りHP=初期HP(modified_status, tokyo),
    フェーズ=0,
    ウマ状態=ウマ状態(掛かり=False, ペースダウン=False, 下り坂加速=False),
    ラストスパート基準速度=None,
    ラストスパート開始位置=None,
)
