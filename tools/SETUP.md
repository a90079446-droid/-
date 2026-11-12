# 영상·3D 도구 설치 메모 (클라우드 세션은 끝나면 초기화되므로 필요할 때 다시 설치)

- Blender (파이썬 모듈): `pip install bpy`  → `import bpy`, Cycles CPU 렌더 확인(5.3.0)
- Godot 3.5: `apt-get install -y godot3 xvfb`  → `xvfb-run -a godot3 --path <프로젝트> --no-window`
- Three.js: `npm install three` (0.187) → 크롬 headless `--use-gl=swiftshader --enable-unsafe-swiftshader`로 캡처
- Canvas 2D: 브라우저 내장(설치 필요 없음), HTML을 프레임으로 캡처해 ffmpeg로 합침
- Unreal / Unity: 클라우드에 설치 불가 (계정 로그인·GPU·수십 GB 필요). 사용자 PC에 설치해서 사용.
