from challenge_db import (
    get_user_stats,
    get_achievements,
    give_achievement
)


BADGES = [

    {
        "name": "🥇 First Workout",
        "type": "workouts",
        "required": 1
    },

    {
        "name": "🏃 5 Runs",
        "type": "runs",
        "required": 5
    },

    {
        "name": "🏃 10 Runs",
        "type": "runs",
        "required": 10
    },

    {
        "name": "🏃 25 Runs",
        "type": "runs",
        "required": 25
    },

    {
        "name": "🚶 First Walk",
        "type": "walks",
        "required": 1
    },

    {
        "name": "🚶 10 Walks",
        "type": "walks",
        "required": 10
    },

    {
        "name": "🥾 First Hike",
        "type": "hikes",
        "required": 1
    },

    {
        "name": "⏱ 5 Hours Logged",
        "type": "hours",
        "required": 5
    },

    {
        "name": "⏱ 10 Hours Logged",
        "type": "hours",
        "required": 10
    }

]


def check_badges(user_id):

    stats = get_user_stats(user_id)

    workouts = stats[0] or 0
    runs = stats[1] or 0
    walks = stats[2] or 0
    hikes = stats[3] or 0
    total_minutes = stats[4] or 0

    hours = total_minutes // 60

    values = {

        "workouts": workouts,
        "runs": runs,
        "walks": walks,
        "hikes": hikes,
        "hours": hours

    }

    unlocked = []

    for badge in BADGES:

        current = values[badge["type"]]

        if current >= badge["required"]:

            earned = give_achievement(
                user_id,
                badge["name"]
            )

            if earned:
                unlocked.append(
                    badge["name"]
                )

    return unlocked


def get_badge_progress(user_id):

    stats = get_user_stats(user_id)

    workouts = stats[0] or 0
    runs = stats[1] or 0
    walks = stats[2] or 0
    hikes = stats[3] or 0
    total_minutes = stats[4] or 0

    hours = total_minutes // 60

    earned = {

        badge[0]

        for badge in get_achievements(user_id)

    }

    progress = []

    for badge in BADGES:

        if badge["type"] == "workouts":
            current = workouts

        elif badge["type"] == "runs":
            current = runs

        elif badge["type"] == "walks":
            current = walks

        elif badge["type"] == "hikes":
            current = hikes

        else:
            current = hours

        progress.append({

            "name": badge["name"],

            "earned": badge["name"] in earned,

            "current": current,

            "required": badge["required"]

        })

    return progress