import re

id_re = re.compile("\d+")
text_re = re.compile("")
new_re = re.compile("")

with open("tweets.txt") as f:
    tweets = f.read()


print(list())

for tweet in map(lambda t: t.strip().split("|-----------------------------------|"),
                 tweets.strip().split("|===================================|")):
    if len(tweet) == 2:
        with open(f"related/t{tweet[0].strip()}.txt", "a") as f:
            f.write("\n\n")
            f.write(tweet[1])
        print(f"Joined {tweet[0].strip()}")
    else:
        print(f"Error with {tweet}")
