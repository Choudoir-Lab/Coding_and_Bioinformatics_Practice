# Coding and Bioinformatics Practice


## Miniconda

<br>

__Description__

---

Miniconda is a free minimal installer for conda. It is a small bootstrap version of Anaconda that includes only conda, Python, the packages they both depend on, and a small number of other useful packages (like pip, zlib, and a few others). If you need more packages, use the conda install command to install from thousands of packages available by default in Anaconda’s public repo, or from other channels, like conda-forge or bioconda. From the Anaconda documentation (https://docs.anaconda.com/miniconda/#quick-command-line-install).

This allows for control over which packages are installed.

<br>

__Installation__

---
<br>

*Mac (macOS)*

```
mkdir -p ~/miniconda3
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```

**This installs miniconda in your home directory (`$HOME [/Users/{username}]`)**

If using bash shell:

`~/miniconda3/bin/conda init bash`

If using zsh shell:

`~/miniconda3/bin/conda init zsh`

<br>

*Windows*

```
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -o miniconda.exe
start /wait "" miniconda.exe /S
del miniconda.exe
```

or

1. Download an executable file for the installer [here](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).
2. Double-click the `.exe` file.
3. Follow the instructions on the screen. Accept default settings.
4. When the installation finishes, from the Start menu, open Anaconda Prompt.
5. Test your installation by running `conda list`. If conda has been installed correctly, a list of installed packages appears.