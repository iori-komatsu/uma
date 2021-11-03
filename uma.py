from typing import NamedTuple, List
import math

A='A'
B='B'
C='C'
D='D'
E='E'
F='F'
G='G'
逃げ='逃げ'
先行='先行'
差し='差し'
追込='追込'
絶好調='絶好調'
好調='好調'
普通='普通'
不調='不調'
絶不調='絶不調'

def log(x, prefix):
    print("{} = {:.1f}".format(prefix, x))
    return x

class ステータス(NamedTuple):
    スピード: float
    スタミナ: float
    パワー: float
    根性: float
    賢さ: float

    脚質: str
    脚質適性: str
    距離適性: str
    バ場適性: str

class ウマ状態(NamedTuple):
    掛かり: bool
    ペースダウン: bool
    下り坂加速: bool

class 状態(NamedTuple):
    現在速度: float
    残りHP: float
    残り距離: float
    ウマ状態: ウマ状態

class 高低(NamedTuple):
    位置: float
    高さ: float

class コース(NamedTuple):
    距離: float
    バ場種類: str
    バ場状態: str
    アップダウン: List[高低]
    最終直線位置: float
    最終コーナー位置: float

def フェーズ(状態: 状態, コース: コース):
    r = 6.0 * 状態.残り距離 / コース.距離
    if r <= 1.0: # 0-1
        return 3
    if r <= 2.0: # 1-2
        return 2
    if r <= 5.0: # 2-5
        return 1
    return 0 # 5-6

def ステータス補正(生ステータス: ステータス, やる気: str, コース: コース) -> ステータス:
    やる気係数 = {
        '絶好調': 1.04,
        '好調': 1.02,
        '普通': 1.0,
        '不調': 0.98,
        '絶不調': 0.96,
    }[やる気]
    コース係数 = 1.0 # TODO
    バ場補正_スピード = {
        '不良': -50,
        '重': 0,
        '稍重': 0,
        '良': 0,
    }[コース.バ場状態]
    バ場補正_パワー = {
        '不良': -50,
        '重': -50,
        '稍重': -50,
        '良': 0,
    }[コース.バ場状態]
    脚質補正 = {
        'S': 1.1,
        'A': 1.0,
        'B': 0.85,
        'C': 0.75,
        'D': 0.6,
        'E': 0.4,
        'F': 0.2,
        'G': 0.1,
    }[生ステータス.脚質適性]
    return ステータス(
        スピード=生ステータス.スピード * やる気係数 * コース係数 + バ場補正_スピード,
        スタミナ=生ステータス.スタミナ * やる気係数,
        パワー=生ステータス.パワー * やる気係数 + バ場補正_パワー,
        根性=生ステータス.根性 * やる気係数,
        賢さ=生ステータス.賢さ * やる気係数 * 脚質補正,

        脚質=生ステータス.脚質,
        脚質適性=生ステータス.脚質適性,
        距離適性=生ステータス.距離適性,
        バ場適性=生ステータス.バ場適性,
    )

def 初期HP(補正ステータス: ステータス, コース: コース) -> float:
    脚質係数 = {
        '逃げ': 0.95,
        '先行': 0.89,
        '差し': 1.0,
        '追込': 0.995,
    }[補正ステータス.脚質]
    return 0.8 * 脚質係数 * 補正ステータス.スタミナ + コース.距離

def ウマ状態係数(状態: 状態) -> float:
    k = 1.0
    if 状態.ウマ状態.掛かり: k *= 1.6
    if 状態.ウマ状態.ペースダウン: k *= 0.6
    if 状態.ウマ状態.下り坂加速: k *= 0.4
    return k

def 秒間体力消費_基本(状態: 状態, コース: コース) -> float:
    バ場状態係数 = {
        '芝': {
            '不良': 1.02,
            '重': 1.02,
            '稍重': 1,
            '良': 1,
        },
        'ダート': {
            '不良': 1.02,
            '重': 1.01,
            '稍重': 1,
            '良': 1,
        },
    }[コース.バ場種類][コース.バ場状態]
    return 20.0 * ウマ状態係数(状態) * (状態.現在速度 - 基準速度(コース) + 12.0)**2 / 144.0 * バ場状態係数

