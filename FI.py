import maya.cmds as cmds
import math

#  Keyframe Utility
def key(obj, attr, value, frame, offset=0):
    """Shortcut wrapper for setKeyframe"""
    cmds.setKeyframe(obj, at=attr, t=frame + offset, v=value)


#  HoverCar 생성 함수
def create_hovercar_v9_1(name="HoverCar"):
    """호버카 모델을 생성하고 재질을 적용하여 하나의 그룹으로 반환"""

    # 중복 방지
    if cmds.objExists(name):
        cmds.delete(name)

    root = cmds.group(em=True, name=name)

    # Body
    body, _ = cmds.polySphere(r=1.0, sx=40, sy=20, name=name + "_Body")
    cmds.scale(2.2, 0.55, 1.2, body)
    cmds.move(0, 1.2, 0)
    cmds.polySmooth(body, mth=0, dv=1)
    cmds.parent(body, root)

    # Seat
    seat, _ = cmds.polyCube(w=0.8, h=0.2, d=0.8, name=name + "_Seat")
    cmds.move(-0.2, 1.2, 0)
    cmds.rotate(0, -90, 0, seat)
    cmds.parent(seat, root)

    # Backrest
    back, _ = cmds.polyCube(w=0.8, h=0.45, d=0.15, name=name + "_Backrest")
    cmds.move(-0.6, 1.45, 0)
    cmds.rotate(0, -90, 0, back)
    cmds.parent(back, root)

    # Canopy
    canopy, _ = cmds.polyCube(w=1.0, h=0.25, d=0.5, name=name + "_Canopy")
    cmds.move(0.3, 1.55, 0)
    cmds.rotate(-10, -90, 0, canopy)
    cmds.parent(canopy, root)

    # Engines + Glow Rings
    engines = []
    glow_materials = []

    for side in (-1, 1):
        eng, _ = cmds.polySphere(r=0.5, sx=30, sy=20,
                                 name=f"{name}_Engine_{'L' if side < 0 else 'R'}")
        cmds.scale(2.2, 0.55, 0.55, eng)
        cmds.move(0.3, 1.1, side * 1.25, eng)
        cmds.parent(eng, root)

        # front ring
        ring, _ = cmds.polyTorus(r=0.52, sr=0.05,
                                 name=f"{name}_EngineFrontRing_{'L' if side < 0 else 'R'}")
        cmds.rotate(0, 90, 0, ring)
        cmds.move(1.1, 1.1, side * 1.25, ring)
        cmds.parent(ring, root)

        # glow ring (발광)
        glow_ring, _ = cmds.polyTorus(r=0.32, sr=0.06,
                                      name=f"{name}_EngineGlow_{'L' if side < 0 else 'R'}")
        cmds.rotate(0, 90, 0, glow_ring)
        cmds.move(-0.55, 1.1, side * 1.25, glow_ring)
        cmds.parent(glow_ring, root)

        engines.extend([eng, ring, glow_ring])
        glow_materials.append(glow_ring)

    # Hover Pads
    pad_positions = [
        (-0.6, 0.7, 0.6),
        (0.6, 0.7, 0.6),
        (-0.6, 0.7, -0.6),
        (0.6, 0.7, -0.6)
    ]

    pads = []
    for i, pos in enumerate(pad_positions):
        pad, _ = cmds.polyCylinder(r=0.25, h=0.12, sx=20,
                                   name=f"{name}_Pad_{i+1}")
        cmds.move(pos[0], pos[1], pos[2], pad)
        cmds.parent(pad, root)
        pads.append(pad)

    # Materials
    hull = cmds.shadingNode("blinn", asShader=True, name=name + "_Hull")
    cmds.setAttr(hull + ".color", 0.7, 0.9, 1.0, type="double3")
    cmds.setAttr(hull + ".transparency", 0.55, 0.55, 0.55, type="double3")

    glass = cmds.shadingNode("blinn", asShader=True, name=name + "_Glass")
    cmds.setAttr(glass + ".color", 0.2, 0.4, 1.0, type="double3")
    cmds.setAttr(glass + ".transparency", 0.7, 0.7, 0.7, type="double3")

    metal = cmds.shadingNode("blinn", asShader=True, name=name + "_Metal")
    cmds.setAttr(metal + ".color", 0.6, 0.6, 0.63, type="double3")

    glow = cmds.shadingNode("lambert", asShader=True, name=name + "_Glow")
    cmds.setAttr(glow + ".color", 0.1, 0.8, 1.0, type="double3")
    cmds.setAttr(glow + ".incandescence", 0.2, 0.9, 1.0, type="double3")

    # 재질 적용 함수
    def apply(mat, objs):
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat + "_SG")
        cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader")
        cmds.sets(objs, e=True, forceElement=sg)

    apply(hull, [body])
    apply(glass, [canopy])
    apply(metal, engines)
    apply(glow, pads + glow_materials)

    cmds.xform(root, centerPivots=True)

    return root, glow_materials


