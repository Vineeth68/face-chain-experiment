## Setup

### 1. Prerequisites

Make sure CMake and C++ build tools are installed for compiling `dlib`:

```bash
# Windows (via Conda - recommended for dlib)
conda install -c conda-forge dlib

# Or via pip (requires VS C++ build tools installed)
pip install -r requirements.txt


---
2. Environment Configuration
Copy the example environment file:

bash
cp .env.example .env

---
Populate the required keys in .env:

Code snippet
SERPAPI_API_KEY="your_serpapi_key"
RPC_URL="[https://polygon-amoy-bor-rpc.publicnode.com](https://polygon-amoy-bor-rpc.publicnode.com)"
PRIVATE_KEY="your_testnet_private_key"

---
Usage
Run the pipeline against any target photo:

Bash
cd src
python pipeline.py --image "../test.jpg"

---
To supply search hints (e.g., handles or locations) to narrow web results:

Bash
python pipeline.py --image "../test.jpg" --hint "username or domain"

---
Bypass consent prompts for automated testing:

Bash
python pipeline.py --image "../test.jpg" --skip_consent_prompt

