
from clients.mantis_operations import MantisOperations
from clients.google_sheets_operations import GoogleSheetsOperations
from config.config_manager import ConfigurationManager
from loggers.logging_config import LoggerSetup
from dateutil import parser

class RegressionProgressUpdater:
    def __init__(self):
        self.logger = LoggerSetup.setup_logger("regression_progress", "logs/regression_progress")
        self.config = ConfigurationManager()
        self.mantis_ops = MantisOperations()
        self.sheet_ops = GoogleSheetsOperations(credentials_file=self.config.get("GS_CREDENTIAL_FILE"))
        
        # Sheet details from config.json
        self.spreadsheet_key = self.config.get("REGRESSION_SHEET_KEY")
        self.sheet_name = self.config.get("MANTIS_TICKETS_NEXUS_E6")
    
    def update_progress(self):
        self.logger.info("Starting Regression Progress Update Process...")

        filter_id = self.config.get("REGRESSION_FILTER_ID")
        if not filter_id:
            self.logger.error("Filter ID not found in config.")
            return
        
        self.logger.info(f"Fetching Mantis tickets using Filter ID: {filter_id}")
        issues = self.mantis_ops.get_tickets_from_filter(filter_id)

        if not issues:
            self.logger.warning("No issues found with the given filter.")
            return
        
        self.logger.info(f"Total issues fetched: {len(issues)}")

        processed_rows = []
        td_count = 0
        
        # Process each issue
        for issue in issues:
            faucet = self.mantis_ops.get_faucet(issue)
            record_type = self.mantis_ops.get_record_type(issue)

            # Skip Technical Debt issues unless Code Move
            if faucet == "Technical Debt." and record_type != "Code Move":
                td_count += 1
                continue
            
            fixed_date, fixed_by = self.get_most_recent_status_change_date_and_user(issue)

            row_data = [
                f'=HYPERLINK("{self.mantis_ops.get_ticket_url(issue["id"])}", "{issue["id"]}")',
                issue.get('category', {}).get('name', ''),
                issue.get('project', {}).get('name', ''),
                record_type,
                issue.get('summary', ''),
                issue.get('handler', {}).get('real_name', ''),
                self.mantis_ops.get_qa_owner(issue),
                issue.get('resolution', {}).get('label', ''),
                issue.get('status', {}).get('label', ''),
                issue.get('priority', {}).get('label', ''),
                self.format_date(issue.get('created_at')),
                fixed_date,
                self.has_source_changeset(issue),
                fixed_by,
                self.get_most_recent_root_cause(issue),
                self.get_tags(issue),
                faucet,
                self.mantis_ops.get_efforts_dev(issue)
            ]
            
            processed_rows.append(row_data)

        self.logger.info(f"TD Count (Skipped Issues): {td_count}")
        self.logger.info(f"Processed Issues: {len(processed_rows)}")

        # Update Google Sheet
        try:
            self.logger.info(f"Updating Google Sheet: {self.spreadsheet_key}, Sheet Name: {self.sheet_name}")

            sheet = self.sheet_ops.client.open_by_key(self.spreadsheet_key).worksheet(self.sheet_name)
            
            # Clear old data (A3:R2000)
            sheet.batch_clear(["A3:R2000"])
            
            # Prepare and insert rows starting at row 3
            cell_range = f"A3:R{3 + len(processed_rows) - 1}"
            if processed_rows:
                # sheet.update(cell_range, processed_rows)
                sheet.update(cell_range, processed_rows, value_input_option='USER_ENTERED')

            # Update TD count in G1
            sheet.update_acell("G1", td_count)

            self.logger.info("Regression Progress Sheet updated successfully.")
        
        except Exception as e:
            self.logger.error(f"Failed to update Google Sheet: {e}")

    def format_date(self, date_string):
        if not date_string:
            return ""
        try:
            dt = parser.isoparse(date_string)
            return dt.strftime("%m/%d/%Y")  # Or whatever output format you need
        except Exception as e:
            self.logger.error(f"Date parsing error: {e}")
            return ""

    def get_most_recent_status_change_date_and_user(self, issue):
        try:
            resolution_label = issue.get('resolution', {}).get('label', '')
            
            if resolution_label not in [
                'Fixed',
                'For QA',
                'For Submitter',
                'Deployable on Hold',
                'For Product Management'
            ]:
                return "", ""

            # Reverse iterate over history to get the most recent entry first
            for history in reversed(issue.get('history', [])):
                field = history.get('field', {})
                
                if field.get('label') == 'Current Status':
                    old_value_label = history.get('old_value', {}).get('label', '')
                    
                    if old_value_label in [
                        'New',
                        'Partially Fixed',
                        'Not Fixed',
                        'In Progress',
                        'Investigation in Progress'
                    ]:
                        fixed_date = self.format_date(history.get('created_at'))
                        fixed_by = history.get('user', {}).get('real_name', '')
                        return fixed_date, fixed_by

            # No matching history found
            return "", ""

        except Exception as e:
            self.logger.error(f"Error extracting most recent status change date/user: {e}")
            return "", ""


    def has_source_changeset(self, issue):
        try:
            for history in issue.get('history', []):
                field = history.get('field', {})
                if field.get('label') == 'Source_changeset_attached':
                    return "Yes"
        except Exception as e:
            self.logger.error(f"Error checking source changeset: {e}")
        return ""

    def get_most_recent_root_cause(self, issue):
        try:
            history_entries = [
                entry for entry in issue.get('history', [])
                if entry.get('field', {}).get('name') == "Root Cause"
            ]

            if not history_entries:
                return ""

            # Sort by created_at descending
            sorted_entries = sorted(
                history_entries,
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )

            # Return the most recent 'new_value'
            return sorted_entries[0].get('new_value', '')
        
        except Exception as e:
            self.logger.error(f"Error fetching most recent root cause: {e}")
            return ""


    def get_tags(self, issue):
        try:
            tags = issue.get('tags', [])
            if not tags:
                return ""
            
            return ", ".join(tag.get('name', '') for tag in tags)
        
        except Exception as e:
            self.logger.error(f"Error fetching tags: {e}")
            return ""
