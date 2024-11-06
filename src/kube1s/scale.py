import subprocess
import json
import os
import time
import requests

# LINE noti 보내기
api_url = 'https://notify-api.line.me/api/notify'
key = os.getenv('LINE_TOKEN')

start_time = 0

# 사용중인 CPU 크기 확인
def check_CPU(n):
    CPU=[]
    for n in range(1,n+1):
        r = subprocess.check_output(["docker", "stats", f"me-blog-{n}", "--no-stream", "--format", "{{json .}}"])
        j = json.loads(r.decode("utf-8"))
        CPU.append(float(j['CPUPerc'].strip('%')))
    return sum(CPU)

# 로그파일 만들기
def save_log(event):
    file_name='scale_log.txt'
    my_path = __file__
    dir_name = os.path.dirname(my_path)

    # 디렉토리가 없을 경우 생성
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok = True)
    file_path = os.path.join(dir_name, file_name)
    
    with open(file_path, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%s %H:%M:%S')} / {event}\n")

# auto scale in & out
def auto_controll():
    
    while True:

    # 실행 중인 도커 개수 카운트
        r = subprocess.check_output(["docker", "ps", "--filter","name=me-blog", "--format", "{{.Names}}"])
        blog = r.decode("utf-8").strip().split("\n")
        blogcount=len(blog)
        useCPU=check_CPU(blogcount)

    # 전체 CPU 사용량이 50%를 넘고 1분 이상 지속되면
    # n+1개로 scale out
        if useCPU > 0.5:
            if not start_time:
                start_time = time.time()
            else: 
                end_time = time.time()
                if end_time - start_time >=60.00:
                    print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 50%를 넘었습니다. 1분 이상 지속되어 {blogcount+1}개로 scale out을 진행합니다.")
                    os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount+1}")
                    save_log(f"scale out / {blogcount+1}")
                    request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'{blogcount+1}개로 scale out 진행 중'})
                    start_time = 0 # 조건문 진행되면 시간 초기화 

    # 전체 CPU 사용량이 50%를 넘지만 1분 미만 지속되면
    # n-1개로 scale in
        elif useCPU> 0.5 and blogcount>1:
            if not start_time:
                start_time=time.time()
            else:
                end_time= time.time()
                if end_time - start_time >= 60.00:                
                    print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 50%를 넘었습니다. 1분 이상 지속되지 않아 {blogcount-1}개로 scale in을 진행합니다.")
                    os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog={blogcount-1}")
                    save_log(f"scale in  / {blogcount-1}")
                    request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'1분 이상 지속되지 않아 {blogcount-1}개로 scale in 진행 중'})
                    start_time = 0

    # 전체 CPU 사용량이 2% 미만이면
    # 1개로 scale in
        elif useCPU < 0.02:
            print(f"현재 blog는 {blogcount}개, CPU 사용량은 {useCPU}로 2% 미만입니다. 1개로 scale in을 진행합니다.")
            os.system(f"docker compose -f /home/hahahellooo/code/docker/kube1s/docker-compose.yml up -d --scale blog=1")
            save_log(f"scale in  / 1")
            request = requests.post(url=api_url, headers =  {'Authorization':'Bearer ' + key}, data = {'message' : f'CPU 사용량 2% 미만, 1개로 scale in 진행 중'})
            start_time = 0

        # 10 초마다 동작
        time.sleep(10)

