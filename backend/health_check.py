#!/usr/bin/env python3
"""
Health Check Script for Hotel Management System Backend
Verifies all system components are operational
"""

import os
import sys
from datetime import datetime
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class HealthCheck:
    def __init__(self):
        self.checks = {
            "Environment": False,
            "Database Connection": False,
            "Database Tables": False,
            "Initial Data": False,
            "API Server": False,
            "Authentication": False,
        }
        self.details = {}
        self.api_url = "http://localhost:8001"
        self.errors = []

    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
        print(f"{BLUE}{BOLD}{text:^70}{RESET}")
        print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")

    def print_check(self, name, status, message=""):
        """Print check result"""
        icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
        print(f"  {icon} {name:<30} {status_text:<10}", end="")
        if message:
            print(f"  {YELLOW}{message}{RESET}")
        else:
            print()

    def check_environment(self):
        """Check environment variables"""
        print(f"\n{BOLD}1. Environment Configuration{RESET}")
        required_vars = ["DATABASE_URL", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        missing = []

        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)

        if not missing:
            self.checks["Environment"] = True
            self.print_check("Environment Variables", True, "All required variables present")
            db_url = os.getenv("DATABASE_URL")
            masked_url = db_url[:30] + "..." if db_url else "N/A"
            self.print_check("DATABASE_URL", True, masked_url)
        else:
            self.checks["Environment"] = False
            self.print_check("Environment Variables", False, f"Missing: {', '.join(missing)}")
            self.errors.append(f"Missing environment variables: {', '.join(missing)}")

    def check_database_connection(self):
        """Check database connection"""
        print(f"\n{BOLD}2. Database Connection{RESET}")
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                self.print_check("Database Connection", False, "DATABASE_URL not set")
                return

            engine = create_engine(database_url, echo=False)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.close()

            self.checks["Database Connection"] = True
            self.print_check("Database Connection", True, "PostgreSQL (Supabase)")

            # Get database info
            with engine.connect() as conn:
                version_result = conn.execute(text("SELECT version()"))
                version = version_result.scalar()
                if version:
                    version_short = version.split(",")[0]
                    self.print_check("Database Version", True, version_short[:50])

        except Exception as e:
            self.checks["Database Connection"] = False
            self.print_check("Database Connection", False, str(e)[:40])
            self.errors.append(f"Database connection failed: {str(e)}")

    def check_database_tables(self):
        """Check if all tables exist"""
        print(f"\n{BOLD}3. Database Schema{RESET}")
        try:
            database_url = os.getenv("DATABASE_URL")
            engine = create_engine(database_url, echo=False)

            expected_tables = [
                "users", "room_types", "rooms", "room_images", "room_type_images",
                "guests", "reservations", "payments", "payment_attachments",
                "settings", "discounts", "booking_channels"
            ]

            with engine.connect() as conn:
                # Get actual tables
                result = conn.execute(text("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                """))
                actual_tables = [row[0] for row in result]

            found = [t for t in expected_tables if t in actual_tables]
            missing = [t for t in expected_tables if t not in actual_tables]

            if not missing:
                self.checks["Database Tables"] = True
                self.print_check("All Required Tables", True, f"{len(found)}/12 present")
            else:
                self.checks["Database Tables"] = False
                self.print_check("All Required Tables", False, f"Missing: {', '.join(missing)}")
                self.errors.append(f"Missing tables: {', '.join(missing)}")

            # Show table count
            self.print_check("Total Tables Found", True, f"{len(found)} tables")

        except Exception as e:
            self.checks["Database Tables"] = False
            self.print_check("Database Tables", False, str(e)[:40])
            self.errors.append(f"Table check failed: {str(e)}")

    def check_initial_data(self):
        """Check if initial data is seeded"""
        print(f"\n{BOLD}4. Initial Data{RESET}")
        try:
            database_url = os.getenv("DATABASE_URL")
            engine = create_engine(database_url, echo=False)

            data_checks = {
                "room_types": ("Room Types", 4),
                "booking_channels": ("Booking Channels", 5),
                "settings": ("Settings", 8),
                "users": ("Users", 1),
            }

            all_good = True
            with engine.connect() as conn:
                for table, (label, expected) in data_checks.items():
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()

                    if count >= expected:
                        self.print_check(label, True, f"{count} records")
                    else:
                        self.print_check(label, False, f"{count}/{expected} records")
                        all_good = False

            if all_good:
                self.checks["Initial Data"] = True
            else:
                self.checks["Initial Data"] = False
                self.errors.append("Some initial data missing or incomplete")

        except Exception as e:
            self.checks["Initial Data"] = False
            self.print_check("Initial Data Check", False, str(e)[:40])
            self.errors.append(f"Data check failed: {str(e)}")

    def check_api_server(self):
        """Check if API server is running"""
        print(f"\n{BOLD}5. API Server{RESET}")
        try:
            response = requests.get(f"{self.api_url}/api", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.checks["API Server"] = True
                self.print_check("API Server", True, f"Running on port 8001")
                self.print_check("API Version", True, data.get("version", "N/A"))
                self.print_check("API Status", True, data.get("status", "N/A"))
            else:
                self.checks["API Server"] = False
                self.print_check("API Server", False, f"HTTP {response.status_code}")
                self.errors.append(f"API returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.checks["API Server"] = False
            self.print_check("API Server", False, "Not running (connection refused)")
            self.errors.append("API server not running on http://localhost:8001")
        except Exception as e:
            self.checks["API Server"] = False
            self.print_check("API Server", False, str(e)[:40])
            self.errors.append(f"API check failed: {str(e)}")

    def check_authentication(self):
        """Check if authentication works"""
        print(f"\n{BOLD}6. Authentication{RESET}")
        try:
            # Try login
            login_response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
                timeout=5
            )

            if login_response.status_code == 200:
                data = login_response.json()
                token = data.get("access_token")

                if token:
                    self.print_check("Admin Login", True, "Token generated")

                    # Try using token
                    me_response = requests.get(
                        f"{self.api_url}/api/auth/me",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5
                    )

                    if me_response.status_code == 200:
                        user_data = me_response.json().get("user", {})
                        self.checks["Authentication"] = True
                        self.print_check("Token Validation", True, f"User: {user_data.get('username')}")
                        self.print_check("User Role", True, user_data.get('role', 'N/A'))
                    else:
                        self.checks["Authentication"] = False
                        self.print_check("Token Validation", False, f"HTTP {me_response.status_code}")
                        self.errors.append(f"Token validation failed: HTTP {me_response.status_code}")
                else:
                    self.checks["Authentication"] = False
                    self.print_check("Admin Login", False, "No token returned")
                    self.errors.append("Login failed: no token returned")
            else:
                self.checks["Authentication"] = False
                self.print_check("Admin Login", False, f"HTTP {login_response.status_code}")
                self.errors.append(f"Login failed: HTTP {login_response.status_code}")

        except requests.exceptions.ConnectionError:
            self.checks["Authentication"] = False
            self.print_check("Authentication", False, "API not running")
            self.errors.append("Cannot test authentication: API not running")
        except Exception as e:
            self.checks["Authentication"] = False
            self.print_check("Authentication", False, str(e)[:40])
            self.errors.append(f"Authentication check failed: {str(e)}")

    def print_summary(self):
        """Print health check summary"""
        passed = sum(1 for v in self.checks.values() if v)
        total = len(self.checks)
        percentage = (passed / total) * 100

        print(f"\n{BOLD}{'=' * 70}{RESET}")
        print(f"{BOLD}SUMMARY{RESET}")
        print(f"{BOLD}{'=' * 70}{RESET}\n")

        for check, status in self.checks.items():
            icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
            status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
            print(f"  {icon} {check:<35} {status_text}")

        print(f"\n{BOLD}Overall Status: {passed}/{total} checks passed ({percentage:.0f}%){RESET}")

        if percentage == 100:
            print(f"{GREEN}{BOLD}✓ All systems operational!{RESET}\n")
            return 0
        elif percentage >= 80:
            print(f"{YELLOW}{BOLD}⚠ Most systems operational (some issues to address){RESET}\n")
            return 1
        else:
            print(f"{RED}{BOLD}✗ Critical issues detected{RESET}\n")
            return 2

    def print_errors(self):
        """Print detailed errors"""
        if self.errors:
            print(f"{BOLD}Issues Found:{RESET}\n")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {RED}{error}{RESET}")
            print()

    def run(self):
        """Run all health checks"""
        self.print_header("HOTEL MANAGEMENT SYSTEM - HEALTH CHECK")

        self.check_environment()
        self.check_database_connection()
        self.check_database_tables()
        self.check_initial_data()
        self.check_api_server()
        self.check_authentication()

        self.print_summary()
        self.print_errors()

        return self.print_summary()


if __name__ == "__main__":
    checker = HealthCheck()
    exit_code = checker.run()
    sys.exit(exit_code)
