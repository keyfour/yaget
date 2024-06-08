# main.py

def process_data(data):
    # TODO: Optimize the data processing algorithm
    processed_data = [x * 2 for x in data]  # Simple processing for now
    # ENDTODO
    return processed_data

if __name__ == "__main__":
    sample_data = [1, 2, 3, 4, 5]
    print("Processed Data:", process_data(sample_data))

