import re


class Message(object):
    def __init__(self):
        self.valid = True
        self.repeat = False
        self.next_available = {
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
        self.rewards = []
        self.rarity = "unknown"

    def set_next_available(self, hours, minutes, seconds):
        self.next_available.update({
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        })


def parse_message(content):
    message = Message()

    if "rarity_" not in content:
        message.valid = False

    else:
        message.rarity = content.split("rarity_")[1].split(":")[0]

        if "You already have claimed" in content:
            # already claimed this one
            message.repeat = True

            time_content = content.split("Please come back in ")[1].split(".")[0]

            result = re.findall(r'\d{1,}', time_content)
            hours = 19
            minutes = 59
            seconds = 60

            if "hour" in time_content:
                hours = hours - int(result.pop(0))
            if "minute" in time_content:
                minutes = minutes - int(result.pop(0))
            if "second" in time_content:
                seconds = seconds - int(result.pop(0))

            if seconds == 60:
                minutes = minutes + 1
                seconds = 0

            if minutes == 60:
                hours = hours + 1
                minutes = 0

            message.set_next_available(hours, minutes, seconds)

        rewards = ":".join(content.split("reward")[-1].split(":")[1:])
        results = set(re.findall(r'<:[^:]*:\d{5,}>', rewards))
        for result in results:
            rewards = rewards.replace(result, "")
        items = rewards.split("\n")
        items = [item.strip() for item in items if item.strip() != ""]
        message.rewards = items

    return message
