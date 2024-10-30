import subprocess
import json
import os

# 사용중인 CPU 크기 확인
def check_CPU(n):
    CPU=[]
    for n in range(1,n+1):
        r = subprocess.check_output(["docker", "stats", f"me-blog-{n}", "--no-stream", "--format", "{{json .}}"])
        j = json.loads(r.decode("utf-8"))
        CPU.append(float(j['CPUPerc'].strip('%')))
    print(sum(CPU))
    return sum(CPU)


while True:
    # 실행 중인 도커 개수 카운트
    r = subprocess.check_output(["docker", "ps", "--filter","name=me-blog", "--format", "{{.Names}}"])
    blog = r.decode("utf-8").strip().split("\n")
    blogcount=len(blog)
    print(len(blog))
    
    useCPU=check_CPU(blogcount) 
    # 전체 CPU 사용량이 50%를 넘으면 
    # n+1개로 scale out
    if useCPU > 0.5:
        print(f"CPU 사용량이 50%를 넘었습니다.{blogcount+1}개로 scale out을 진행합니다.")
        os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount+1}")

    # 전체 CPU 사용량이 20% 미만이면
    # 1개로 scale in
    elif useCPU < 0.2:
        if blogcount >1:
            print(f"현재 blog는 {blogcount}개로, CPU 사용량이 20% 미만입니다. 1개로 scale in을 진행합니다.")
            os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog=1")
    os.system("sleep 5")