#  Animation Functions
# Hover + Lift Off
def animate_hover_and_liftoff(root, start=1, hoverEnd=60, liftEnd=100):
    baseY = cmds.getAttr(root + ".translateY")

    # Hover sine wave
    for f in range(start, hoverEnd + 1, 5):
        y = baseY + 0.2 * math.sin(f * 0.2)
        key(root, "translateY", y, f)

    # Lift upward
    key(root, "translateY", baseY + 1.5, liftEnd)


# Path A
def animate_uam_path_A(root, start=100, end=600, offset=0):
    key(root, "translateX", -10, start, offset)
    key(root, "translateY", 2, start, offset)
    key(root, "translateZ", -8, start, offset)

    key(root, "translateX", -2, start+200, offset)
    key(root, "translateY", 3.5, start+200, offset)
    key(root, "translateZ", -1, start+200, offset)

    key(root, "translateX", 6, start+400, offset)
    key(root, "translateY", 4.5, start+400, offset)
    key(root, "translateZ", 3, start+400, offset)

    key(root, "translateX", 10, end, offset)
    key(root, "translateY", 5, end, offset)
    key(root, "translateZ", 6, end, offset)


# Path B
def animate_uam_path_B(root, start=1, end=600, offset=0):
    key(root, "translateX", 12, start, offset)
    key(root, "translateY", 10, start, offset)
    key(root, "translateZ", 8, start, offset)

    key(root, "translateX", 6, start+200, offset)
    key(root, "translateY", 12, start+200, offset)
    key(root, "translateZ", 2, start+200, offset)

    key(root, "translateX", -2, start+400, offset)
    key(root, "translateY", 13, start+400, offset)
    key(root, "translateZ", -2, start+400, offset)

    key(root, "translateX", -10, end, offset)
    key(root, "translateY", 14, end, offset)
    key(root, "translateZ", -6, end, offset)


# Path C
def animate_uam_path_C(root, start=1, end=600, offset=0):
    key(root, "translateX", 8, start, offset)
    key(root, "translateY", 15, start, offset)
    key(root, "translateZ", -10, start, offset)

    key(root, "translateX", 4, start+150, offset)
    key(root, "translateY", 16, start+150, offset)
    key(root, "translateZ", -3, start+150, offset)

    key(root, "translateX", -1, start+350, offset)
    key(root, "translateY", 17, start+350, offset)
    key(root, "translateZ", 4, start+350, offset)

    key(root, "translateX", -8, end, offset)
    key(root, "translateY", 17, end, offset)
    key(root, "translateZ", 10, end, offset)


# Engine Glow Animation
def animate_engine_glow(glow_list, start=1, end=600, offset=0):
    """sin 기반 발광 변화"""
    for f in range(start, end+1, 40):
        glow = (math.sin((f + offset) * 0.1) + 1) * 0.3
        for g in glow_list:
            key(g, "incandescenceR", glow, f)
            key(g, "incandescenceG", glow, f)
            key(g, "incandescenceB", 1.0, f)


