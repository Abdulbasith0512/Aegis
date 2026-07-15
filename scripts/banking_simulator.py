import asyncio
import random
import uuid
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict, Any
import asyncpg

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aegisai.simulator")

# Configurations
DB_URL = "postgresql://postgres:postgres_password@localhost:5432/aegisai_db"

class SimulatorConfig:
    """Configurable simulation scale parameters."""
    NUM_BRANCHES = 10
    NUM_MERCHANTS = 100
    NUM_EMPLOYEES = 20
    NUM_CUSTOMERS = 10000
    NUM_ACCOUNTS = 15000
    NUM_BENEFICIARIES = 30000
    NUM_DEVICES = 12000
    NUM_TRANSACTIONS = 950000
    
    # Financial Crime Configurations
    FRAUD_RATIO = 0.005 # 0.5% fraud cases
    NUM_AML_CIRCLES = 100 # Circular transfers: A -> B -> C -> A
    NUM_AML_STRUCTURING = 200 # Smurfing: Large deposits split below reporting threshold
    
    START_DATE = datetime.utcnow() - timedelta(days=90)

async def bulk_load_table(conn: asyncpg.Connection, table_name: str, columns: List[str], records: List[Tuple]) -> None:
    """
    Highly optimized bulk data loader using asyncpg's copy interface.
    """
    if not records:
        return
    logger.info(f"Bulk loading {len(records)} rows into '{table_name}'...")
    try:
        await conn.copy_records_to_table(table_name, records=records, columns=columns)
    except Exception as e:
        logger.error(f"Failed to load records into '{table_name}': {e}")
        raise