def 秒間体力消費(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    ret = 秒間体力消費_基本(状態, コース)
    if フェーズ(状態, コース) >= 2:
        ret *= 200.0 / math.sqrt(600.0 * 補正ステータス.根性) + 1.0
    return ret

def 基準速度(コース: コース) -> float:
    return 20.0 - (コース.距離 - 2000) / 1000

def 賢さ乱数_期待値(補正賢さ: float) -> float:
    上限 = (補正賢さ / 5500) * math.log10(補正賢さ * 0.1)
    下限 = 上限 - 0.65
    return (上限 + 下限) / 2.0 / 100.0

def 目標速度スピード加算(補正ステータス: ステータス):
    距離適性係数 = {
        'S': 1.05,
        'A': 1.0,
        'B': 0.9,
        'C': 0.8,
        'D': 0.6,
        'E': 0.4,
        'F': 0.2,
        'G': 0.1,
    }[補正ステータス.距離適性]
    return math.sqrt(500.0 * 補正ステータス.スピード) * 距離適性係数 * 0.002

def 基準目標速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    脚質係数 = {
        '逃げ': [1.0,   0.98,  0.962, 0.962],
        '先行': [0.978, 0.991, 0.975, 0.975],
        '差し': [0.938, 0.998, 0.994, 0.994],
        '追込': [0.931, 1.0,   1.0,   1.0],
    }[補正ステータス.脚質][フェーズ(状態, コース)]
    ret = 基準速度(コース) * 脚質係数 + (賢さ乱数_期待値(補正ステータス.賢さ) * 基準速度(コース))
    if フェーズ(状態, コース) >= 2:
        ret += 目標速度スピード加算(補正ステータス)
    return ret

def 坂角度_tan(状態: 状態, コース: コース) -> float:
    for i, curr in enumerate(コース.アップダウン):
        if curr.位置 <= 状態.残り距離:
            if i == 0:
                return 0.0
            prev = コース.アップダウン[i-1]
            x_diff = prev.位置 - curr.位置
            y_diff = curr.高さ - prev.高さ
            return y_diff / x_diff
    return 0.0

def 目標速度_坂補正(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    tangent = 坂角度_tan(状態, コース)
    angle = math.atan(tangent) * 180.0 / math.pi 
    slope = tangent * 100.0
    if slope >= 1.0:
        # 上り坂
        return -abs(100 * math.tan(angle * 0.017453)) * 200 / 補正ステータス.パワー
    elif slope <= -1.0:
        # 下り坂
        # 実際には確率で下り坂加速モードに入っている場合にのみ加算されるが、この実装では常に加算している
        # 後で直す
        return 0.3 + abs(math.tan(angle) * 0.017453) / 10.0
    else:
        return 0.0

def 目標速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    # 実際にはポジションキープや移動補正などに影響されるが、未実装
    return 基準目標速度(状態, コース, 補正ステータス) + 目標速度_坂補正(状態, コース, 補正ステータス)

def 加速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    脚質係数 = {
        '逃げ': [1.0,   1.0, 0.996, 0.996],
        '先行': [0.985, 1.0, 0.996, 0.996],
        '差し': [0.975, 1.0, 1.0,   1.0],
        '追込': [0.945, 1.0, 0.997, 0.997],
    }[補正ステータス.脚質][フェーズ(状態, コース)]
    バ場適性係数 = {
        'S': 1.05,
        'A': 1.0,
        'B': 0.9,
        'C': 0.8,
        'D': 0.6,
        'E': 0.4,
        'F': 0.2,
        'G': 0.1,
    }[補正ステータス.バ場適性]
    距離適性係数 = {
        'S': 1.0,
        'A': 1.0,
        'B': 1.0,
        'C': 1.0,
        'D': 1.0,
        'E': 0.6,
        'F': 0.5,
        'G': 0.4,
    }[補正ステータス.距離適性]

    tangent = 坂角度_tan(状態, コース)
    slope = tangent * 100.0
    if slope >= 1.0:
        # 上り坂
        係数 = 0.0004
    else:
        係数 = 0.0006

    return 係数 * math.sqrt(500.0 * 補正ステータス.パワー) * 脚質係数 * バ場適性係数 * 距離適性係数

def 減速時加速度(状態: 状態, コース: コース) -> float:
    return [-1.2, -0.8, -1.0, -1.0][フェーズ(状態, コース)]

def スタートダッシュ加速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    return 加速度(状態, コース, 補正ステータス) + 24.0

def スタートダッシュ制限速度(コース: コース) -> float:
    return 基準速度(コース) * 0.85

def 最低速度(コース: コース, 補正ステータス: ステータス) -> float:
    return 基準速度(コース) * 0.85 + math.sqrt(200.0 * 補正ステータス.根性) * 0.001

def ラストスパート基準目標速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    return (基準目標速度(状態, コース, 補正ステータス) + 0.01 * 基準速度(コース)) * 1.05 + 目標速度スピード加算(補正ステータス)

def ラストスパート目標速度(状態: 状態, コース: コース, 補正ステータス: ステータス) -> float:
    return ラストスパート基準目標速度(状態, コース, 補正ステータス) + 目標速度_坂補正(状態, コース, 補正ステータス)

def 回復スキル回復量(回復量pct: float, コース: コース, 補正ステータス: ステータス) -> float:
    return 初期HP(補正ステータス, コース) * 回復量pct / 100.0

def 回復スキル累計(金: int, 白: int, 下位固有: int, 八方にらみ: int, 焦り: int) -> float:
    return 金 * 5.5 + 白 * 1.5 + 下位固有 * 3.5 - 八方にらみ * 3.0 - 焦り * 1.0

################################################################################

FPS = 15.0

def next_velocity(curr_vel: float, curr_acc: float, target_vel: float) -> float:
    '''次のフレームの速度を返す'''
    # [s] = [15f]
    # [m/s^2] -> [m/f^2]
    a = curr_acc / (FPS * FPS)
    # [m/s] -> [m/f]
    v = curr_vel / FPS
    # [m/f] -> [m/s]
    next_vel = (v+a) * FPS
    if a >= 0:
        return min(next_vel, target_vel)
    else:
        return max(next_vel, target_vel)

class SimulationResult(NamedTuple):
    残り距離: List[float]
    残りHP: List[float]
    速度: List[float]
    加速度: List[float]
    フェーズ境界: List[int]
    最終直線突入F: int
    最終コーナー突入F: int

def simulate(生ステータス: ステータス, コース: コース, やる気: str, 回復スキル回復量pct: float):
    status = ステータス補正(生ステータス, やる気, コース)
    state = 状態(
        現在速度=3.0,
        # 回復スキルによる回復は一番最初から入れておく
        残りHP=log(初期HP(status, コース), "初期HP") + log(回復スキル回復量(回復スキル回復量pct, コース, status), "回復スキル回復量"),
        残り距離=コース.距離,
        ウマ状態=ウマ状態(掛かり=False, ペースダウン=False, 下り坂加速=False),
    )

    result = SimulationResult(
        残り距離=[],
        残りHP=[],
        速度=[],
        加速度=[],
        フェーズ境界=[],
        最終直線突入F=-1,
        最終コーナー突入F=-1,
    )

    frame = 0
    last_phase = 0

    while state.残り距離 > 0.0:
        phase = フェーズ(state, コース)
        if phase >= 2:
            # ラストスパート
            # スタミナが足りる場合だけを実装する
            a = 加速度(state, コース, status)
            v_min = 最低速度(コース, status)
            v_max = 1e8
            target_vel = ラストスパート目標速度(state, コース, status)
        elif frame < 8:
            # スタートダッシュ
            a = スタートダッシュ加速度(state, コース, status)
            v_min = 0.0
            v_max = スタートダッシュ制限速度(コース)
            target_vel = 目標速度(state, コース, status)
        else:
            a = 加速度(state, コース, status)
            v_min = 最低速度(コース, status)
            v_max = 1e8
            target_vel = 目標速度(state, コース, status)

        if target_vel < state.現在速度:
            # 減速する
            a = 減速時加速度(state, コース)

        next_v = next_velocity(state.現在速度, a, target_vel)
        next_v = max(next_v, v_min)
        next_v = min(next_v, v_max)

        state = state._replace(
            現在速度=next_v,
            残りHP=state.残りHP - 秒間体力消費(state, コース, status) / FPS,
            残り距離=state.残り距離 - next_v / FPS,
        )

        result.残り距離.append(state.残り距離)
        result.残りHP.append(state.残りHP)
        result.速度.append(state.現在速度)
        result.加速度.append(a)
        if phase != last_phase:
            result.フェーズ境界.append(frame)
        if result.最終直線突入F == -1 and state.残り距離 <= コース.最終直線位置:
            result = result._replace(最終直線突入F=frame)
        if result.最終コーナー突入F == -1 and state.残り距離 <= コース.最終コーナー位置:
            result = result._replace(最終コーナー突入F=frame)

        frame += 1
        last_phase = phase

    return result
