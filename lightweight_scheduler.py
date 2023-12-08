
# A simple to use API for scheduling jobs, made for humans.
# In-process scheduler for periodic jobs. No extra processes needed!
# Very lightweight and no external dependencies.
# Excellent test coverage.
# Tested on Python and 3.7, 3.8, 3.9, 3.10, 3.11

# requires : pip install schedule

import schedule
import time


def job():
    print("I'm working...")

schedule.every(2).seconds.do(job)
schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every(5).to(10).minutes.do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)
schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
schedule.every().minute.at(":17").do(job)

def job_with_argument(name):
    print(f"I am {name}")

schedule.every(4).seconds.do(job_with_argument, name="Peter")

while True:
    schedule.run_pending()
    time.sleep(1)

def main():
    get_latest_price()
    


if __name__ == "__main__":
    main()