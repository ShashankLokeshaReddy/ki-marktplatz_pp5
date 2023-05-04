import simpy
import random

class Machine:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine_resource = simpy.Resource(env, capacity=1)

    def process_job(self, job):
        # Wait for machine resource to be available
        with self.machine_resource.request() as request:
            yield request
            print(f"Job {job['job']} on Machine {self.name} starts at {self.env.now}")
            # Simulate job processing time
            yield self.env.timeout(job["duration_machine"])
            print(f"Job {job['job']} on Machine {self.name} ends at {self.env.now}")

def generate_jobs(num_jobs):
    for i in range(num_jobs):
        yield {"job": f"job{i}", "duration_machine": random.randint(1, 10)}

def run_simultaneously(env, machines):
    jobs = list(generate_jobs(10))  # Generate 10 jobs
    while jobs:
        job = jobs.pop(0)
        # Choose a machine randomly to process the job
        chosen_machine = random.choice(machines)
        env.process(chosen_machine.process_job(job))

if __name__ == "__main__":
    env = simpy.Environment()
    m1531 = Machine(env, "1531")
    m1532 = Machine(env, "1532")
    m1533 = Machine(env, "1533")
    m1534 = Machine(env, "1534")
    m1535 = Machine(env, "1535")
    m1536 = Machine(env, "1536")
    m1537 = Machine(env, "1537")
    m1541 = Machine(env, "1541")
    m1542 = Machine(env, "1542")
    m1543 = Machine(env, "1543")
    
    machines = [m1531, m1532, m1533, m1534, m1535, m1536, m1537, m1541, m1542, m1543]
    
    run_simultaneously(env, machines)
    
    env.run(until=100)  # Run the simulation for 100 units of time
