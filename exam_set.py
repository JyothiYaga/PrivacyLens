"""
PrivacyLens evaluation exam (v1).

30 questions in five categories:
  - gdpr_single (7): questions about GDPR only
  - dpdp_single (7): questions about the DPDP Act only
  - comparison  (8): questions that need both laws
  - detail      (4): specific numbers, deadlines, bodies
  - trap        (4): off-topic questions that must be refused

Fields:
  id               unique question id
  category         one of the categories above
  question         the question as Priya would ask it
  expected_sources list of groups; each group is a list of acceptable citations,
                   and at least one citation from EVERY group must be cited.
                   Example: [["GDPR Article 17"], ["DPDP Section 12"]]
  expected_facts   key facts a correct answer must contain (for the LLM judge)
  should_refuse    True for trap questions
"""

EXAM = [
    # ---------------- GDPR only ----------------
    {
        "id": "G01", "category": "gdpr_single",
        "question": "What does 'personal data' mean under the GDPR?",
        "expected_sources": [["GDPR Article 4"]],
        "expected_facts": [
            "Personal data is any information relating to an identified or identifiable natural person.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G02", "category": "gdpr_single",
        "question": "What are the lawful bases for processing personal data under the GDPR?",
        "expected_sources": [["GDPR Article 6"]],
        "expected_facts": [
            "Processing is lawful only if at least one basis applies.",
            "The bases are consent, contract, legal obligation, vital interests, public task and legitimate interests.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G03", "category": "gdpr_single",
        "question": "What conditions apply to consent under the GDPR?",
        "expected_sources": [["GDPR Article 7"]],
        "expected_facts": [
            "The controller must be able to demonstrate that consent was given.",
            "The data subject can withdraw consent at any time.",
            "Withdrawing consent must be as easy as giving it.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G04", "category": "gdpr_single",
        "question": "When does an organisation have to appoint a Data Protection Officer under the GDPR?",
        "expected_sources": [["GDPR Article 37"]],
        "expected_facts": [
            "A DPO is required when processing is carried out by a public authority or body.",
            "A DPO is required when core activities involve regular and systematic monitoring of data subjects on a large scale.",
            "A DPO is required when core activities involve large-scale processing of special categories of data or criminal conviction data.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G05", "category": "gdpr_single",
        "question": "What is the right to data portability under the GDPR?",
        "expected_sources": [["GDPR Article 20"]],
        "expected_facts": [
            "The data subject can receive their personal data in a structured, commonly used and machine-readable format.",
            "The data subject can transmit that data to another controller.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G06", "category": "gdpr_single",
        "question": "When is a data protection impact assessment required under the GDPR?",
        "expected_sources": [["GDPR Article 35"]],
        "expected_facts": [
            "It is required when processing is likely to result in a high risk to the rights and freedoms of natural persons.",
            "It must be carried out before the processing.",
        ],
        "should_refuse": False,
    },
    {
        "id": "G07", "category": "gdpr_single",
        "question": "What are the principles for processing personal data under the GDPR?",
        "expected_sources": [["GDPR Article 5"]],
        "expected_facts": [
            "The principles include lawfulness, fairness and transparency, purpose limitation, data minimisation, accuracy, storage limitation, and integrity and confidentiality.",
            "The controller is responsible for demonstrating compliance (accountability).",
        ],
        "should_refuse": False,
    },

    # ---------------- DPDP only ----------------
    {
        "id": "D01", "category": "dpdp_single",
        "question": "Who is a Data Fiduciary under the DPDP Act?",
        "expected_sources": [["DPDP Section 2"]],
        "expected_facts": [
            "A Data Fiduciary is any person who alone or with others determines the purpose and means of processing personal data.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D02", "category": "dpdp_single",
        "question": "What must a notice to the Data Principal contain under the DPDP Act?",
        "expected_sources": [["DPDP Section 5"]],
        "expected_facts": [
            "The notice must describe the personal data and the purpose of processing.",
            "It must explain how the Data Principal can exercise their rights, including withdrawing consent and grievance redressal.",
            "It must explain how to complain to the Data Protection Board.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D03", "category": "dpdp_single",
        "question": "For which legitimate uses can personal data be processed without consent under the DPDP Act?",
        "expected_sources": [["DPDP Section 7"]],
        "expected_facts": [
            "Data voluntarily provided for a specified purpose where the person has not objected.",
            "Purposes such as legal obligations, medical emergencies and employment-related purposes are legitimate uses.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D04", "category": "dpdp_single",
        "question": "What extra obligations does a Significant Data Fiduciary have under the DPDP Act?",
        "expected_sources": [["DPDP Section 10"]],
        "expected_facts": [
            "It must appoint a Data Protection Officer based in India.",
            "It must appoint an independent data auditor.",
            "It must carry out periodic Data Protection Impact Assessments and audits.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D05", "category": "dpdp_single",
        "question": "What duties does a Data Principal have under the DPDP Act?",
        "expected_sources": [["DPDP Section 15"]],
        "expected_facts": [
            "A Data Principal must not impersonate another person.",
            "A Data Principal must not suppress material information or register a false or frivolous grievance.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D06", "category": "dpdp_single",
        "question": "Can personal data be transferred outside India under the DPDP Act?",
        "expected_sources": [["DPDP Section 16"]],
        "expected_facts": [
            "Transfer is allowed, but the Central Government may restrict transfers to countries or territories it notifies.",
        ],
        "should_refuse": False,
    },
    {
        "id": "D07", "category": "dpdp_single",
        "question": "What is the right to nominate under the DPDP Act?",
        "expected_sources": [["DPDP Section 14"]],
        "expected_facts": [
            "A Data Principal can nominate another individual to exercise their rights in the event of death or incapacity.",
        ],
        "should_refuse": False,
    },

    # ---------------- Comparison (both laws) ----------------
    {
        "id": "C01", "category": "comparison",
        "question": "Can a user make a company delete their data under the GDPR and the DPDP Act?",
        "expected_sources": [["GDPR Article 17"], ["DPDP Section 12"]],
        "expected_facts": [
            "Under the GDPR the data subject has a right to erasure.",
            "Under the DPDP Act the Data Principal has a right to erasure of personal data.",
            "Both laws allow retention where required for legal compliance or other specified reasons.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C02", "category": "comparison",
        "question": "When must a personal data breach be reported under the GDPR and the DPDP Act?",
        "expected_sources": [["GDPR Article 33"], ["DPDP Section 8"]],
        "expected_facts": [
            "Under the GDPR the controller must notify the supervisory authority within 72 hours where feasible.",
            "Under the DPDP Act the Data Fiduciary must inform the Board and each affected Data Principal in the prescribed form and manner; the Act itself does not set a specific deadline.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C03", "category": "comparison",
        "question": "How do the GDPR and the DPDP Act treat children's personal data?",
        "expected_sources": [["GDPR Article 8"], ["DPDP Section 9"]],
        "expected_facts": [
            "Under the GDPR, for online services, consent for a child below 16 must be given or authorised by a parent, and member states may lower the age to no less than 13.",
            "Under the DPDP Act, processing a child's data requires verifiable consent of the parent.",
            "The DPDP Act prohibits tracking, behavioural monitoring and targeted advertising directed at children.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C04", "category": "comparison",
        "question": "What right does a person have to access information about their personal data under each law?",
        "expected_sources": [["GDPR Article 15"], ["DPDP Section 11"]],
        "expected_facts": [
            "Under the GDPR the data subject can obtain confirmation of processing and access to their personal data.",
            "Under the DPDP Act the Data Principal can obtain a summary of their personal data and processing activities.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C05", "category": "comparison",
        "question": "What makes consent valid under the GDPR and under the DPDP Act?",
        "expected_sources": [["GDPR Article 7", "GDPR Article 4"], ["DPDP Section 6"]],
        "expected_facts": [
            "Under the DPDP Act consent must be free, specific, informed, unconditional and unambiguous, with a clear affirmative action.",
            "Under both laws consent can be withdrawn.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C06", "category": "comparison",
        "question": "What are the maximum penalties under the GDPR and the DPDP Act?",
        "expected_sources": [["GDPR Article 83"], ["DPDP Schedule"]],
        "expected_facts": [
            "The GDPR allows fines up to 20 million euros or 4% of total worldwide annual turnover, whichever is higher.",
            "The highest DPDP penalty is up to 250 crore rupees, for failing to take reasonable security safeguards.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C07", "category": "comparison",
        "question": "Can a person get inaccurate personal data corrected under both laws?",
        "expected_sources": [["GDPR Article 16"], ["DPDP Section 12"]],
        "expected_facts": [
            "Under the GDPR the data subject has a right to rectification of inaccurate personal data.",
            "Under the DPDP Act the Data Principal has a right to correction, completion and updating of personal data.",
        ],
        "should_refuse": False,
    },
    {
        "id": "C08", "category": "comparison",
        "question": "How do the GDPR and the DPDP Act handle transfers of personal data to other countries?",
        "expected_sources": [["GDPR Article 44", "GDPR Article 45", "GDPR Article 46"], ["DPDP Section 16"]],
        "expected_facts": [
            "The GDPR allows transfers based on an adequacy decision or appropriate safeguards.",
            "The DPDP Act allows transfers unless the Central Government restricts transfers to notified countries.",
        ],
        "should_refuse": False,
    },

    # ---------------- Specific details ----------------
    {
        "id": "S01", "category": "detail",
        "question": "What is the penalty under the DPDP Act for failing to take reasonable security safeguards to prevent a personal data breach?",
        "expected_sources": [["DPDP Schedule"]],
        "expected_facts": [
            "The penalty may extend to 250 crore rupees.",
        ],
        "should_refuse": False,
    },
    {
        "id": "S02", "category": "detail",
        "question": "How long does a controller have to respond to a data subject's request under the GDPR?",
        "expected_sources": [["GDPR Article 12"]],
        "expected_facts": [
            "The controller must respond without undue delay and within one month.",
            "The period can be extended by two further months where necessary.",
        ],
        "should_refuse": False,
    },
    {
        "id": "S03", "category": "detail",
        "question": "What is the maximum penalty for a Data Principal who breaches their duties under the DPDP Act?",
        "expected_sources": [["DPDP Schedule", "DPDP Section 15"]],
        "expected_facts": [
            "The penalty may extend to ten thousand rupees.",
        ],
        "should_refuse": False,
    },
    {
        "id": "S04", "category": "detail",
        "question": "Where can a person appeal against an order of the Data Protection Board of India?",
        "expected_sources": [["DPDP Section 29"]],
        "expected_facts": [
            "Appeals go to the Appellate Tribunal, the Telecom Disputes Settlement and Appellate Tribunal.",
            "The appeal must be filed within sixty days.",
        ],
        "should_refuse": False,
    },

    # ---------------- Traps (must refuse) ----------------
    {
        "id": "T01", "category": "trap",
        "question": "What is the GST rate on restaurant services in India?",
        "expected_sources": [],
        "expected_facts": [],
        "should_refuse": True,
    },
    {
        "id": "T02", "category": "trap",
        "question": "How do I file my income tax return in India?",
        "expected_sources": [],
        "expected_facts": [],
        "should_refuse": True,
    },
    {
        "id": "T03", "category": "trap",
        "question": "What does the California Consumer Privacy Act say about selling personal data?",
        "expected_sources": [],
        "expected_facts": [],
        "should_refuse": True,
    },
    {
        "id": "T04", "category": "trap",
        "question": "Who won the 2023 Cricket World Cup?",
        "expected_sources": [],
        "expected_facts": [],
        "should_refuse": True,
    },
]

assert len(EXAM) == 30, f"Expected 30 questions, got {len(EXAM)}"
assert len({q["id"] for q in EXAM}) == 30, "Question ids must be unique"