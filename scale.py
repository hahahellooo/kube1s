import subprocess
import json
import os
import time
import requests

# LINE noti 보내기
api_url = 'https://notify-api.line.me/api/notify'
key = os.getenv('LINE_TOKEN')

# 사용중인 CPU 크기 확인
def check_CPU(n):
    CPU=[]
    for n in range(1,n+1):
        r = subprocess.check_output(["docker", "stats", f"me-blog-{n}", "--no-stream", "--format", "{{json .}}"])
        j = json.loads(r.decode("utf-8"))
        CPU.append(float(j['CPUPerc'].strip('%')))
    return sum(CPU)


max_time= time.time() + (60*1)
while True:

    # 실행 중인 도커 개수 카운트
    r = subprocess.check_output(["docker", "ps", "--filter","name=me-blog", "--format", "{{.Names}}"])
    blog = r.decode("utf-8").strip().split("\n")
    blogcount=len(blog)
    useCPU=round(check_CPU(blogcount),3) 

    # 전체 CPU 사용량이 50%를 넘고 1분 이상 지속되면
    # n-1개로 scale in
    if useCPU > 0.5 and time.time() >= max_time:
        print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 50%를 넘었습니다. \n 1분 이상 지속되어 {blogcount+1}개로 scale out을 진행합니다.")
        os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount+1}")
        request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'{blogcount+1}개로 scale out 진행 중'})
   
   # 전체 CPU 사용량이 50%를 넘지만 1분 미만 지속되면
    # n+1개로 scale out
    elif useCPU> 0.5 and time.time() < max_time:
        if blogcount>1:
            print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 50%를 넘었습니다.\n 1분 이상 지속되지 않아 {blogcount-1}개로 scale in을 진행합니다.")
            os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount-1}")
            request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'1분 이상 지속되지 않아 {blogcount-1}개로 scale in 진행 중'})

    # 전체 CPU 사용량이 10% 미만이면
    # n+1개로 scale out
    elif useCPU < 0.1:
        if blogcount>1:
            print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 10% 미만입니다. \n {blogcount-1}개로 scale in을 진행합니다.")
            os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount-1}")
            request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'CPU 사용량 10% 미만, {blogcount-1}개로 scale out 진행 중'})
os.system("sleep 10")