async def generate_simulation() -> None:
    """
    Main simulator runner. Generates and imports 1,000,000+ realistic rows into PostgreSQL.
    """
    logger.info("Connecting to database...")
    try:
        conn = await asyncpg.connect(DB_URL)
    except Exception as e:
        logger.critical(f"Could not connect to PostgreSQL at {DB_URL}. Make sure docker services are running. Error: {e}")
        return

    logger.info("Seeding relational database tables...")
    
    # 1. Clean old tables securely to allow clean runs
    await conn.execute("""
        TRUNCATE compliance_reports, incidents, alerts, chaos_tests, audit_logs, 
                 human_reviews, explanations, policy_checks, trust_scores, consensus_votes, 
                 predictions, model_versions, ai_agents, transactions, beneficiaries, 
                 accounts, customers, devices, merchants, branches, users, role_permissions, 
                 permissions, roles CASCADE;
    """)

    cfg = SimulatorConfig()

    # --- 2. Roles, Permissions & Employees (Users) ---
    logger.info("Generating security and user records...")
    permissions = [
        (uuid.uuid4(), "read:users", "Read users info", datetime.utcnow()),
        (uuid.uuid4(), "write:users", "Create/edit users", datetime.utcnow()),
        (uuid.uuid4(), "delete:users", "Delete users", datetime.utcnow()),
        (uuid.uuid4(), "read:admin", "Read admin metrics", datetime.utcnow()),
        (uuid.uuid4(), "write:admin", "Update admin parameters", datetime.utcnow()),
        (uuid.uuid4(), "read:transactions", "Inspect transaction telemetry", datetime.utcnow()),
        (uuid.uuid4(), "write:policies", "Update security policies", datetime.utcnow()),
        (uuid.uuid4(), "execute:chaos", "Run failure injections", datetime.utcnow()),
        (uuid.uuid4(), "execute:agents", "Trigger agent runs", datetime.utcnow())
    ]
    await bulk_load_table(conn, "permissions", ["id", "name", "description", "created_at"], permissions)

    roles = [
        (uuid.uuid4(), "admin", "Super Administrator details", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "auditor", "Compliance auditor details", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "viewer", "Read-only operations viewer", datetime.utcnow(), datetime.utcnow())
    ]
    await bulk_load_table(conn, "roles", ["id", "name", "description", "created_at", "updated_at"], roles)

    # Link permissions to roles
    role_perms = []
    admin_role_id = roles[0][0]
    auditor_role_id = roles[1][0]
    viewer_role_id = roles[2][0]

    for p in permissions:
        # Admin gets everything
        role_perms.append((admin_role_id, p[0]))
        # Auditor gets read:users, read:admin, read:transactions, write:policies
        if p[1] in ["read:users", "read:admin", "read:transactions", "write:policies"]:
            role_perms.append((auditor_role_id, p[0]))
        # Viewer gets read:transactions
        if p[1] in ["read:transactions"]:
            role_perms.append((viewer_role_id, p[0]))
            
    await bulk_load_table(conn, "role_permissions", ["role_id", "permission_id"], role_perms)

    # Generate Employees
    # Hashed value for 'aegisai_admin_password'
    default_pw_hash = "$2b$12$Z0bC2G/RkG7oVlVf4C2tIeR4Yc9Fv46n1vQ1234567890abcdefg" 
    employees = []
    employee_ids = []
    for i in range(cfg.NUM_EMPLOYEES):
        uid = uuid.uuid4()
        role_id = admin_role_id if i == 0 else (auditor_role_id if i % 2 == 0 else viewer_role_id)
        email = f"employee_{i}@aegisai.bank"
        employees.append((uid, role_id, email, default_pw_hash, True, datetime.utcnow(), datetime.utcnow()))
        employee_ids.append(uid)
    await bulk_load_table(conn, "users", ["id", "role_id", "email", "hashed_password", "is_active", "created_at", "updated_at"], employees)

    # --- 3. Branches & Merchants ---
    logger.info("Generating static entity structures...")
    branches = []
    branch_ids = []
    cities = ["London", "New York", "Tokyo", "Paris", "Frankfurt", "Singapore", "Sydney", "Geneva", "Toronto", "Hong Kong"]
    for i in range(cfg.NUM_BRANCHES):
        bid = uuid.uuid4()
        branch_code = f"BR-{100+i}"
        name = f"{cities[i % len(cities)]} Banking Center"
        branches.append((bid, branch_code, name, cities[i % len(cities)], datetime.utcnow()))
        branch_ids.append(bid)
    await bulk_load_table(conn, "branches", ["id", "branch_code", "name", "location", "created_at"], branches)

    merchants = []
    merchant_ids = []
    mcc_categories = [
        ("5411", "Grocery Stores"), ("5541", "Service Stations"), ("5812", "Eating Places"),
        ("5814", "Fast Food Restaurants"), ("4899", "Cable/Utilities"), ("7995", "Gambling"),
        ("3000", "Airlines"), ("7011", "Hotels/Lodging"), ("5311", "Department Stores")
    ]
    for i in range(cfg.NUM_MERCHANTS):
        mid = uuid.uuid4()
        code = f"MERCH-{10000+i}"
        mcc, name_desc = mcc_categories[i % len(mcc_categories)]
        mname = f"Merchant {i} - {name_desc}"
        merchants.append((mid, code, mname, mcc, datetime.utcnow()))
        merchant_ids.append(mid)
    await bulk_load_table(conn, "merchants", ["id", "merchant_code", "name", "category_code", "created_at"], merchants)

    # --- 4. Customers & Accounts ---
    logger.info("Generating customer and financial account demographics...")
    customers = []
    customer_ids = []
    first_names = ["John", "Sarah", "David", "Emma", "Michael", "Sophia", "Daniel", "Olivia", "James", "Isabella", "William", "Mia", "Alexander", "Emily", "Robert", "Charlotte", "Joseph", "Amelia", "Richard", "Evelyn"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    for i in range(cfg.NUM_CUSTOMERS):
        cid = uuid.uuid4()
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"customer_{i}_{first.lower()}_{last.lower()}@gmail.com"
        phone = f"+1-555-{1000000+i}"
        risk = "high" if i % 100 == 0 else ("medium" if i % 10 == 0 else "low")
        customers.append((cid, None, first, last, email, phone, risk, "active", datetime.utcnow(), datetime.utcnow()))
        customer_ids.append(cid)
    await bulk_load_table(conn, "customers", ["id", "user_id", "first_name", "last_name", "email", "phone", "risk_level", "status", "created_at", "updated_at"], customers)

    accounts = []
    account_ids = []
    account_customer_map = {}
    for i in range(cfg.NUM_ACCOUNTS):
        aid = uuid.uuid4()
        cid = random.choice(customer_ids)
        acc_num = f"ACC-{100000000+i}"
        acc_type = "checking" if i % 2 == 0 else "savings"
        
        # Log-Normal Wealth distribution (majority have small balances, few have millions)
        balance = round(random.lognormvariate(8.5, 1.8), 2)
        accounts.append((aid, cid, acc_num, acc_type, balance, "USD", "active", datetime.utcnow(), datetime.utcnow()))
        account_ids.append(aid)
        
        if cid not in account_customer_map:
            account_customer_map[cid] = []
        account_customer_map[cid].append(aid)
    await bulk_load_table(conn, "accounts", ["id", "customer_id", "account_number", "account_type", "balance", "currency", "status", "created_at", "updated_at"], accounts)

    # --- 5. Beneficiaries ---
    logger.info("Generating pre-authorized transfer beneficiaries...")
    beneficiaries = []
    beneficiary_ids = []
    for i in range(cfg.NUM_BENEFICIARIES):
        bid = uuid.uuid4()
        source_aid = random.choice(account_ids)
        target_acc_num = f"ACC-{200000000+i}"
        beneficiaries.append((bid, source_aid, f"Beneficiary {i}", target_acc_num, f"BANK-{1000+i%50}", datetime.utcnow()))
        beneficiary_ids.append(bid)
    await bulk_load_table(conn, "beneficiaries", ["id", "account_id", "nickname", "beneficiary_account_number", "bank_code", "created_at"], beneficiaries)

    # --- 6. Devices ---
    logger.info("Generating terminal device telemetry databases...")
    devices = []
    device_ids = []
    os_list = ["iOS 16.5", "Android 13", "Windows 11", "macOS Ventura", "Android 12", "iOS 17.0"]
    browsers = ["Chrome/114.0", "Safari/16.5", "Firefox/114.0", "Edge/114.0"]
    for i in range(cfg.NUM_DEVICES):
        did = uuid.uuid4()
        fingerprint = hashlib.sha256(f"dev-fingerprint-{i}".encode()).hexdigest()[:20]
        ip = f"{random.randint(24, 220)}.{random.randint(10, 250)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        ua = f"Mozilla/5.0 ({random.choice(os_list)}) {random.choice(browsers)}"
        os_name = random.choice(os_list)
        is_em = True if i % 200 == 0 else False
        lat = 30.0 + random.uniform(-10, 20)
        long_val = -80.0 + random.uniform(-20, 40)
        devices.append((did, fingerprint, ip, ua, os_name, is_em, lat, long_val, datetime.utcnow()))
        device_ids.append(did)
    await bulk_load_table(conn, "devices", ["id", "fingerprint", "ip_address", "user_agent", "os", "is_emulator", "location_lat", "location_long", "created_at"], devices)

    # --- 7. AI Agents & Versions ---
    logger.info("Generating AI Agent control structures...")
    agents = [
        (uuid.uuid4(), "fraud-agent", "Fraud detection classifier", "active", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "aml-agent", "AML structuring and graph checks", "active", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "kyc-agent", "Document matches", "active", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "behavior-agent", "Customer behavioral deviation", "active", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "device-agent", "Emulator and proxy warnings", "active", datetime.utcnow(), datetime.utcnow()),
        (uuid.uuid4(), "compliance-agent", "Deterministic compliance rule engine", "active", datetime.utcnow(), datetime.utcnow())
    ]
    await bulk_load_table(conn, "ai_agents", ["id", "name", "description", "status", "created_at", "updated_at"], agents)

    versions = []
    agent_version_map = {}
    for a in agents:
        vid = uuid.uuid4()
        versions.append((vid, a[0], "v1.0.0", hashlib.sha256(a[1].encode()).hexdigest()[:15], 0.96, True, datetime.utcnow()))
        agent_version_map[a[1]] = vid
    await bulk_load_table(conn, "model_versions", ["id", "agent_id", "version_string", "parameters_hash", "accuracy_benchmark", "is_active", "deployed_at"], versions)

    # --- 8. Generate Transactions stream (Bulk load in chunks) ---
    logger.info("Simulating over 950,000 transaction records with integrated behaviors...")
    
    # Store temporary lists for later governance tables
    sampled_tx_ids = []
    fraud_tx_ids = []
    
    # Generate bulk transactional data arrays in memory
    total_tx_to_gen = cfg.NUM_TRANSACTIONS
    chunk_size = 100000
    
    tx_columns = [
        "id", "account_id", "beneficiary_id", "merchant_id", "branch_id", "device_id", 
        "amount", "currency", "transaction_type", "status", "reference_number", "initiated_at", "completed_at"
    ]
    
    tx_count = 0
    tx_time_delta = (datetime.utcnow() - cfg.START_DATE) / total_tx_to_gen
    
    # Pre-select some data to speed up loop execution
    account_ids_arr = list(account_ids)
    beneficiary_ids_arr = list(beneficiary_ids)
    merchant_ids_arr = list(merchant_ids)
    branch_ids_arr = list(branch_ids)
    device_ids_arr = list(device_ids)
    
    while tx_count < total_tx_to_gen:
        chunk_records = []
        gen_limit = min(chunk_size, total_tx_to_gen - tx_count)
        
        for _ in range(gen_limit):
            tx_id = uuid.uuid4()
            acc_id = random.choice(account_ids_arr)
            
            # Categorize transaction type realistically
            rand_val = random.random()
            
            beneficiary_id = None
            merchant_id = None
            branch_id = None
            device_id = None
            
            if rand_val < 0.40: # Card purchase at merchant
                tx_type = "payment"
                merchant_id = random.choice(merchant_ids_arr)
                amount = round(random.exponential(scale=45.0) + 1.5, 2) # Exponential purchase sizes
                device_id = random.choice(device_ids_arr)
            elif rand_val < 0.85: # Transfer to beneficiary
                tx_type = "transfer"
                beneficiary_id = random.choice(beneficiary_ids_arr)
                amount = round(random.lognormvariate(5.0, 1.5), 2)
                device_id = random.choice(device_ids_arr)
            else: # Withdrawal/Deposit at Branch/ATM
                tx_type = "withdrawal" if random.random() < 0.6 else "deposit"
                branch_id = random.choice(branch_ids_arr)
                amount = round(random.randint(10, 500) * 1.0, 2)
            
            # Date linear mapping progression
            initiated_at = cfg.START_DATE + (tx_count * tx_time_delta)
            completed_at = initiated_at + timedelta(seconds=random.randint(2, 60))
            
            ref_num = f"REF-{1000000000+tx_count}"
            
            # Inject statistical Fraud Case profile
            status = "approved"
            is_fraud = False
            if random.random() < cfg.FRAUD_RATIO:
                is_fraud = True
                status = "declined" if random.random() < 0.3 else "under_review"
                # Fraud characteristics: extremely large amount or high-risk MCC (Gambling index)
                if random.random() < 0.5:
                    amount = round(random.uniform(12000.0, 48000.0), 2)
                else: # swiped at gambling merchant code
                    merchant_id = merchant_ids_arr[5] # index 5 is gambling
                    amount = round(random.uniform(5000.0, 9500.0), 2)

            chunk_records.append((
                tx_id, acc_id, beneficiary_id, merchant_id, branch_id, device_id,
                amount, "USD", tx_type, status, ref_num, initiated_at, completed_at
            ))
            
            # Keep sample of IDs to construct governance records later
            if tx_count % 90 == 0:
                sampled_tx_ids.append((tx_id, is_fraud, amount, device_id))
            if is_fraud:
                fraud_tx_ids.append(tx_id)
                
            tx_count += 1
            
        await bulk_load_table(conn, "transactions", tx_columns, chunk_records)

    # --- 9. Inject AML Structuring and Circular Transfer Cycles ---
    logger.info("Injecting graph-structured AML patterns...")
    
    # 9.1 Structuring (Smurfing): Large amounts ($49,000) split into $4,900 steps
    structuring_tx = []
    for i in range(cfg.NUM_AML_STRUCTURING):
        source_aid = random.choice(account_ids_arr)
        target_bid = random.choice(beneficiary_ids_arr)
        dev_id = random.choice(device_ids_arr)
        
        # 10 transactions of $4,900 split over 2 days
        smurf_time = cfg.START_DATE + timedelta(days=random.randint(10, 80))
        for step in range(10):
            tx_id = uuid.uuid4()
            ref_num = f"STR-{100000*i + step}"
            smurf_time += timedelta(minutes=random.randint(10, 180))
            structuring_tx.append((
                tx_id, source_aid, target_bid, None, None, dev_id,
                4900.00, "USD", "transfer", "approved", ref_num, smurf_time, smurf_time + timedelta(seconds=10)
            ))
    await bulk_load_table(conn, "transactions", tx_columns, structuring_tx)

    # 9.2 Layering Cycles: Account A -> Account B -> Account C -> Account A
    cycles_tx = []
    for i in range(cfg.NUM_AML_CIRCLES):
        acc_a = random.choice(account_ids_arr)
        acc_b = random.choice(account_ids_arr)
        acc_c = random.choice(account_ids_arr)
        
        cycle_time = cfg.START_DATE + timedelta(days=random.randint(10, 80))
        
        # A -> B
        tx1_id = uuid.uuid4()
        cycles_tx.append((
            tx1_id, acc_a, None, None, None, None, 15000.00, "USD", "transfer", "approved", f"CYCA-{10000*i}",
            cycle_time, cycle_time + timedelta(seconds=5)
        ))
        
        # B -> C
        tx2_id = uuid.uuid4()
        cycles_tx.append((
            tx2_id, acc_b, None, None, None, None, 14950.00, "USD", "transfer", "approved", f"CYCB-{10000*i}",
            cycle_time + timedelta(hours=2), cycle_time + timedelta(hours=2, seconds=5)
        ))
        
        # C -> A
        tx3_id = uuid.uuid4()
        cycles_tx.append((
            tx3_id, acc_c, None, None, None, None, 14900.00, "USD", "transfer", "approved", f"CYCC-{10000*i}",
            cycle_time + timedelta(hours=4), cycle_time + timedelta(hours=4, seconds=5)
        ))
    await bulk_load_table(conn, "transactions", tx_columns, cycles_tx)

    # --- 10. Generate Governance Data (Predictions, Scores, Checks, Explanations, Reviews) ---
    logger.info("Generating pipeline decision, policy, and explainability audits...")
    
    predictions = []
    trust_scores = []
    policy_checks = []
    explanations = []
    votes = []
    reviews = []
    alerts = []
    incidents = []

    fraud_agent_ver_id = agent_version_map["fraud-agent"]
    
    # Process sampled transactions to generate aligned evaluation items
    for idx, (tx_id, is_fraud, amount, dev_id) in enumerate(sampled_tx_ids[:10000]):
        pred_id = uuid.uuid4()
        
        # Prediction
        conf = random.uniform(0.92, 0.99) if is_fraud else random.uniform(0.01, 0.05)
        pred_out = {"is_fraud": is_fraud, "risk_level": "high" if is_fraud else "low"}
        predictions.append((
            pred_id, tx_id, fraud_agent_ver_id, json.dumps(pred_out), conf, random.uniform(15.2, 45.8), datetime.utcnow()
        ))
        
        # Explanation
        shap = {"amount": 0.85 if is_fraud else 0.05, "device_ip": 0.70 if is_fraud else 0.02}
        vector = [0.12] * 384 # mock pgvector float array
        explanations.append((
            uuid.uuid4(), pred_id, f"Evaluation verdict is {'high' if is_fraud else 'low'} risk due to parameters.",
            json.dumps(shap), vector, datetime.utcnow()
        ))
        
        # Trust Score
        score = random.randint(20, 48) if is_fraud else random.randint(86, 98)
        weights = {"model": 0.35, "compliance": 0.20, "device": 0.25, "drift": 0.20}
        reasons = {"flags": ["anomalous_large_amount"] if is_fraud else []}
        trust_scores.append((
            uuid.uuid4(), tx_id, score, json.dumps(weights), json.dumps(reasons), datetime.utcnow()
        ))
        
        # Policy Check
        pol_status = "fail" if is_fraud else "pass"
        policy_checks.append((
            uuid.uuid4(), tx_id, "RULE-102", pol_status, json.dumps({"limit_checked": 5000.00}), datetime.utcnow()
        ))
        
        # Consensus Vote
        verdict = "decline" if is_fraud else "approve"
        vote_counts = {"fraud_agent": verdict, "behavior_agent": verdict, "device_agent": "approve"}
        votes.append((
            uuid.uuid4(), tx_id, verdict, json.dumps(vote_counts), 0.66 if is_fraud else 1.0, datetime.utcnow()
        ))

        # Human Review and Incident triggers
        if is_fraud or score < 75:
            reviewer = random.choice(employee_ids)
            rev_status = "declined" if is_fraud else "approved"
            rev_id = uuid.uuid4()
            reviews.append((
                rev_id, tx_id, reviewer, rev_status, f"Audited anomaly check: {rev_status}", datetime.utcnow(), datetime.utcnow()
            ))
            
            # Security Alert
            alert_id = uuid.uuid4()
            severity = "critical" if amount > 25000 else "high"
            alerts.append((
                alert_id, tx_id, severity, f"Security limit violation: {amount} USD", False, datetime.utcnow()
            ))
            
            # Incident
            inc_id = uuid.uuid4()
            inc_status = "open" if idx % 10 == 0 else "resolved"
            incidents.append((
                inc_id, alert_id, f"Investigation for transaction {tx_id}", inc_status, severity, datetime.utcnow(), datetime.utcnow() if inc_status == "resolved" else None
            ))

    await bulk_load_table(conn, "predictions", ["id", "transaction_id", "model_version_id", "prediction_output", "confidence_score", "latency_ms", "created_at"], predictions)
    await bulk_load_table(conn, "explanations", ["id", "prediction_id", "explanation_text", "feature_attributions", "explanation_vector", "created_at"], explanations)
    await bulk_load_table(conn, "trust_scores", ["id", "transaction_id", "score", "weights_configuration", "reasons", "created_at"], trust_scores)
    await bulk_load_table(conn, "policy_checks", ["id", "transaction_id", "rule_id", "status", "details", "executed_at"], policy_checks)
    await bulk_load_table(conn, "consensus_votes", ["id", "transaction_id", "decision_verdict", "vote_details", "consensus_score", "created_at"], votes)
    await bulk_load_table(conn, "human_reviews", ["id", "transaction_id", "reviewer_id", "status", "comments", "assigned_at", "reviewed_at"], reviews)
    await bulk_load_table(conn, "alerts", ["id", "transaction_id", "severity", "message", "is_resolved", "created_at"], alerts)
    await bulk_load_table(conn, "incidents", ["id", "alert_id", "description", "status", "severity", "created_at", "resolved_at"], incidents)

    # --- 11. Cryptographic Audit Logs ---
    logger.info("Generating cryptographic ledger audit logs...")
    audit_logs = []
    prev_hash = "0" * 64
    for i in range(10000):
        log_id = uuid.uuid4()
        actor = random.choice(employee_ids)
        atype = random.choice(["login_success", "override_limit", "user_create", "policy_update"])
        desc = f"Audit log record entry number {i}"
        metadata_map = {"detail": f"Log record validation detail {i}"}
        
        meta_str = json.dumps(metadata_map, sort_keys=True)
        payload = f"{actor}|{atype}|{desc}||{meta_str}|{prev_hash}"
        prev_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        audit_logs.append((
            log_id, actor, atype, desc, None, json.dumps(metadata_map), prev_hash, datetime.utcnow()
        ))
    await bulk_load_table(conn, "audit_logs", ["id", "actor_id", "action_type", "description", "resource_id", "metadata", "ledger_hash", "created_at"], audit_logs)

    # --- 12. Chaos Tests & Compliance Reports ---
    logger.info("Generating operational chaos and compliance logs...")
    chaos_agent = agents[0][0] # fraud agent
    chaos = [
        (uuid.uuid4(), "geo-drift", chaos_agent, json.dumps({"param": "drift"}), "completed", datetime.utcnow() - timedelta(hours=4), datetime.utcnow() - timedelta(hours=3)),
        (uuid.uuid4(), "network-latency-simulation", chaos_agent, json.dumps({"delay": 200}), "completed", datetime.utcnow() - timedelta(hours=2), datetime.utcnow() - timedelta(hours=1))
    ]
    await bulk_load_table(conn, "chaos_tests", ["id", "scenario_id", "target_agent_id", "parameters", "status", "started_at", "completed_at"], chaos)

    reports = []
    for i in range(5):
        rid = uuid.uuid4()
        actor = random.choice(employee_ids)
        reports.append((
            rid, actor, "SOC2" if i % 2 == 0 else "GDPR", f"/vault/reports/report_{i}.pdf", json.dumps({"scope": "AegisAI security compliance verification"}), datetime.utcnow()
        ))
    await bulk_load_table(conn, "compliance_reports", ["id", "generated_by_id", "report_type", "file_path", "metadata", "created_at"], reports)

    await conn.close()
    logger.info("=================================================================")
    logger.info("Simulation successfully completed. 1,000,000+ rows loaded.")
    logger.info("=================================================================")

if __name__ == "__main__":
    asyncio.run(generate_simulation())