#  애니메이션 후처리 
def print_key_info(obj, attr):
    print("Times:", cmds.keyframe(obj, q=True, at=attr, timeChange=True))
    print("Values:", cmds.keyframe(obj, q=True, at=attr, valueChange=True))

def exaggerate_hover(root, amount=0.3, time_range=(1,60)):
    cmds.keyframe(root, edit=True, at="translateY", time=time_range,
                  relative=True, valueChange=amount)

def clean_hover_spike(root):
    cmds.cutKey(root, at="translateY", time=(50,50))

def smooth_motion_curve(obj, attr, time_range):
    cmds.keyTangent(obj, edit=True, at=attr, time=time_range,
                    inTangentType="spline", outTangentType="spline")

def slow_down_motion(obj, time_range=(1,600), scale=1.3):
    cmds.scaleKey(obj, time=time_range, timeScale=scale,
                  timePivot=time_range[0])


#  도시 환경 생성
def create_material(name, color):
    mat = cmds.shadingNode("lambert", asShader=True, name=name+"_Mat")
    cmds.setAttr(mat + ".color", color[0], color[1], color[2], type="double3")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name+"_SG")
    cmds.connectAttr(mat+".outColor", sg+".surfaceShader")
    return sg

def create_building(name, x, z, h=12, w=8, d=8):
    bld, _ = cmds.polyCube(w=w, d=d, h=h, name=name)
    cmds.move(x, h/2, z)
    cmds.sets(bld, e=True, forceElement=create_material(name, (0.82,0.88,0.96)))
    return bld

def create_tree(name, x, z):
    trunk, _ = cmds.polyCylinder(r=0.3, h=2.5, name=name+"_Trunk")
    cmds.move(x,1.25,z)
    leaves,_=cmds.polySphere(r=1.4,name=name+"_Leaves")
    cmds.move(x,3,z)
    cmds.sets(trunk, e=True, forceElement=create_material(name+"_Bark",(0.35,0.22,0.12)))
    cmds.sets(leaves, e=True, forceElement=create_material(name+"_Leaves",(0.2,0.5,0.25)))
    return cmds.group(trunk, leaves, name=name)

def create_ground(size=60):
    ground,_=cmds.polyPlane(w=size,h=size,name="Ground")
    cmds.setAttr("Ground.translateY",-0.02)
    cmds.sets(ground,e=True,forceElement=create_material("Ground",(0.65,0.68,0.72)))
    return ground

def create_city_environment():
    create_ground(60)
    create_building("Building_1",-15,12,12)
    create_building("Building_2",0,-15,10)
    for i,(x,z) in enumerate([(-8,6),(8,6),(-6,-3),(6,-3),(-3,12),(3,12)]):
        create_tree(f"Tree_{i+1}",x,z)


# -----------------------------
# 여기부터 Taxi 코드 추가
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
# 실행 영역
# -----------------------------
create_city_environment()

vehicles=[]
glow_groups=[]

for i,pos in enumerate([(0,2,0),(-6,2,-4),(6,2,4)]):
    name=f"HoverCar_{i+1}"
    root,glows=create_hovercar_v9_1(name)
    cmds.xform(root,ws=True,t=pos)
    cmds.rotate(0,(i*15)-10,0,root)
    vehicles.append(root)
    glow_groups.append(glows)

v1,v2,v3 = vehicles

animate_hover_and_liftoff(v1)
animate_uam_path_A(v1)
animate_uam_path_B(v2, offset=20)
animate_uam_path_C(v3, offset=40)

for i,glows in enumerate(glow_groups):
    animate_engine_glow(glows, offset=i*15)

# After animation: 과제에서 요구한 애니메이션 개념 적용
exaggerate_hover(v1, amount=0.25)
clean_hover_spike(v1)

smooth_motion_curve(v1,"translateX",(100,600))
smooth_motion_curve(v2,"translateX",(1,600))
smooth_motion_curve(v3,"translateZ",(1,600))

slow_down_motion(v3,(1,600),scale=1.3)

print_key_info(v1,"translateX")

