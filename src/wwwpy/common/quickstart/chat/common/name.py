import random

adjectives = [
    'adaptive', 'agile', 'ambitious', 'analytical', 'bold', 'brilliant', 'clever', 'crazy', 'creative', 'curious',
    'daring', 'determined', 'dynamic', 'efficient', 'energetic', 'fearless', 'focused', 'innovative', 'insightful',
    'inspired', 'intuitive', 'masterful', 'mighty', 'nimble', 'passionate', 'proactive', 'quick', 'reliable',
    'resourceful', 'savvy', 'sharp', 'skillful', 'sleek', 'smart', 'strategic', 'talented', 'tenacious',
    'versatile', 'visionary', 'witty'
]

roles = [
    'ace', 'analyst', 'architect', 'artisan', 'builder', 'champion', 'coder', 'connoisseur', 'creator', 'debugger',
    'designer', 'developer', 'dynamo', 'engineer', 'expert', 'genius', 'guru', 'innovator', 'luminary', 'maestro',
    'maintainer', 'manager', 'master', 'maverick', 'ninja', 'operator', 'pioneer', 'prodigy', 'programmer', 'sage',
    'specialist', 'strategist', 'technician', 'trailblazer', 'tuner', 'virtuoso', 'visionary', 'whiz', 'wizard',
    'wrangler'
]


def generate_name():
    return f"{random.choice(adjectives)}-{random.choice(roles)}"
