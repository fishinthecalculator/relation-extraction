from pathlib import Path


def tweet_to_path(tweet_id, root=Path.cwd(), make_it=False):
    dirs = [tweet_id[i - 1:i + 1] for i in range(1, len(tweet_id) + 1, 2)]
    path = Path(root, *dirs)
    if make_it:
        path.mkdir(parents=True, exist_ok=True)
    return path
