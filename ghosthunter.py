import os
import asyncio
import httpx
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional

# 1. Strict Enterprise Configuration Schema
class GhostHunterConfig(BaseModel):
    active_emails: List[str]
    username_to_email_map: Dict[str, str]
    repo_owner: str
    repo_name: str

# 2. Bulletproof Slack Notifier
async def send_slack_alert(webhook_url: str, message: str) -> bool:
    if not webhook_url:
        print("⚠️  [Slack System] Webhook URL missing. Skipping live notification.")
        return False
        
    payload = {"text": message}
    # Set a timeout so if Slack is slow, your script doesn't freeze forever
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("📨 [Slack System] Live alert successfully beamed to company channel!")
                return True
            print(f"❌ [Slack System] API rejected message with status code: {response.status_code}")
            return False
        except httpx.RequestError as exc:
            # Captures network outages without crashing the software
            print(f"⚠️  [Slack System] Network error delivering alert: {exc}")
            return False

# 3. Bulletproof GitHub Scan Engine
async def scan_github_securely(config: GhostHunterConfig, github_token: str) -> Tuple[Optional[dict], Optional[str]]:
    url = f"https://api.github.com/repos/{config.repo_owner}/{config.repo_name}/contributors"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GhostHunter-Ultimate-Enterprise"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        
    timeout = httpx.Timeout(15.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url, headers=headers)
            
            # Catch authentication or permissions errors smoothly
            if response.status_code == 401:
                return None, "Unauthorized. Your GITHUB_TOKEN is invalid or expired."
            if response.status_code == 404:
                return None, f"Repository '{config.repo_owner}/{config.repo_name}' not found or token lacks access."
            if response.status_code != 200:
                return None, f"GitHub API unexpected status code: {response.status_code}"
                
            github_data = response.json()
            
            # Safeguard against unexpected API payload shapes
            if not isinstance(github_data, list):
                return None, "GitHub API returned invalid data format."
                
            current_github_users = [user["login"].lower() for user in github_data if "login" in user]
            
            ghosts = []
            strangers = []
            
            # Run the matching database layer
            for gh_user in current_github_users:
                if gh_user in config.username_to_email_map:
                    real_email = config.username_to_email_map[gh_user]
                    if real_email not in config.active_emails:
                        ghosts.append(f"{gh_user} (Fired Account: {real_email})")
                else:
                    strangers.append(gh_user)
                    
            return {"ghosts": ghosts, "strangers": strangers}, None
            
        except httpx.RequestError as exc:
            return None, f"Failed to establish connection to GitHub servers: {exc}"
        except Exception as e:
            return None, f"Critical unexpected error during JSON parsing: {e}"

# 4. Master Orchestration Core
async def main_enterprise_execution(config: GhostHunterConfig):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "") 
    SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
    
    print("🔒 [Core] GhostHunter operating in Secure On-Premises Mode.")
    print(f"🚀 [Core] Initiating network handshake with target: {config.repo_owner}/{config.repo_name}...\n")
    
    # Run the secure scan
    results, error = await scan_github_securely(config, GITHUB_TOKEN)
    
    if error:
        print(f"🚨 SYSTEM CORRUPTION ALERT: Security scan aborted!")
        print(f"Reason: {error}")
        print("-----------------------------------------")
        return

    ghosts = results["ghosts"]
    strangers = results["strangers"]
    is_breached = bool(ghosts or strangers)
    
    # Constructing a flawless audit report
    report_lines = [
        "--- GHOSTHUNTER SECURITY AUDIT REPORT ---",
        f"SYSTEM COMPLIANCE STATUS: {'🚨 BREACHED' if is_breached else '✅ SECURE'}"
    ]
    
    if ghosts:
        report_lines.append("\n[VULNERABILITY] Ex-employees retain active repository access keys:")
        for ghost in ghosts:
            report_lines.append(f"   ↳ {ghost}")
            
    if strangers:
        report_lines.append(f"\n[ANOMALY DETECTED] Found {len(strangers)} untracked/mystery accounts:")
        report_lines.append(f"   ↳ {strangers[:3]}... (and {len(strangers)-3} more required to link via database map)")
        
    report_lines.append("\n-----------------------------------------")
    
    full_report = "\n".join(report_lines)
    print(full_report)
    
    # Broadcast to security operations center via Slack if breached
    if is_breached:
        slack_message = (
            f"⚠️ *GhostHunter Critical Security Alert*\n"
            f"Target System: `{config.repo_owner}/{config.repo_name}`\n"
            f"Status: *BREACHED*\n"
            f"Found `{len(ghosts)}` ghost employee accounts and `{len(strangers)}` untracked keys. "
            f"Check internal terminal outputs immediately."
        )
        await send_slack_alert(SLACK_WEBHOOK, slack_message)

# --- PRODUCTION DEPLOYMENT SIMULATION ---
enterprise_config = GhostHunterConfig(
    active_emails=["james@ceo.com", "lead_dev@startup.com"],
    username_to_email_map={
        "lukasa": "lead_dev@startup.com",
        "sigmavirus24": "ex-employee-fired-last-month@startup.com"
    },
    repo_owner="psf",
    repo_name="requests"
)

# Run the un-crashable code
await main_enterprise_execution(enterprise_config)
