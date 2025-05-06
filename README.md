발표영상은 아래 유튜브링크에 있습니다.
https://www.youtube.com/watch?v=kHCK4kMwv8U

아래느 코드 설명입니다.

1. bvh_viewer_code.py BVH 뷰어코드 제작
모션캡쳐 된 BVH 파일을 OpenGL로 렌더링하는 스크립트입니다. 트리구조의 BVH 파일을 읽어들이고, wxpython으로 사용자의 입력값을 처리합니다.

![image](https://github.com/user-attachments/assets/e12c5cf3-8c14-4896-baf6-958d6f67b8a1)

2. fps60.py 프레임 드랍 전처리
Data Set을 60프레임으로 낮추는 스크립트입니다. CMU Data Set은 120프레임으로 모션캡쳐 되어 있어 데이터가 과하므로 프레임을 낮추어 해결하였습니다.

3. location.py 모든 joint의 위치 계산
BVH 파일로부터 프레임별 모든 joint의 3D 위치(x, y, z)를 계산하여 *_location.txt 로 저장합니다. 캐릭터 위치를 min_y 값 기준으로 위로 띄워서 지면 위를 걷도록 위치값을 보정합니다.

4. vel.py joint의 속도 계산
*_location.txt (joint 위치)로부터 속도값을 계산하여 *_velocity.txt 로 저장합니다.

5. trajectory.py = location + velocity = 경로
*_location.txt (joint 위치)와 *_velocity.txt (속도)를 결합한 경로값을 *.database 로 저장합니다. 이는 학습 데이터로 사용됩니다.

6. face_vector.py 정면 방향 벡터
BVH 파일로부터 각 프레임별로 캐릭터의 정면 방향 벡터를 계산해서 출력합니다. 사람의 어깨와 골반 방향을 기반으로 계산되며, 학습 데이터로 사용됩니다.

7. phase.py phase 기준 프레임 지정
좌우 발이 지면에 닿은 순간의 프레임 번호를 추출하여 _phase.txt 로 저장합니다. 이를 left 와 right로 표기하여 phase의 기준이 되는 프레임을 지정하는 역할을 하도록 합니다. 

8. interpolate.py 선형 보간
_phase.txt 로부터 보행의 phase 값을 생성하여 .phase 파일로 저장합니다. 프레임과 함께 적인 right left 값을 기준으로 선형 보간하여 0~1 사이의 값으로 phase 값을 반환합니다. .phase 파일은 학습 데이터로 사용됩니다.
[interpolate.py 예시]
0 right (phase 0)
(phase 증가)
28 left (phase 1)
(phase 감소)
54 end (phase 0)

9. gait.py 동작 상태 판별
BVH 파일로부터 동작 상태(gait state)를 추출하여 .gait 파일로 변환하는 스크립트입니다. stand, walk, jog, run, cross, jump, cratwheel, etc 의 8가지 동작 중에서 BVH 프레임이 어떤 동작 상태인지 분류하여 숫자로 치환합니다. 이렇게 처리된 .gait 파일은 학습 데이터로 사용됩니다.

10. new_nn.py pytorch 딥러닝 학습
.input .output .phase 파일을 기반으로 PFNN 학습을 수행합니다. Net 클래스는 3-layer MLP을 갖는 4개의 서브넷입니다. forward() 함수는 phase 값을 기반으로 한 4개의 subnet을 spline 방식으로 보간하여 중간값을 예측하도록 합니다. work() 함수에서 100 EPOCH 만큼 학습을 수행하도록 지정하였습니다. 그 결과, input 프레임에 대한 joint position delta, joint velocity, joint rotation 값을 예측하여 output 프레임으로 반환하도록 합니다.

11. nn_based_bvh2.py 학습 결과
학습된 결과를 바탕으로 tensor.py 모델을 로딩해서, BVH 파일을 드래그 앤 드롭 하여, 실시간으로 동작시키는 BVH viewer 파일입니다. Start 버튼으로 시작하고 Stop 버튼으로 중지할 수 있습니다. << >> 버튼으로 프레임 이동이 가능하며, Jump 버튼으로 특정 프레임으로 이동 가능합니다. 키보드 화살표를 기반으로 사용자가 목표하는 속도를 입력받습니다.

![image](https://github.com/user-attachments/assets/8e2cd95b-842f-4882-b2ad-bdd4f19e9506)
