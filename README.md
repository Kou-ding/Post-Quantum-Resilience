# Post-Quantum-Resilience
Thoughts on the topic of post-quantum cryptography and the algorithms required to ensure resilience in information systems in a post-quantum world.

### Conda setup
Installation:
```bash
yay -S miniconda3
```

Add the following lines at the ewnd of the ~/.bashrc file:
```txt
export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1
[ -f /opt/miniconda3/etc/profile.d/conda.sh ] && source /opt/miniconda3/etc/profile.d/conda.sh
```

Commands:
```bash
# Create a new conda environment
conda create --name myenv python=3.8.0

# Activate the new environment
conda activate myenv

# Install a package in the active environment
conda install numpy

# List all conda environments
conda env list

# Deactivate the current environment
conda deactivate

# Remove an environment
conda remove --name myenv --all
```