# === Taxi 생성 & 애니메이션 추가 ===
taxi = create_flying_taxi()
cmds.xform(taxi, ws=True, t=(0, 10, 0))  # 도시 위쪽에 배치
animate_taxi(taxi)


# =========================================================
# (추가만) 색감 + 가로등 + 건물 조금 더
#  - 기존 코드 수정/삭제 없이, 아래만 "맨 아래"에 추가
# =========================================================
import random
random.seed(7)

def make_shader(shader_type, name):
    # 중복 이름 방지: 이미 있으면 재사용
    if cmds.objExists(name):
        return name
    return cmds.shadingNode(shader_type, asShader=True, name=name)

def make_sg(shader_name):
    sg = shader_name + "_SG"
    if cmds.objExists(sg):
        return sg
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg)
    cmds.connectAttr(shader_name + ".outColor", sg + ".surfaceShader", f=True)
    return sg

def assign(obj_list, shader_name):
    if not isinstance(obj_list, (list, tuple)):
        obj_list = [obj_list]
    sg = make_sg(shader_name)
    cmds.sets(obj_list, e=True, forceElement=sg)

def add_road_and_sidewalk():
    extra = cmds.group(em=True, name="CityExtra_grp")

    # 도로(바닥 위에 얇게)
    road, _ = cmds.polyPlane(w=48, h=12, name="ExtraRoad_geo")
    cmds.setAttr(road + ".translateY", 0.001)
    cmds.rotate(0, 0, 0, road)
    cmds.parent(road, extra)

    asphalt = make_shader("lambert", "Extra_Asphalt_mat")
    cmds.setAttr(asphalt + ".color", 0.08, 0.08, 0.10, type="double3")
    assign(road, asphalt)

    # 인도(좌/우)
    sideL, _ = cmds.polyPlane(w=48, h=4, name="ExtraSidewalkL_geo")
    sideR = cmds.duplicate(sideL, name="ExtraSidewalkR_geo")[0]
    cmds.setAttr(sideL + ".translateY", 0.0015)
    cmds.setAttr(sideR + ".translateY", 0.0015)
    cmds.setAttr(sideL + ".translateZ", 8)
    cmds.setAttr(sideR + ".translateZ", -8)
    cmds.parent(sideL, sideR, extra)

    sidewalk = make_shader("lambert", "Extra_Sidewalk_mat")
    cmds.setAttr(sidewalk + ".color", 0.18, 0.18, 0.20, type="double3")
    assign([sideL, sideR], sidewalk)

    # 차선(간단히 점선 조금)
    line_mat = make_shader("lambert", "Extra_Line_mat")
    cmds.setAttr(line_mat + ".color", 0.95, 0.85, 0.25, type="double3")
    cmds.setAttr(line_mat + ".incandescence", 0.08, 0.06, 0.02, type="double3")

    lines = []
    for i in range(-6, 7):
        if i % 2 == 0:
            seg, _ = cmds.polyCube(w=2.0, h=0.02, d=0.18, name=f"ExtraLine_{i}_geo")
            cmds.move(i * 3.0, 0.012, 0, seg)
            lines.append(seg)
    cmds.parent(lines, extra)
    assign(lines, line_mat)

    return extra

def add_streetlight(name, x, z, h=5.4):
    grp = cmds.group(em=True, name=name + "_grp")

    pole, _ = cmds.polyCylinder(r=0.08, h=h, sx=12, name=name + "_pole_geo")
    cmds.move(x, h/2, z, pole)

    arm, _ = cmds.polyCube(w=1.0, h=0.08, d=0.08, name=name + "_arm_geo")
    cmds.move(x + 0.45, h - 0.45, z, arm)

    bulb, _ = cmds.polySphere(r=0.18, sx=16, sy=10, name=name + "_bulb_geo")
    cmds.move(x + 0.95, h - 0.52, z, bulb)

    metal = make_shader("lambert", "Extra_LightMetal_mat")
    cmds.setAttr(metal + ".color", 0.25, 0.25, 0.28, type="double3")

    glow = make_shader("lambert", "Extra_LightBulb_mat")
    cmds.setAttr(glow + ".color", 1.0, 0.95, 0.75, type="double3")
    cmds.setAttr(glow + ".incandescence", 0.85, 0.75, 0.55, type="double3")

    assign([pole, arm], metal)
    assign(bulb, glow)

    cmds.parent(pole, arm, bulb, grp)
    return grp

