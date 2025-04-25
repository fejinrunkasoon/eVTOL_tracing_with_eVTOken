import threading
import time

# 功能1：计算并输出100以内的质数
def print_prime_in_100():
    for n in range(2,101): #1不是质数，所以可以从2开始遍历
        if n ==2:
            print(f"{n} is prime")
            continue #如果输入return 语句会导致循环提前终止，所以使用continue
        if n % 2 == 0:
            continue #跳过其他偶数
        is_prime =True
        for h in range(3,int(n**0.5)+1,2): #检查奇数因数
            if n % h ==0:
                is_prime=False
                break
        if is_prime:
            print(f"{n} is prime")  
        time.sleep(0.1)   #延时：方便多线程交替输出，该打印结束，允许另一个进程运行
    

# 功能2：计算并输出100以内，所有能被3整除的数字        
def calculate():
    for n in range(1,101):
        if n % 3 ==0:
            print(f"the number{n} can be divided by 3")
        time.sleep(0.1)   #延时：方便多线程交替输出，该打印结束，允许另一个进程运行
        
        
if __name__ == "__main__":
    thread1 =threading.Thread(target=print_prime_in_100)
    thread2 =threading.Thread(target=calculate)
    
    # 多线程的核心特征是任务并发执行，具体体现为:
    # 1/由于两个线程同时运行，print_numbers和calculate的输出会交替出现。
    # 2/time.sleep(0.1)的等待耗时模拟
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    print("All tasks are completed")