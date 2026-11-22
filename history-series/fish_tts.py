#!/usr/bin/env python3
"""에피소드 JSON 의 장면별 내레이션을 Fish Audio 로 생성 → work/<id>/voice/sNN.mp3
API 키는 네트워크 프록시가 넣어주므로 코드에는 없다. 로컬에서는 FISH_API_KEY 환경변수를 쓴다."""
import json, os, sys, time, urllib.request
VOICE = os.environ.get("FISH_VOICE_ID", "305751c5cd59475cb48b342f907fd76c")
KEY = os.environ.get("FISH_API_KEY", "proxy-injected")
ep = json.load(open(sys.argv[1]))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", ep["id"], "voice")
os.makedirs(out, exist_ok=True)
for i, sc in enumerate(ep["scenes"]):
    p = os.path.join(out, f"s{i:02d}.mp3")
    if not sc.get("narr") or os.path.exists(p):
        continue
    body = json.dumps({"text": sc["narr"], "reference_id": VOICE, "format": "mp3", "latency": "normal"}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://api.fish.audio/v1/tts", data=body, method="POST", headers={
                "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "model": "s1"})
            data = urllib.request.urlopen(req, timeout=120).read()
            open(p, "wb").write(data); print("ok", i, len(data), flush=True); break
        except Exception as e:
            print("retry", i, e, flush=True); time.sleep(3 * (attempt + 1))