def add_streetlights_row(x_from=-18, x_to=18, step=8, zA=6.2, zB=-6.2):
    lights_grp = cmds.group(em=True, name="StreetLightsExtra_grp")
    for x in range(x_from, x_to + 1, step):
        a = add_streetlight(f"ExtraStreetLightA_{x}", x, zA)
        b = add_streetlight(f"ExtraStreetLightB_{x}", x, zB)
        cmds.parent(a, b, lights_grp)
    return lights_grp

def add_extra_buildings():
    bgrp = cmds.group(em=True, name="BuildingsExtra_grp")

    # 도로 바깥쪽에만 살짝 추가(과하지 않게)
    coords = [(-22, 14), (-12, 18), (0, 20), (12, 18), (22, 14),
              (-22, -14), (22, -14)]
    for i, (x, z) in enumerate(coords, start=1):
        h = random.uniform(10, 20)
        w = random.uniform(6, 9)
        d = random.uniform(6, 9)

        b, _ = cmds.polyCube(w=w, d=d, h=h, name=f"ExtraBuilding_{i}_geo")
        cmds.move(x, h/2, z)

        # “차가운” 건물 색감 + 약간 변주
        mat = make_shader("lambert", f"ExtraBuilding_{i}_mat")
        base = 0.55 + random.random()*0.25
        cmds.setAttr(mat + ".color", base, base + 0.05, base + 0.12, type="double3")
        assign(b, mat)

        # 야경 창문(한 면만, 과하지 않게)
        if random.random() < 0.8:
            win, _ = cmds.polyPlane(w=w*0.6, h=h*0.5, name=f"ExtraBuilding_{i}_win_geo")
            cmds.move(x + w/2 + 0.01, h*0.55, z, win)
            cmds.rotate(0, 90, 0, win)

            wmat = make_shader("lambert", f"ExtraBuilding_{i}_win_mat")
            cmds.setAttr(wmat + ".color", 0.25, 0.8, 1.0, type="double3")
            cmds.setAttr(wmat + ".incandescence", 0.25, 0.8, 1.0, type="double3")
            assign(win, wmat)

            cmds.parent(win, bgrp)

        cmds.parent(b, bgrp)

    return bgrp

def add_skydome_night():
    # 이미 있으면 스킵
    if cmds.objExists("ExtraSkyDome_geo"):
        return "ExtraSkyDome_geo"

    dome, _ = cmds.polySphere(r=160, sx=36, sy=18, name="ExtraSkyDome_geo")
    cmds.setAttr(dome + ".translateY", 20)

    # 안쪽이 보이도록(실패해도 무시)
    try:
        cmds.polyNormal(dome, normalMode=0, userNormalMode=0, ch=0)
    except:
        pass

    sky = make_shader("lambert", "Extra_Sky_mat")
    cmds.setAttr(sky + ".color", 0.04, 0.06, 0.10, type="double3")
    cmds.setAttr(sky + ".incandescence", 0.02, 0.03, 0.05, type="double3")
    assign(dome, sky)

    cmds.setAttr(dome + ".castsShadows", 0)
    cmds.setAttr(dome + ".receiveShadows", 0)

    return dome

# -------------------------
# 실행(추가)
# -------------------------
# 1) 도로/인도 추가(색감 안정)
extra_grp = add_road_and_sidewalk()

# 2) 가로등 추가(요청 포인트)
lights = add_streetlights_row(step=8)
cmds.parent(lights, extra_grp)

# 3) 건물 조금 더 추가(과하지 않게 외곽만)
bld = add_extra_buildings()
cmds.parent(bld, extra_grp)

# 4) 야경 하늘(선택 느낌)
add_skydome_night()
