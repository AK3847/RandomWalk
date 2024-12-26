import ollama
import json
import os
import argparse
import time

ollama_client = ollama.Client()

GRID_SIZE = 20
INITIAL_X = 0
INITIAL_Y = 0
TOTAL_STEPS = 20
MODEL_NAME = ""
TEMP_RANGE = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
ROUNDS_PER_TEMP = 5
DATA_DIR = "data"
DATA_FILE = ""

# path = [[INITIAL_Y,INITIAL_X]]
# current_position = [INITIAL_X,INITIAL_Y]

data = {}


def construct_path():
    data[f"{MODEL_NAME}"] = {}

    for curr_temp in TEMP_RANGE:
        data[f"{MODEL_NAME}"][f"TEMP_{curr_temp}"] = {}

        start_time = time.time()
        for curr_round in range(ROUNDS_PER_TEMP):
            data[f"{MODEL_NAME}"][f"TEMP_{curr_temp}"][f"R_{curr_round}"] = [[], []]

            path = [[INITIAL_Y, INITIAL_X]]
            current_position = [INITIAL_X, INITIAL_Y]

            for step in range(TOTAL_STEPS):
                data[f"{MODEL_NAME}"][f"TEMP_{curr_temp}"][f"R_{curr_round}"][1].append(
                    current_position.copy()
                )

                prompt = f"""
                You are a random walker in a grid of size {GRID_SIZE} x {GRID_SIZE} which is centered at (0,0).
                You started at step = 0 and your current step is {step}, with your position being {current_position}
                Your task is to reply with either UP, DOWN, LEFT or RIGHT to move in any direction that you want.
                If you find that the direction you choose will put you out of the Gride size - {GRID_SIZE} x {GRID_SIZE} reply with STOP.
                Do not reply with any other extra words apart from the above.
                """
                response = ollama_client.chat(
                    model=f"{MODEL_NAME}",
                    messages=[{"role": "user", "content": f"{prompt}"}],
                    options={"temperature": curr_temp},
                )
                reply = response["message"]["content"].strip()

                if reply == "RIGHT":
                    dx, dy = 1, 0
                elif reply == "LEFT":
                    dx, dy = -1, 0
                elif reply == "DOWN":
                    dx, dy = 0, -1
                elif reply == "UP":
                    dx, dy = 0, 1
                else:
                    dx, dy = 0, 0
                current_position[0] += dx
                current_position[1] += dy

                data[f"{MODEL_NAME}"][f"TEMP_{curr_temp}"][f"R_{curr_round}"][0].append(
                    reply
                )

                path.append(current_position.copy())
        end_time = time.time() - start_time
        print(
            f"--- {ROUNDS_PER_TEMP} rounds done for temperature - {curr_temp} - time taken : {end_time:.2f} seconds"
        )

    # print(data)
    print(f"Saving data to {DATA_FILE}")
    with open(f"{DATA_FILE}", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random Walk")
    parser.add_argument("--model_name", "-m", type=str, help="Name of the model")
    args = parser.parse_args()

    MODEL_NAME = args.model_name
    modified_file_name = (
        str(MODEL_NAME).split(":")[0] + "_" + str(MODEL_NAME).split(":")[1]
    )
    DATA_FILE = os.path.join(DATA_DIR, f"{modified_file_name}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    config = f"""
    The model: {MODEL_NAME} will RandomeWalk for {TOTAL_STEPS} steps
    in the gride of size {GRID_SIZE}x{GRID_SIZE} 
    at Temperature values - {TEMP_RANGE} 
    with each temperature having {ROUNDS_PER_TEMP} independent rounds.
    Total API calls - {TOTAL_STEPS*len(TEMP_RANGE)*ROUNDS_PER_TEMP}
    """
    print(config)
    construct_path()
