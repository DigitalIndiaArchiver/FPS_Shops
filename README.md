# FPS Shops

This repository contains a script to extract and manage a database of Fair Price Shops (FPS) in India. The database includes information about the location, ownership of shops. The source of the data is [IMPDS Portal](https://impds.nic.in/sale/)


## Getting Started

### Prerequisites

Make sure you have Python 3.6+ installed on your system. You can download Python from the [official website](https://www.python.org/).

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/DigitalIndiaArchiver/FPS_Shops.git
    cd FPS_Shops
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Script

The script `script.py` is designed to extract FPS data from the specified source and combine JSON files into a single CSV file.

To run the script, use the following command:

```bash
python script.py