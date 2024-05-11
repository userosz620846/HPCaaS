# import numpy as np
# import pandas as pd
# from sklearn.datasets import make_blobs

# # Generate synthetic data with three clusters (you can adjust parameters)
# n_samples = 100000000  # Increase the number of samples
# n_features = 2
# n_clusters = 3

# # Create blobs with distinct centers
# X, y = make_blobs(n_samples=n_samples, n_features=n_features, centers=n_clusters, random_state=42, dtype=np.float16)

# # Convert to a Pandas DataFrame
# df = pd.DataFrame(X, columns=['x', 'y'])
# # df['class'] = y

# # Save the larger dataset to a CSV file
# df.to_csv('mydata.csv', index=False)

# print("Larger synthetic dataset saved as 'mydata.csv'")
##-------------------------------------------------------------------------

# import pandas as pd
# import numpy as np

# # Generate random points
# n_points = 100000000
# x_values = np.random.rand(n_points)
# y_values = np.random.rand(n_points)

# # Create a DataFrame
# df = pd.DataFrame({'x': x_values, 'y': y_values})

# # Save to a CSV file
# df.to_csv('mydata.csv', index=False)

# print("Random points saved as 'mydata.csv'")


##---------------------------------------------------------------------------------

# import csv

# def create_matrix(n):
#     """
#     Creates an n x n matrix filled with sequential integers.
#     """
#     matrix = [[i * n + j +12 for j in range(n)] for i in range(n)]
#     return matrix

# def save_matrix_to_csv(matrix, filename):
#     """
#     Converts the matrix to a CSV file.
#     """
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerows(matrix)

# if __name__ == "__main__":
#     n = 15
#     matrix = create_matrix(n)
#     filename = "matrix15.csv"
#     save_matrix_to_csv(matrix, filename)
#     print(f"Matrix of size {n}x{n} saved to {filename}.")


import csv

def create_matrix(rows, cols):
    """
    Creates a matrix filled with sequential integers.
    """
    matrix = [[i * cols + j + 12 for j in range(cols)] for i in range(rows)]
    return matrix

def save_matrix_to_csv(matrix, filename):
    """
    Converts the matrix to a CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)

if __name__ == "__main__":
    rows = 30
    cols = 45
    matrix = create_matrix(rows, cols)
    filename = f"matrix{rows}x{cols}.csv"
    save_matrix_to_csv(matrix, filename)
    print(f"Matrix of size {rows}x{cols} saved to {filename}.")
