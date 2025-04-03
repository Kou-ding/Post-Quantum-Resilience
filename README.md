# Post-Quantum-Resilience
Thoughts on the topic of post-quantum cryptography and the algorithms required to ensure resilience in information systems in a post-quantum world.

### Conda + pip setup
Recreate identical code running conditions:  
```bash
# Step 1: Recreate conda environment
conda env create -f environment.yml

# Step 2: Activate the conda env
conda activate env_name

# Step 3: Install dependencies from requirements txt
pip install -r requirements.txt
```

To-do List
----------
- [] Test the IBM quantum computer API on old shor
- [] Break RSA using a binary computer
- [] 