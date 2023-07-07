import re
from datetime import datetime

log_file = "testlogs.log"  # replace with your actual log file path

queue_re = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Attempting to queue Deployment of '(.*?)'.*")
sent_re = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Deployment of '.*' on '.*' sent to agent.*")

queue_dict = {}

with open(log_file, 'r') as f:
    for line in f:
        queue_match = queue_re.match(line)
        sent_match = sent_re.match(line)

        if queue_match:
            time_str = queue_match.group(1)
            deployment_name = queue_match.group(2)
            queue_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S,%f")

            # Add queue_time to the list of queue times for deployment_name
            if deployment_name not in queue_dict:
                queue_dict[deployment_name] = [queue_time]
            else:
                queue_dict[deployment_name].append(queue_time)

        if sent_match:
            time_str = sent_match.group(1)
            sent_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S,%f")
            for name, q_times in list(queue_dict.items()):
                if q_times:
                    q_time = q_times.pop(0)  # remove the first queue time in the list
                    time_diff = sent_time - q_time
                    print(f"Deployment {name} took {time_diff.total_seconds()} seconds to be sent to the queue.")
                    if not q_times:  # if there are no more queue times for this deployment, remove it from the dict
                        del queue_dict[name]
                break  # assuming each 'sent to agent' corresponds to the latest 'Attempting to queue'
