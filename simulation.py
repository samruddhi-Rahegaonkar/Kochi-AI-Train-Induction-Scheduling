import sqlite3
import pandas as pd
import datetime
from database_setup import fetch_all

def run_simulation(params):
    """
    Run the what-if simulation for train induction.
    params: dict with scenario variables
    Returns: dict with metrics and selected trains
    """
    # Fetch data
    trains = fetch_all("trains")
    fitness = fetch_all("fitness_certificates")
    jobs = fetch_all("job_cards")
    cleaning = fetch_all("cleaning_slots")
    branding = fetch_all("branding_priorities")

    # Compute base statuses
    train_statuses = []
    for train in trains:
        train_id = train['id']
        issues = []

        # Fitness check
        fit = [f for f in fitness if f['train_id'] == train_id]
        if not fit or any(f['certificate_status'] != 'Valid' or datetime.date.today() > datetime.datetime.strptime(f['valid_till'], '%Y-%m-%d').date() for f in fit):
            issues.append("Invalid/Expired Fitness")

        # Job check
        open_jobs = [j for j in jobs if j['train_id'] == train_id and j['status'] != 'Closed']
        if open_jobs:
            issues.append("Open Job Cards")

        # Cleaning check
        pending_clean = [c for c in cleaning if c['train_id'] == train_id and c['status'] != 'Done']
        if pending_clean:
            issues.append("Pending Cleaning")

        status = "Passed Checks" if not issues else "Needs Maintenance"
        train_statuses.append({
            'id': train_id,
            'train_number': train['train_number'],
            'status': status,
            'issues': issues,
            'issue_count': len(issues)
        })

    # Apply overrides
    for ts in train_statuses:
        if params.get('allow_risky_trains', False) and ts['issue_count'] <= params.get('max_issues_allowed', 1):
            ts['status'] = "Passed Checks"  # Override to allow

    # Select induction candidates
    # Prioritize passed checks, then by branding priority if advertiser focus
    candidates = [ts for ts in train_statuses if ts['status'] == "Passed Checks"]
    if params.get('prioritize_advertiser', False):
        # Add branding info
        for ts in candidates:
            brand = next((b for b in branding if b['train_id'] == ts['id']), None)
            ts['priority'] = brand['priority_level'] if brand else 'Low'
            ts['exposure'] = brand['exposure_hours'] if brand else 0
        # Sort by priority (High > Medium > Low)
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        candidates.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)

    # Limit to min_induction_count
    selected = candidates[:params.get('min_induction_count', len(candidates))]

    # Compute metrics
    total_selected = len(selected)
    punctuality = (total_selected / len(trains)) * 100 if trains else 0  # % ready trains inducted

    # Cost: base per train + penalty per issue overridden
    base_cost_per_train = 1000  # Assume fixed cost
    cost = total_selected * base_cost_per_train
    overridden = [ts for ts in selected if ts['issue_count'] > 0]
    cost += len(overridden) * params.get('cost_penalty_per_issue', 500)

    # Safety: average issues per selected train
    safety_score = sum(ts['issue_count'] for ts in selected) / total_selected if total_selected > 0 else 0

    # Advertiser: total exposure hours
    advertiser_exposure = sum(ts.get('exposure', 0) for ts in selected)

    return {
        'selected_trains': selected,
        'metrics': {
            'punctuality': round(punctuality, 2),
            'cost': cost,
            'safety_score': round(safety_score, 2),
            'advertiser_exposure': round(advertiser_exposure, 2)
        }
    }
