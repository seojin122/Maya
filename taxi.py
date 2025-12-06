import maya.cmds as cmds

# 새 씬
cmds.file(new=True, force=True)

# 타임라인 설정
cmds.playbackOptions(min=1, max=240)
cmds.currentTime(1)

# -----------------------------
# 1. 드론 택시 모델
# -----------------------------
def create_rotor(name):
    grp = cmds.group(em=True, name=name + "_grp")
    ring, _ = cmds.polyTorus(r=0.7, sr=0.12, name=name + "_ring_geo")
    blade_a, _ = cmds.polyCube(w=1.2, h=0.08, d=0.18, name=name + "_bladeA_geo")
    blade_b = cmds.duplicate(blade_a, name=name + "_bladeB_geo")[0]
    cmds.rotate(0, 90, 0, blade_b, r=True)
    cmds.parent(ring, blade_a, blade_b, grp)
    return grp


def create_flying_taxi():
    taxi_grp = cmds.group(em=True, name="flyingTaxi_grp")

    # 차체
    body, _ = cmds.polyCube(w=4.5, h=1.0, d=2.2, name="taxiBody_geo")
    cmds.scale(1.0, 0.9, 1.0, body)
    cmds.move(0, 1.0, 0, body)
    cmds.parent(body, taxi_grp)

    # 지붕
    roof, _ = cmds.polySphere(r=1.2, name="taxiRoof_geo")
    cmds.scale(1.6, 0.9, 1.4, roof)
    cmds.move(0.3, 1.6, 0, roof)
    cmds.parent(roof, taxi_grp)

    # 앞 유리
    glass, _ = cmds.polySphere(r=1.25, name="taxiGlass_geo")
    cmds.scale(1.5, 0.8, 1.4, glass)
    cmds.move(1.7, 1.45, 0, glass)
    cmds.parent(glass, taxi_grp)

    # 헤드라이트
    light_L, _ = cmds.polySphere(r=0.18, name="headLight_L_geo")
    cmds.move(2.3, 0.9, 0.5, light_L)
    cmds.parent(light_L, taxi_grp)
    light_R = cmds.duplicate(light_L, name="headLight_R_geo")[0]
    cmds.move(2.3, 0.9, -0.5, light_R)
    cmds.parent(light_R, taxi_grp)

    # 암
    arm_FL, _ = cmds.polyCylinder(r=0.08, h=2.0, name="arm_FL_geo")
    cmds.rotate(0, 0, 90, arm_FL)
    cmds.move(0.5, 1.2, 1.4, arm_FL)
    cmds.parent(arm_FL, taxi_grp)

    arm_FR = cmds.duplicate(arm_FL, name="arm_FR_geo")[0]
    cmds.move(0.5, 1.2, -1.4, arm_FR)
    cmds.parent(arm_FR, taxi_grp)

    arm_RL = cmds.duplicate(arm_FL, name="arm_RL_geo")[0]
    cmds.move(-1.8, 1.2, 1.4, arm_RL)
    cmds.parent(arm_RL, taxi_grp)

    arm_RR = cmds.duplicate(arm_FL, name="arm_RR_geo")[0]
    cmds.move(-1.8, 1.2, -1.4, arm_RR)
    cmds.parent(arm_RR, taxi_grp)

    # 프로펠러 4개
    rotor_FL = create_rotor("rotor_FL")
    cmds.move(1.6, 1.2, 2.2, rotor_FL)
    cmds.parent(rotor_FL, taxi_grp)

    rotor_FR = create_rotor("rotor_FR")
    cmds.move(1.6, 1.2, -2.2, rotor_FR)
    cmds.parent(rotor_FR, taxi_grp)

    rotor_RL = create_rotor("rotor_RL")
    cmds.move(-2.9, 1.2, 2.2, rotor_RL)
    cmds.parent(rotor_RL, taxi_grp)

    rotor_RR = create_rotor("rotor_RR")
    cmds.move(-2.9, 1.2, -2.2, rotor_RR)
    cmds.parent(rotor_RR, taxi_grp)

    # 재질
    body_mat = cmds.shadingNode("blinn", asShader=True, name="taxiBody_mat")
    cmds.setAttr(body_mat + ".color", 0.9, 0.9, 1.0, type="double3")
    cmds.setAttr(body_mat + ".specularColor", 0.9, 0.9, 0.9, type="double3")

    glass_mat = cmds.shadingNode("blinn", asShader=True, name="taxiGlass_mat")
    cmds.setAttr(glass_mat + ".color", 0.2, 0.3, 0.5, type="double3")
    cmds.setAttr(glass_mat + ".transparency", 0.7, 0.7, 0.75, type="double3")

    light_mat = cmds.shadingNode("lambert", asShader=True, name="light_mat")
    cmds.setAttr(light_mat + ".color", 1.0, 1.0, 0.9, type="double3")

    cmds.select(body, roof); cmds.hyperShade(assign=body_mat)
    cmds.select(glass); cmds.hyperShade(assign=glass_mat)
    cmds.select(light_L, light_R); cmds.hyperShade(assign=light_mat)

    # 프로펠러 회전
    expr = """
rotor_FL_grp.rotateY = time * 60;
rotor_FR_grp.rotateY = time * 60;
rotor_RL_grp.rotateY = time * 60;
rotor_RR_grp.rotateY = time * 60;
"""
    cmds.expression(s=expr, name="rotorSpin_expr")

    return taxi_grp


# -----------------------------
# 2. 애니메이션
# -----------------------------
def animate_taxi(taxi_grp):
    cmds.cutKey(taxi_grp, time=(1,240))  # 혹시 이전 키 있으면 삭제

    cmds.currentTime(1)
    cmds.setKeyframe(taxi_grp, at="translateX", v=-15)
    cmds.setKeyframe(taxi_grp, at="translateY", v=8)
    cmds.setKeyframe(taxi_grp, at="translateZ", v=-5)
    cmds.setKeyframe(taxi_grp, at="rotateY", v=15)

    cmds.currentTime(100)
    cmds.setKeyframe(taxi_grp, at="translateX", v=0)
    cmds.setKeyframe(taxi_grp, at="translateY", v=12)
    cmds.setKeyframe(taxi_grp, at="translateZ", v=0)
    cmds.setKeyframe(taxi_grp, at="rotateY", v=40)

    cmds.currentTime(200)
    cmds.setKeyframe(taxi_grp, at="translateX", v=15)
    cmds.setKeyframe(taxi_grp, at="translateY", v=16)
    cmds.setKeyframe(taxi_grp, at="translateZ", v=3)
    cmds.setKeyframe(taxi_grp, at="rotateY", v=70)

    cmds.selectKey(taxi_grp)
    cmds.keyTangent(itt="spline", ott="spline")


# -----------------------------
# 실행 부분
# -----------------------------
taxi = create_flying_taxi()
animate_taxi(taxi)

# 카메라 세팅 + 현재 뷰에 적용
cam, camShape = cmds.camera(name="taxiCam")
cmds.move(-5, 12, 25, cam)
cmds.rotate(-18, -20, 0, cam)
panel = cmds.getPanel(withFocus=True)
cmds.lookThru(panel, cam)

# 타임라인을 자동 재생해 보기 (멈추고 싶으면 GUI에서 Stop)
cmds.currentTime(1)
cmds.play(state=True)
