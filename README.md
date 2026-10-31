# rover\_llm



\# Rover Command LLM



A small transformer language model, trained from scratch on CPU, that turns plain-English rover commands into a step plan. A chat assistant then prints the ROS 2 commands to run, asks you for `/odom` values, and prints the exact `/cmd\_vel` Twist values for each step.



\*\*It only prints. It never publishes to ROS 2 or moves a robot.\*\*



Example: `go straight 4 m then 6 m left` becomes `MOVE F 4; TURN L 90deg; MOVE F 6`



\## How it works



1\. A character-level transformer converts your sentence into a short plan.

2\. A strict validator checks the plan and enforces limits (20 m, 720 degrees, 60 s per step).

3\. You confirm the plan with `y/n`.

4\. Plain Python code (not the model) computes the Twist values, durations, `ros2 topic pub` commands and expected odometry.



The model never produces velocity numbers. Chat memory (last pose, last plan) is kept by `chat.py`.



\## Requirements



\- Python 3.10 or newer

\- Git

\- About 1 GB of disk space for PyTorch (CPU build)

\- No GPU and no ROS 2 needed to run the assistant



\## Quick start: Windows (PowerShell)



```powershell

git clone https://github.com/eshwareshanth-maker/rover\_llm.git

cd rover\_llm

python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.venv\\Scripts\\Activate.ps1

pip install torch

python src\\chat.py

```



\## Quick start: Ubuntu



```bash

sudo apt update

sudo apt install -y git python3 python3-venv python3-pip

git clone https://github.com/eshwareshanth-maker/rover\_llm.git

cd rover\_llm

python3 -m venv .venv

source .venv/bin/activate

pip install torch --index-url https://download.pytorch.org/whl/cpu

python src/chat.py

```



Run all scripts from the `rover\_llm` folder, not from inside `src`.



\## Example session



```

>> go straight 4 m then 6 m left

I understood:

&#x20; 1. MOVE forward 4 m

&#x20; 2. TURN left / counter-clockwise by 90 deg

&#x20; 3. MOVE forward 6 m

Correct? \[y/n] y

Run in another terminal:  python3 odom.py   (shows /odom)

Paste 4 numbers from /odom:  x  y  qz  qw   (example: 0.0 0.0 0.0 1.0)

odom> 0.0 0.0 0.0 1.0



=== COMMANDS TO RUN (Ubuntu / WSL terminals) ===

Terminal A:  python3 cmd\_vel\_relay.py

Terminal B:  run these in order, waiting for each to finish



Step 1: MOVE forward 4 m

&#x20; topic: /cmd\_vel   type: geometry\_msgs/msg/Twist

&#x20; linear  x=+0.200 m/s  y=+0.000  z=+0.000

&#x20; angular x=+0.000  y=+0.000  z=+0.000 rad/s

&#x20; hold for 20.00 s, then publish all zeros

&#x20; expected /odom afterwards: x=4.000 y=0.000 yaw=0.0 deg

...

```



Chat commands: type any rover command, or `repeat`, `pose`, `quit`.



Clockwise turns print a negative `angular.z`, because in ROS positive is counter-clockwise.



\## Retrain the model (optional)



The repo includes a trained model (`checkpoints/model.pt`), so retraining is not needed. To retrain, for example after adding new phrasing to `src/gen\_dataset.py`:



```

python src/gen\_dataset.py

python src/prepare\_data.py

python src/train.py

python src/evaluate.py

```



On Ubuntu, run `mkdir -p data checkpoints` first. Training takes a while on CPU. For a quick test, set `max\_steps=300` in `train()` in `src/train.py`. `evaluate.py` reports exact-match accuracy on sentences that were not in the training set.



\## Configure for your rover



Edit the top of `src/rover.py`:



| Setting | Default | Meaning |

| --- | --- | --- |

| `LIN\_SPEED` | 0.2 | forward speed, m/s |

| `ANG\_SPEED` | 0.5 | turning speed, rad/s |

| `ODOM\_CMD` | `python3 odom.py` | command that shows `/odom` |

| `RELAY\_CMD` | `python3 cmd\_vel\_relay.py` | command that relays `/cmd\_vel` |



`odom.py` and `cmd\_vel\_relay.py` are not part of this repo. Point these settings at your own scripts.



Interpretations built into the dataset: `6 m left` means turn left 90 degrees, then drive 6 m. A bare `turn left` means 90 degrees. `u-turn` means 180 degrees.



\## Project layout



```

src/common.py          vocabulary, plan grammar, safety limits

src/gen\_dataset.py     generates training data (instruction -> plan)

src/prepare\_data.py    converts the data to tensors

src/model.py           the transformer

src/train.py           training loop

src/planner.py         text -> plan (greedy decoding)

src/evaluate.py        accuracy on held-out sentences

src/rover.py           Twist values, commands, expected odometry

src/chat.py            interactive assistant

checkpoints/model.pt   trained weights

data/meta.json         model settings

```



\## Troubleshooting



\- \*\*Scripts are disabled (Windows):\*\* run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate the venv again.

\- \*\*`ModuleNotFoundError` or file not found:\*\* run from the repo root, with the venv active.

\- \*\*`checkpoints/model.pt` or `data/meta.json` missing:\*\* run the retrain steps above.

\- \*\*A command is rejected or misread:\*\* add that phrasing to `src/gen\_dataset.py`, then retrain. Always check the `I understood` list before confirming.



\## Limitations



The model is small and trained on generated sentences. It handles phrasing similar to the dataset and rejects unfamiliar wording rather than guessing. Test in simulation (for example Gazebo) before using a real rover.

