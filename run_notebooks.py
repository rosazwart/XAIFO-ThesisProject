import subprocess

if __name__ == "__main__":
    notebooks_to_run = ['edge2vec_embedding.ipynb', 'predictor.ipynb']  # Replace with your notebook file names

    for i in range(9):
        print(f'Time {i}')
        for notebook in notebooks_to_run:
            cmd = f'jupyter nbconvert --execute --inplace {notebook}'
            subprocess.run(cmd, shell=True)