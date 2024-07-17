# Flight Delay Insurance, Web3 Platform
![Group 6 (1)](https://github.com/user-attachments/assets/53b590d8-a603-42c8-ab7e-c641af4a235b)

## ABSTRACT
The objective of this report is to demonstrate the potential of Ethereum as a platform for flight delay insurance. Our solution allows customers to purchase flight delay insurance that automatically triggers payouts based on real-time flight data by leveraging a decentralized marketplace on Ethereum. This paper presents a business strategy that emphasizes efficiency, cost savings, and market transparency, as well as a technical implementation that includes machine learning models for delay prediction and dynamic insurance rates. Our analysis indicates that this blockchain-based solution offers an alternative to traditional insurance, with the potential to reduce fraud and increase customer satisfaction through automated claims processing. 

## Introduction
In the modern era, air travel has become a fundamental aspect of our daily lives. However, flight delays are a common occurrence that can result in substantial financial losses for both passengers and airlines. While traditional insurance provides a solution to mitigate these losses, it is often associated with high administrative costs and delays in processing claims, which can be problematic for both passengers and airlines alike. Blockchain technology and smart contracts have the potential to transform the way we address flight delays, offering a more efficient, transparent, and cost-effective approach. Smart contracts are self-executing digital contracts stored on a decentralized network, such as the blockchain. They automatically execute agreements when certain conditions are met, eliminating the need for manual processing. 

Our proposal is to purchase flight delay insurance via a decentralized marketplace on Ethereum. These smart contracts monitor flight data in real time and automatically trigger a payout to the insured traveler in the event of a delay that meets predefined conditions. This system streamlines the claims settlement process, enhances transparency, and mitigates the risk of fraud. This report provides a comprehensive examination of the market analysis, technical solution, business model, SWOT analysis, and legal aspects of implementing such a system. It demonstrates how blockchain technology can enhance the efficiency and reliability of flight delay insurance.

# Market Analysis

## Market Size
The market value of global travel insurance is estimated to be 16.8 billion dollars in 2022 and will reach a growth of 20.1% to 2032. Like travel insurance, the number of tourists will increase, so more people will fly in the future. The insurance market is huge, and it will only increase, so they must implement new technologies to make the process faster. Every airline has their own policies, about how they will handle the delayed or cancelled flights.

## Etherisc & Lemonade
First decentralized insurance app, that insures your flight against delays or cancellations. What makes this app different to normal insurance companies is that you get the payment right after the landing. The customers don’t have to registrate the delay to the insurance company, it will automatically get the information about the issue from their own website “Flight Delay”. 

Lemonade is an insurance company, which focuses on Renters, Homeowners, Cars, Pets and Life insurance. They’re using blockchain for fast claim processing.

## What is the difference?
The difference between flight delay insurance and Etherisc is the creation of a marketplace, where investors or in general people can buy and sell those claims. Through machine learning, predictions about delays and cancellations were made, which will help to get a decentralized version of predictions. On the other hand Lemonade doesn’t include flight delay insurance therefore the comparison between flight delay insurance Lemonade is not really there.

# Technical Solutions

## Data Preprocessing
The dataset used for this project spans from August 2019 to August 2023 and was retrieved via the DOT On-Time Reporting Carrier On-Time Performance application, aiming to enable efficient querying and data manipulation. Covering flight delay and cancellation information, the dataset includes variables such as flight routes (origin, destination), event time ranges (minutes, local time), and limited reasons for delays and cancellations. The data retrieval process involved downloading monthly subsets from the DOT’s application and joining them by year. The consolidation process ensured the dataset was up-to-date, with the most current information for 2023 from August. 

Acknowledgement goes to the U.S. Department of Transportation’s Bureau of Transportation Statistics for tracking the on-time performance of domestic flights operated by large air carriers and publishing this data in the DOT’s monthly Air Travel Consumer Report. The dataset can be merged with the “Airline Delay and Cancellation Data, 2009 - 2018,” adopting similar header names, ensuring consistency in data reporting and analysis. 

## Machine Learning
The Flight Delay Insurance project employs machine learning to forecast flight delays and adjust insurance premiums in real-time based on the predicted delay duration. The program commences with the loading and cleansing of flight data, the extraction of key time-related features and the separation of datasets for classification and regression tasks.  

In the training phase, the program addresses the issue of class imbalance by computing class weights and training a RandomForestClassifier with these weights. The model's performance is evaluated using several metrics, including ROC AUC, accuracy, classification reports and confusion matrices. A RandomForestRegressor is trained to estimate the duration of delays for flights that have been delayed, with the resulting estimate evaluated using the Mean Absolute Error (MAE) metric. 

The WebApp class implements a Flask web application that provides a predictive service for the pricing of flight delay insurance. The application employs pre-trained machine learning models to forecast flight delays and to calculate insurance premiums on a dynamic basis, with the insurance premium being calculated according to the predicted delay duration. 

The predict method defines a Flask route (/predict) that handles POST requests. It processes the request's JSON data, transforming it into a Pandas DataFrame. Subsequently, the classifier model predicts the probability of a delay, and if this probability exceeds a threshold (0.05), the regressor model predicts the delay duration. The insurance cost is then determined based on these predictions, and the results are returned as a JSON response. 

## Introduction: Buying Insurance Using Ethereum 
In the realm of decentralized finance (DeFi), Ethereum has enabled innovative solutions beyond simple transactions and investments. One such application is the ability to purchase insurance directly on the blockchain. This provides a transparent, immutable, and accessible way for individuals to secure insurance coverage without traditional intermediaries.

## Understanding the InsuranceEngine Contract 
The InsuranceEngine contract is a foundational smart contract deployed on the Ethereum blockchain. Its purpose is to manage and facilitate the purchase of insurance policies using ERC20 tokens. Here’s a breakdown of how this contract operates: 

Token Integration: The contract is initialized with an ERC20 token interface (IERC20) which serves as the currency for purchasing insurance policies. This token acts as a unit of value within the contract, enabling seamless transactions. 

Policy Management: Each insurance policy is represented as a structured entity within the contract. It includes essential attributes such as a unique identifier (id) and a price (price) in ERC20 tokens. Policies are stored and managed using efficient data structures to ensure scalability and clarity. 

Owner Privileges: The contract leverages the Ownable pattern, granting special permissions to the contract deployer or owner. These permissions allow the owner to add new insurance policies (addInsurancePolicy) and update existing policy prices (updateInsurancePrice). This flexibility ensures that insurance offerings can adapt to market dynamics and user demands. 

Insurance Purchase Process: Users interact with the contract to purchase insurance. By invoking the purchaseInsurance function with a specific policy ID, users initiate a transaction. This function verifies the validity of the policy, checks if the user isn’t already insured, and facilitates the transfer of ERC20 tokens from the user to the contract. Once completed, the user is marked as insured under the specified policy. 

Transparency and Accessibility: The contract promotes transparency by allowing anyone to query the available insurance policies and their respective prices (getInsurancePolicies). This function provides potential customers with clear visibility into available coverage options, fostering trust and informed decision-making. 

Verification of Coverage: For transparency and peace of mind, the contract includes a function (isInsured) that enables users to verify their insurance status under a specific policy. By querying this function, users can confirm whether they are currently insured under a given policy.

## Conclusion 
The InsuranceEngine contract exemplifies how Ethereum’s smart contract capabilities can revolutionize the insurance industry. By leveraging blockchain technology, the contract facilitates secure, efficient, and transparent insurance transactions using ERC20 tokens. This not only eliminates traditional barriers associated with intermediaries but also enhances accessibility and trust in insurance services within the decentralized ecosystem. 

## Beta Version Deployment 
The beta version of the InsuranceEngine contract is deployed on the Speoleite ERC network at the following address: 0x7F0b6c053DeF457ebbaCcBed66d688d5636C67ae.

This deployment enables users to explore and utilize decentralized insurance solutions powered by Ethereum and ERC20 tokens. 

# BUSINESS MODEL
## Case/Problem
As already mentioned, the problems in this case are flight delays and cancellations who are causing significant inconvenience. The processing time of claims are a huge problem and every so often the claims filer wouldn’t get any payment due to different reasons and for those claims are causing high administrative costs for travel delay insurances.
## Customers
Main target Agents are travelers and Airlines or Travel Agencies. Mostly frequent travelers will more likely experience a delay or cancellation during their flight than people who travel less. Travel agencies could use the blockchain technology to implement in their system to enhance their products. 
## Product/Solution Idea
Traditional flight insurance is based on manual processing so creating a decentralized insurance platform with Ethereum will be solution with a market to sell the claims.
# SWOT ANALYSIS
Strengths:
- Efficiency: Claims will be processed automatically
- Cost saving: In traditional Flight delay insurance there are high administrative costs involved and with the following innovation the costs could be reduced.
- Innovation
- Transparency

Weaknesses:
  - Regulatory problems: Rules and Regulations are different in every country so the implementation in every country will be a challenge.
 
Opportinities:
- Fraud detection: Fake claims are hard to verify manually, using blockchain will make it easier to verify the claims truth.
- Market Expansion

Threats/Challenges:
- New technology: The biggest challenge will be to implement the landscape of insurance across different countries and their regulations. Convincing and educating people about technology and their positives. Most people have the fear of the unknown and fear of failure.

# Legal Analysis
Our company must comply with several legal considerations. Firstly, smart contracts can potentially automate insurance claims for flight delays based on predefined conditions. It is crucial to ascertain whether these contracts are intended to serve merely as execution tools or legally binding agreements to guarantee their enforceability. For this project, implementing these contracts as smart legal contracts will ensure that they are legally binding, as they fulfill the basic requirements of offer, acceptance, consideration, and mutual intent. Secondly, we must decide whether to register as an insurance company at the state or federal level, taking into account regulatory compliance and the nature of our business. Insurance companies in the United States are typically subject to state-level regulation, as outlined in the McCarran-Ferguson Act of 1945. Registering in states like Wyoming, which is known for its favorable business environment and blockchain-friendly legislation, offers the added benefit of lower administrative costs and regulatory burdens. Wyoming's innovative legal framework, specifically the Wyoming Utility Token Act, provides a clear legal status for utility tokens and a supportive environment for blockchain businesses. Third, the Dodd-Frank Act, particularly Section V, has significant implications for financial services, including insurance. This section places a strong emphasis on consumer protection, risk management, and transparency. Our practices are designed to ensure that we do not engage in any unfair or deceptive acts. Compliance with these regulations is consistent with the Federal Trade Commission Act (FTC Act) Section 5, which prohibits unfair or deceptive practices in commerce. Fourth, we are required to comply with state-specific privacy laws, such as the California Consumer Privacy Act (CCPA), which imposes strict data protection measures. It is of the utmost importance to ensure data security and protect customer privacy to avoid legal liability. In addition, consumer protection laws under Section 5 of the FTC Act require that our advertising, promotional materials, and overall business practices be transparent and not misleading. This encompasses adherence to guidelines set forth by the Consumer Financial Protection Bureau (CFPB). Fifth, our token classification must comply with the relevant regulations. Our tokens are designed with the primary purpose of facilitating the purchase of insurance coverage, rather than as investment vehicles. This classification defines them as utility tokens. This categorization helps to avoid classification as securities, thereby reducing the regulatory burdens associated with such a classification. It is therefore essential to ensure that comprehensive documentation and structuring are in place to guarantee compliance with the Howey test, which determines whether an asset qualifies as an investment contract. Finally, it is essential to have an effective dispute-resolution mechanism to address potential issues. Options include pre-litigation settlements, online dispute resolution (ODR) mechanisms, traditional court systems, or arbitration. On-chain dispute resolution platforms, such as Kleros or JUR.io, offer decentralized alternatives that can resolve disputes efficiently without conventional legal systems. Given our business nature, on-chain dispute resolution mechanisms are suitable due to their transparency and efficiency. Platforms like Kleros use blockchain technology for transparent and efficient resolution processes, where parties submit evidence and receive decisions from a decentralized jury, offering a novel approach to dispute resolution. 

# Conclusions
This report looks at the integration of Ethereum into the insurance industry, with a particular focus on airline delay insurance. It highlights the potential of Ethereum to transform the industry through improved efficiency, cost savings and transparency. The use of smart contracts to automate claims leads to a significant reduction in the administrative burden as well as an acceleration in processing time compared to conventional methods. The immutability of the blockchain ensures a transparent and reliable transaction history, while its robust security features minimize the risk of fraudulent claims. The Ethereum platform offers several benefits. These include greater efficiency through the automated processing of claims, lower operational costs through the elimination of intermediaries, greater transparency through the immutable record, and improved security against fraudulent claims. 

However, there are also some challenges associated with this platform. Navigating the divergent regulatory landscapes in the various jurisdictions can be complex and time-consuming. A key challenge is gaining the trust of consumers, particularly those who are unfamiliar with blockchain technology. Furthermore, reliance on advanced technology requires significant investment in education and infrastructure, which can slow adoption. There is also the possibility that established, traditional insurance companies will become serious competitors if they implement similar technologies. Another issue that needs to be addressed is the volatility of gas prices on the Ethereum network. This can lead to unpredictably high transaction costs and thus affect the overall profitability of the platform. 

Although several challenges can be identified, the proposed blockchain-based platform for flight delay insurance is considered promising. Provided that regulatory, trust-related and technological hurdles are overcome, it could revolutionize the insurance industry and set a new standard for automated and transparent insurance solutions. Such innovation could lead to a more efficient, cost-effective and trustworthy insurance experience for consumers worldwide. 

# Author Contributions
## Contributors
- Darryl Nyamayaro (University of Cape Town)
- Eren Tomak (Baskent University)
- Mauro Dünki (University of Zurich)
- Mikhail Filippov (University of Mannheim)
- Sulagsaan Jeyekumar (University of Zurich)

All authors conceived and designed the project idea. Below is a detailed overview of each author's specific contributions. All authors reviewed and approved the final version of this document. 

Abstract, Introdcuction and Conclusion: 
- Sulagsaan Jeyekumar 
- Mauro Dünki 

Business Section: 
- Sulagsaan Jeyekumar: Market Analysis and Business Case 
- Mauro Dünki: Market Analysis 
- Eren Tokmak: Economics of the Token 

Technical Section: 
- Eren Tokmak
- Mikhail Filippov: Data Gathering & Preprocessing, Predictive Analysis, Machine Learning, Flask Web Application 
- Darryl Nyamayaro 

Regulatory Section: 
- Mauro Dünki

# References
5 U.S.C. § 45 (1914, as amended in 1994).  

15 U.S.C. § 6701 (1999).  

Allied Market Research, https://www.alliedmarketresearch.com/. (n.d.). Travel Insurance MarketSize, Share, Competitive Landscape and Trend Analysis Report, by insurance cover, by distribution channel, by end user, by age group : Global Opportunity Analysis and Industry Forecast, 2023-2032. Allied Market Research.https://www.alliedmarketresearch.com/travel-insurance market#:~:text=The%20global%20travel%20insurance%20market,before%20or%20during%20a%20trip. 

California Consumer Privacy Act of 2018, Cal. Civ. Code § 1798.100 et seq. (2018, as amended by the California Privacy Rights Act of 2020).  

Dodd-Frank Wall Street Reform and Consumer Protection Act, Pub. L. No. 111-203, § 5, 124 Stat. 1376, 1391 (2010).  

ETHERISC | Make insurance fair and accessible. (n.d.). https://etherisc.com/ 

Gromenko, A. (2022, 3. Oktober). Benefits of Blockchain in Insurance | Code&Care. Code&Care. https://code-care.com/blog/benefits-of-blockchain-in-insurance/ 

Journal of Financial Regulation and Compliance | Emerald Insight. (2024). https://www.emerald.com/insight/1358-1988.htm

Jur.io. (n.d.). Retrieved July 17, 2024, from https://jur.io/  

Kleros. (n.d.). Retrieved July 17, 2024, from https://kleros.io/  

U.S. Securities and Exchange Commission. (2019). Framework for "Investment Contract" Analysis of Digital Assets. Retrieved from https://www.sec.gov/files/dlt-framework.pdf  

Wyo. Stat. § 34-29-106 (2019). 
