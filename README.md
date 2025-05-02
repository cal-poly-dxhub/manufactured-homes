# Manufactured Homes Solution

## Collaboration
Thanks for your interest in our solution. Having specific examples of replication and cloning allows us to continue to grow and scale our work. If you clone or download this repository, kindly shoot us a quick email to let us know you are interested in this work!

[wwps-cic@amazon.com]

# Disclaimers
**Customers are responsible for making their own independent assessment of the information in this document.**

**This document:**

(a) is for informational purposes only,

(b) represents current AWS product offerings and practices, which are subject to change without notice, and

(c) does not create any commitments or assurances from AWS and its affiliates, suppliers or licensors. AWS products or services are provided “as is” without warranties, representations, or conditions of any kind, whether express or implied. The responsibilities and liabilities of AWS to its customers are controlled by AWS agreements, and this document is not part of, nor does it modify, any agreement between AWS and its customers.

(d) is not to be considered a recommendation or viewpoint of AWS

**Additionally, all prototype code and associated assets should be considered:**
(a) as-is and without warranties

(b) not suitable for production environments

(d) to include shortcuts in order to support rapid prototyping such as, but not limitted to, relaxed authentication and authorization and a lack of strict adherence to security best practices

**All work produced is open source. More information can be found in the GitHub repo.**

## Authors
- Dhvani Goel - [dhgoel@calpoly.edu]
- Sharon Liang - [sliang19@calpoly.edu]

## Table of Contents
- Overview
- Deployment

## Overview
The DxHub developed a web-based tool to extract key housing data from scanned PDFs using Amazon Textract. Designed to support the City of San Luis Obispo’s housing upgrade concierge service, this tool automates manual document review for faster, more reliable processing.

The extractor includes the following features:
- Upload scanned title and registration documents (PDF)
- Extract key fields:
  - Decal Number  
  - Manufacturer & Model  
  - Manufactured & First Sold Dates  
  - Serial Numbers, HUD Labels, Length & Width  
  - Record Conditions  
  - Sale/Transfer Info (Price and Date)  
  - Situs Address  
  - Last Reported Registered Owner  
- Handle incomplete documents gracefully (e.g. missing sale data or ownership)
- View output instantly in structured JSON format
- (Planned) Export results as CSV for integration into existing workflows
- Streamlit-based frontend for fast deployment and ease of use
- Secure handling of uploaded files (temporary storage, auto-deletion)
- Modular backend for future scaling across housing parks

## Steps to Deploy and Configure the System

### Prerequisites
Before deployment, ensure you have: 
- An AWS account
- API credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN)
- Python 3 installed

### Clone the Repository
- Install git using this command
  ```
  sudo yum install git
  ```
- Clone the repository
  ```
  git clone https://github.com/cal-poly-dxhub/manufactured-homes.git
  ```

### Install Python Dependencies
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Run the streamlit app
```
streamlit run src/app.py
```

## Support
For any queries or issues, please contact:
- Dhvani Goel, Software Developer Intern - dhgoel@calpoly.edu
- Sharon Liang, Software Developer Intern - sliang19@calpoly.edu
